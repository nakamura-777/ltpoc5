
import streamlit as st
import pandas as pd
import plotly.express as px
import chardet

st.set_page_config(page_title="キャッシュ生産性アプリ v16", layout="wide")
st.title("キャッシュ生産性アプリ v16")

# 製品マスターCSVのアップロード
product_master_file = st.file_uploader("製品マスターCSVをアップロード", type=["csv"], key="product_master")
if product_master_file:
    # 文字コード検出
    master_bytes = product_master_file.read()
    master_encoding = chardet.detect(master_bytes)['encoding']
    product_master_file.seek(0)
    try:
        product_master_df = pd.read_csv(product_master_file, encoding=master_encoding)
        st.session_state.product_master_df = product_master_df
        st.success("製品マスターを読み込みました")
    except Exception as e:
        st.error(f"製品マスターの読み込みエラー: {e}")

# 生産データCSVのアップロード
input_file = st.file_uploader("生産データCSVをアップロード", type=["csv"], key="input_data")
if input_file:
    # 文字コード検出
    input_bytes = input_file.read()
    input_encoding = chardet.detect(input_bytes)['encoding']
    input_file.seek(0)
    try:
        input_df = pd.read_csv(input_file, encoding=input_encoding)
        # 日付変換
        input_df["生産開始日"] = pd.to_datetime(input_df["生産開始日"], errors="coerce")
        input_df["出荷日"] = pd.to_datetime(input_df["出荷日"], errors="coerce")

        # スループットとLT計算
        input_df["スループット"] = input_df["売上"] - input_df["材料費"] - input_df["外注費"]
        input_df["LT"] = (input_df["出荷日"] - input_df["生産開始日"]).dt.days.clip(lower=1)
        input_df["TP/LT"] = input_df["スループット"] / input_df["LT"]

        # 集計
        summary = input_df.groupby("品名").agg(
            出荷数合計=("出荷数", "sum"),
            平均TP=("スループット", "mean"),
            平均TP_LT=("TP/LT", "mean"),
            件数=("品名", "count")
        ).reset_index()

        st.subheader("集計結果")
        st.dataframe(summary)

        # グラフ
        fig = px.scatter(
            input_df,
            x="TP/LT",
            y="スループット",
            color="品名",
            size="出荷数",
            hover_data=["生産開始日", "出荷日"]
        )
        st.plotly_chart(fig)

        # CSV出力
        csv = input_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("結果CSVをダウンロード", data=csv, file_name="cash_productivity_results.csv", mime="text/csv")
    except Exception as e:
        st.error(f"データ読み込み・処理エラー: {e}")
