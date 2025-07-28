
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="キャッシュ生産性アプリ", layout="wide")
st.title("📦 キャッシュ生産性アプリ")

uploaded_file = st.file_uploader("CSVファイルをアップロードしてください（製品マスター形式）", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="shift-jis")
    except:
        df = pd.read_csv(uploaded_file)

    # カンマを除去して出荷済数を数値変換
    df["出荷済数"] = pd.to_numeric(df["出荷済数"].astype(str).str.replace(",", ""), errors="coerce")

    # 出荷日（AI列）をdatetimeに変換
    df["出荷予定日"] = pd.to_datetime(df["出荷予定日"], errors="coerce")

    # 必須項目の抽出と初期化
    df = df[["品名", "材料費", "出荷済数", "出荷予定日"]].copy()
    df = df.dropna(subset=["品名", "材料費"])
    df["出荷済数"] = pd.to_numeric(df["出荷済数"], errors="coerce")

    st.write("読み込みデータ（上位10件）")
    st.dataframe(df.head(10))

    with st.form("入力フォーム"):
        st.markdown("### 📝 共通項目の入力")
        生産着手日 = st.date_input("生産着手日", value=datetime.today())
        売上単価 = st.number_input("製品1個あたり売上（円）", value=0)
        外注費単価 = st.number_input("製品1個あたり外注費（円）", value=0)
        submitted = st.form_submit_button("スループットを計算")

    if submitted:
        df = df.dropna(subset=["出荷済数"])
        df["生産着手日"] = pd.to_datetime(生産着手日)
        df["リードタイム（日）"] = (df["出荷予定日"] - df["生産着手日"]).dt.days.clip(lower=1)
        df["材料費_1個あたり"] = df["材料費"] / df["出荷済数"]
        df["TP_1個あたり"] = 売上単価 - df["材料費_1個あたり"] - 外注費単価
        df["TP_合計"] = df["TP_1個あたり"] * df["出荷済数"]
        df["TP/LT"] = df["TP_合計"] / df["リードタイム（日）"]

        # 平均表示
        st.markdown("### 📊 統計情報")
        col1, col2, col3 = st.columns(3)
        col1.metric("製品数", len(df))
        col2.metric("平均TP（円）", f"{df['TP_1個あたり'].mean():,.0f}")
        col3.metric("平均TP/LT", f"{df['TP/LT'].mean():,.0f}")

        # グラフ描画
        st.markdown("### 📈 TP/LTグラフ")
        fig = px.scatter(df, x="TP/LT", y="TP_合計", color="品名",
                         size="出荷済数", hover_data=["品名", "TP_1個あたり", "リードタイム（日）"])
        st.plotly_chart(fig, use_container_width=True)
