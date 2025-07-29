
import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

st.set_page_config(page_title="キャッシュ生産性アプリ", layout="wide")

st.title("キャッシュ生産性アプリ v16")

# 製品マスターのアップロード
st.sidebar.header("製品マスターアップロード")
product_master_file = st.sidebar.file_uploader("製品マスターCSVをアップロード", type=["csv"], key="product_master")
if product_master_file:
    product_master_df = pd.read_csv(product_master_file)
    st.session_state["product_master_df"] = product_master_df
    st.sidebar.success("製品マスターを読み込みました")

# 生産データのアップロード
st.sidebar.header("生産データアップロード")
uploaded_file = st.sidebar.file_uploader("生産出荷CSVをアップロード", type=["csv"], key="input_data")

# 手動入力フォーム
st.header("手動入力")
with st.form("manual_input"):
    product = st.selectbox("品名", options=st.session_state.get("product_master_df", pd.DataFrame()).get("品名", []) if "product_master_df" in st.session_state else [])
    sales_price = st.number_input("売上単価", min_value=0.0)
    material_cost = st.number_input("材料費", min_value=0.0)
    outsourcing_cost = st.number_input("外注費", min_value=0.0)
    shipment_qty = st.number_input("出荷数", min_value=0)
    start_date = st.date_input("生産開始日")
    ship_date = st.date_input("出荷日")
    submitted = st.form_submit_button("入力を確定")

# 生産データの読み込み
if uploaded_file:
    try:
        input_df = pd.read_csv(uploaded_file, encoding="utf-8")
    except:
        input_df = pd.read_csv(uploaded_file, encoding="shift_jis")

    input_df["スループット"] = input_df["売上単価"] - input_df["材料費"] - input_df["外注費"]
    input_df["生産開始日"] = pd.to_datetime(input_df["生産開始日"], errors="coerce")
    input_df["出荷日"] = pd.to_datetime(input_df["出荷日"], errors="coerce")
    input_df["LT"] = (input_df["出荷日"] - input_df["生産開始日"]).dt.days.clip(lower=1)
    input_df["TP/LT"] = input_df["スループット"] / input_df["LT"]
    input_df["出荷数"] = pd.to_numeric(input_df["出荷数"], errors="coerce")

    st.subheader("計算結果プレビュー")
    st.dataframe(input_df)

    # グラフ描画
    fig = px.scatter(input_df, x="TP/LT", y="スループット", size="出荷数", color="品名",
                     hover_data=["品名", "スループット", "TP/LT"])
    st.plotly_chart(fig, use_container_width=True)

    # 平均情報
    avg_tp = input_df["スループット"].mean()
    avg_tp_lt = input_df["TP/LT"].mean()
    product_count = input_df["品名"].nunique()
    st.markdown(f"**製品数:** {product_count}　**平均スループット:** {avg_tp:.2f}　**平均TP/LT:** {avg_tp_lt:.2f}")

    # 結果CSV出力
    csv = input_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("結果CSVをダウンロード", data=csv, file_name="計算結果.csv", mime="text/csv")
