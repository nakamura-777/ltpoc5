
import streamlit as st
import pandas as pd
import plotly.express as px

st.title("キャッシュ生産性アプリ vFinal")

uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df["生産開始日"] = pd.to_datetime(df["生産開始日"], errors="coerce")
    df["出荷日"] = pd.to_datetime(df["出荷日"], errors="coerce")
    df["スループット"] = df["売上単価"] - df["材料費"] - df["外注費"]
    df["LT（日）"] = (df["出荷日"] - df["生産開始日"]).dt.days.clip(lower=1)
    df["TP/LT"] = df["スループット"] / df["LT（日）"]

    st.dataframe(df)

    fig = px.scatter(df, x="TP/LT", y="スループット", color="品名",
                     size="出荷数", hover_data=["品名", "スループット", "TP/LT"])
    st.plotly_chart(fig)

    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("CSVをダウンロード", csv, "結果.csv", "text/csv")
