import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="キャッシュ生産性アプリ", layout="wide")
st.title("キャッシュ生産性アプリ")

# 製品マスターの読み込み
if "product_master_df" not in st.session_state:
    st.session_state.product_master_df = pd.DataFrame(columns=["品名", "材料費", "外注費", "売上単価"])

# 製品マスターのアップロードと手動入力
st.sidebar.header("製品マスター管理")
uploaded_master = st.sidebar.file_uploader("製品マスターCSVをアップロード", type=["csv"])
if uploaded_master:
    st.session_state.product_master_df = pd.read_csv(uploaded_master)

with st.sidebar.form("manual_master"):
    st.subheader("製品マスターの手動追加")
    pname = st.text_input("品名")
    material_cost = st.number_input("材料費", min_value=0.0, step=10.0)
    outsource_cost = st.number_input("外注費", min_value=0.0, step=10.0)
    unit_price = st.number_input("売上単価", min_value=0.0, step=10.0)
    add_master = st.form_submit_button("追加")
    if add_master and pname:
        st.session_state.product_master_df = pd.concat([st.session_state.product_master_df,
            pd.DataFrame([{"品名": pname, "材料費": material_cost, "外注費": outsource_cost, "売上単価": unit_price}])],
            ignore_index=True)

st.sidebar.download_button("マスターをCSVでダウンロード", st.session_state.product_master_df.to_csv(index=False), "product_master.csv")

# 入力フォームとCSVアップロード
st.subheader("生産・出荷データ入力")
input_method = st.radio("データ入力方法を選択", ["手動入力", "CSVアップロード"])

if input_method == "CSVアップロード":
    uploaded_file = st.file_uploader("生産出荷データCSVをアップロード", type=["csv"])
    if uploaded_file:
        try:
            input_df = pd.read_csv(uploaded_file, encoding="utf-8")
            input_df["生産開始日"] = pd.to_datetime(input_df["生産開始日"], errors="coerce")
            input_df["出荷日"] = pd.to_datetime(input_df["出荷日"], errors="coerce")
        except Exception as e:
            st.error(f"読み込みエラー: {e}")
            input_df = pd.DataFrame()
    else:
        input_df = pd.DataFrame()
else:
    with st.form("manual_input"):
        col1, col2 = st.columns(2)
        with col1:
            selected_product = st.selectbox("品名", st.session_state.product_master_df["品名"].unique() if not st.session_state.product_master_df.empty else [])
            manual_start = st.date_input("生産開始日", datetime.today())
            manual_ship = st.date_input("出荷日", datetime.today())
            ship_qty = st.number_input("出荷数", min_value=1)
        with col2:
            if selected_product in st.session_state.product_master_df["品名"].values:
                row = st.session_state.product_master_df[st.session_state.product_master_df["品名"] == selected_product].iloc[0]
                mat_cost, out_cost, unit_price = row["材料費"], row["外注費"], row["売上単価"]
            else:
                mat_cost = st.number_input("材料費", min_value=0.0, step=10.0)
                out_cost = st.number_input("外注費", min_value=0.0, step=10.0)
                unit_price = st.number_input("売上単価", min_value=0.0, step=10.0)

        submitted = st.form_submit_button("データ追加")
        if submitted:
            input_df = pd.DataFrame([{
                "品名": selected_product, "生産開始日": manual_start, "出荷日": manual_ship,
                "出荷数": ship_qty, "材料費": mat_cost, "外注費": out_cost, "売上単価": unit_price
            }])
        else:
            input_df = pd.DataFrame()

# 処理と表示
if not input_df.empty:
    input_df["スループット"] = input_df["売上単価"] - input_df["材料費"] - input_df["外注費"]
    input_df["リードタイム"] = (input_df["出荷日"] - input_df["生産開始日"]).dt.days.clip(lower=1)
    input_df["TP/LT"] = input_df["スループット"] / input_df["リードタイム"]
    input_df["出荷数"] = pd.to_numeric(input_df["出荷数"], errors="coerce")
    avg_tp = input_df["スループット"].mean()
    avg_tpl = input_df["TP/LT"].mean()

    st.markdown(f"**製品数:** {len(input_df)}")
    st.markdown(f"**平均スループット:** {avg_tp:.2f} 円")
    st.markdown(f"**平均TP/LT:** {avg_tpl:.2f} 円/日")

    fig = px.scatter(input_df, x="TP/LT", y="スループット", color="品名",
                     size="出荷数", hover_data=["品名", "スループット", "TP/LT"])
    st.plotly_chart(fig, use_container_width=True)
    st.download_button("結果CSVをダウンロード", input_df.to_csv(index=False), "output_result.csv")
