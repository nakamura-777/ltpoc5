
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="キャッシュ生産性アプリ v15.1", layout="wide")
st.title("キャッシュ生産性アプリ v15.1")

# セッション初期化
if "product_master_df" not in st.session_state:
    st.session_state.product_master_df = pd.DataFrame(columns=["品名", "材料単価", "外注費", "売上単価"])

st.sidebar.header("① 製品マスター登録")
uploaded_master = st.sidebar.file_uploader("CSVアップロード", type="csv", key="master_upload")
if uploaded_master:
    df = pd.read_csv(uploaded_master)
    if "品名" in df.columns:
        st.session_state.product_master_df = df
        st.sidebar.success("マスターを読み込みました")
    else:
        st.sidebar.error("CSVに '品名' 列が必要です")

with st.sidebar.form("manual_master_entry"):
    st.markdown("#### 手動登録")
    name = st.text_input("品名")
    mat_cost = st.number_input("材料単価", step=1.0)
    out_cost = st.number_input("外注費", step=1.0)
    price = st.number_input("売上単価", step=1.0)
    submit = st.form_submit_button("登録")
    if submit and name:
        st.session_state.product_master_df.loc[len(st.session_state.product_master_df)] = [name, mat_cost, out_cost, price]
        st.sidebar.success(f"{name} を登録しました")

st.sidebar.header("② 生産データ入力")
uploaded_input = st.sidebar.file_uploader("出荷データCSV", type="csv", key="input_upload")
input_df = pd.DataFrame()

if uploaded_input:
    input_df = pd.read_csv(uploaded_input)
    try:
        input_df["生産開始日"] = pd.to_datetime(input_df["生産開始日"], errors="coerce")
        input_df["出荷日"] = pd.to_datetime(input_df["出荷日"], errors="coerce")
        input_df["出荷数量"] = pd.to_numeric(input_df["出荷数量"], errors="coerce")
    except Exception as e:
        st.error(f"日付か数値の変換でエラーがあります: {e}")

    merged_df = pd.merge(input_df, st.session_state.product_master_df, on="品名", how="left")
    merged_df["材料単価"] = pd.to_numeric(merged_df["材料単価"], errors="coerce").fillna(0)
    merged_df["外注費"] = pd.to_numeric(merged_df["外注費"], errors="coerce").fillna(0)
    merged_df["売上単価"] = pd.to_numeric(merged_df["売上単価"], errors="coerce").fillna(0)

    merged_df["スループット"] = (merged_df["売上単価"] - merged_df["材料単価"] - merged_df["外注費"]) * merged_df["出荷数量"]
    merged_df["LT(日)"] = (merged_df["出荷日"] - merged_df["生産開始日"]).dt.days.clip(lower=1)
    merged_df["TP/LT"] = merged_df["スループット"] / merged_df["LT(日)"]

    st.header("📊 結果一覧")
    st.dataframe(merged_df)

    st.download_button("📥 結果CSVをダウンロード", data=merged_df.to_csv(index=False), file_name="結果データ.csv")

    st.header("📈 バブルチャート")
    fig = px.scatter(
        merged_df,
        x="TP/LT",
        y="スループット",
        size="出荷数量",
        color="品名",
        hover_data=["品名", "出荷数量", "TP/LT", "スループット"],
        size_max=60,
        title="キャッシュ生産性バブルチャート"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📌 集計情報")
    col1, col2, col3 = st.columns(3)
    col1.metric("製品数", merged_df['品名'].nunique())
    col2.metric("平均 TP", f"{merged_df['スループット'].mean():,.0f}")
    col3.metric("平均 TP/LT", f"{merged_df['TP/LT'].mean():,.2f}")
else:
    st.info("サイドバーから出荷データCSVをアップロードしてください。")
