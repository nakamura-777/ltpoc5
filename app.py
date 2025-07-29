
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="キャッシュ生産性アプリ", layout="wide")
st.title("キャッシュ生産性アプリ")

# CSVアップロード
uploaded_file = st.file_uploader("生産出荷データCSVをアップロード", type="csv")
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding="shift_jis")

    for col in ["生産開始日", "出荷日"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    df["材料費"] = pd.to_numeric(df["材料費"], errors="coerce").fillna(0)
    df["外注費"] = pd.to_numeric(df["外注費"], errors="coerce").fillna(0)
    df["売上"] = pd.to_numeric(df["売上"], errors="coerce").fillna(0)
    df["出荷数"] = pd.to_numeric(df["出荷数"], errors="coerce").fillna(0)

    df["スループット"] = df["売上"] - df["材料費"] - df["外注費"]
    df["リードタイム"] = (df["出荷日"] - df["生産開始日"]).dt.days.clip(lower=1)
    df["TP/LT"] = df["スループット"] / df["リードタイム"]
    df["1個あたりTP"] = df["スループット"] / df["出荷数"]
    df["1個あたりTP/LT"] = df["TP/LT"] / df["出荷数"]

    st.subheader("概要指標")
    st.markdown(f"- 製品数: {df.shape[0]}点")
    st.markdown(f"- 平均スループット: {df['スループット'].mean():,.0f}円")
    st.markdown(f"- 平均TP/LT: {df['TP/LT'].mean():,.2f}")

    st.subheader("TP/LT バブルチャート")
    fig = px.scatter(df, x="TP/LT", y="スループット", size="出荷数", color="品名", hover_data=df.columns)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("CSVダウンロード")
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("結果CSVをダウンロード", csv, "tp_lt_result.csv", "text/csv")

st.subheader("手動入力")
with st.form("manual_input"):
    col1, col2 = st.columns(2)
    with col1:
        品名 = st.text_input("品名")
        材料費 = st.number_input("材料費", min_value=0)
        外注費 = st.number_input("外注費", min_value=0)
        売上 = st.number_input("売上", min_value=0)
    with col2:
        出荷数 = st.number_input("出荷数", min_value=1, value=1)
        生産開始日 = st.date_input("生産開始日")
        出荷日 = st.date_input("出荷日")
    submitted = st.form_submit_button("入力確定")
    if submitted:
        st.success(f"{品名} のデータが入力されました。（※このセッション内でのみ反映）")
