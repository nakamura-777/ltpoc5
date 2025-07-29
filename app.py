
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="キャッシュ生産性アプリ", layout="wide")

st.title("キャッシュ生産性アプリ")

uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("アップロードされたデータ", df.head())

    if "売上" in df.columns and "材料費" in df.columns and "外注費" in df.columns and "生産開始日" in df.columns and "出荷日" in df.columns:
        df["売上"] = pd.to_numeric(df["売上"], errors="coerce")
        df["材料費"] = pd.to_numeric(df["材料費"], errors="coerce")
        df["外注費"] = pd.to_numeric(df["外注費"], errors="coerce")
        df["スループット"] = df["売上"] - df["材料費"] - df["外注費"]
        df["生産開始日"] = pd.to_datetime(df["生産開始日"], errors="coerce")
        df["出荷日"] = pd.to_datetime(df["出荷日"], errors="coerce")
        df["LT（日数）"] = (df["出荷日"] - df["生産開始日"]).dt.days.clip(lower=1)
        df["TP/LT"] = df["スループット"] / df["LT（日数）"]

        st.write("処理結果", df)

        fig = px.scatter(
            df,
            x="TP/LT",
            y="スループット",
            color="製品名" if "製品名" in df.columns else None,
            size="出荷数" if "出荷数" in df.columns else None,
            hover_data=["売上", "材料費", "外注費", "LT（日数）"],
            title="キャッシュ生産性バブルチャート"
        )
        st.plotly_chart(fig)
    else:
        st.error("必要な列が不足しています。'売上', '材料費', '外注費', '生産開始日', '出荷日' を含めてください。")
