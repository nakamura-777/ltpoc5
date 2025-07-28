
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="キャッシュ生産性アプリ", layout="wide")

st.title("📊 キャッシュ生産性アプリ")

uploaded_file = st.file_uploader("製品情報CSVをアップロード", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # 前処理
    for col in ["売上金額", "材料費", "出荷数", "外注費用"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce").fillna(0)

    df["生産開始日"] = pd.to_datetime(df["生産開始日"], errors="coerce")
    df["出荷日"] = pd.to_datetime(df["出荷日"], errors="coerce")
    df["リードタイム"] = (df["出荷日"] - df["生産開始日"]).dt.days.clip(lower=1)

    df["スループット"] = (df["売上金額"] - df["材料費"] - df["外注費用"]) / df["出荷数"].replace(0, 1)
    df["TP/LT"] = df["スループット"] / df["リードタイム"].replace(0, 1)

    # 平均と合計の表示
    st.subheader("📈 指標サマリー")
    col1, col2, col3 = st.columns(3)
    col1.metric("製品数", len(df))
    col2.metric("平均スループット/個", f"{df['スループット'].mean():,.2f}")
    col3.metric("平均TP/LT", f"{df['TP/LT'].mean():,.2f}")

    # グラフ
    st.subheader("📊 TP/LTバブルチャート")
    fig = px.scatter(
        df,
        x="TP/LT",
        y="スループット",
        size="出荷数",
        color="品名",
        hover_data=["品名", "売上金額", "材料費", "外注費用", "リードタイム"],
        size_max=60,
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

    # CSV出力
    st.subheader("⬇ データのダウンロード")
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 結果CSVをダウンロード", csv, "キャッシュ生産性結果.csv", "text/csv")
