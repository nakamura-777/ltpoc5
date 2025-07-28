
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

    # 出荷済数のカンマ除去
    df["出荷済数"] = pd.to_numeric(df["出荷済数"].astype(str).str.replace(",", ""), errors="coerce")

    # 出荷日（AI列）をdatetimeに変換
    df["出荷日"] = pd.to_datetime(df["出荷日"], errors="coerce")

    # 売上単価列を自動検出
    sales_candidates = [col for col in df.columns if "売上" in col or "単価" in col or col.startswith("U")]
    if sales_candidates:
        sales_col = sales_candidates[0]
        df["売上単価"] = pd.to_numeric(df[sales_col].astype(str).str.replace(",", ""), errors="coerce")
    else:
        st.error("⚠️『売上単価』に該当する列が見つかりませんでした。")
        st.stop()

    # 対象列抽出
    required_cols = ["品名", "材料費", "出荷済数", "出荷日", "売上単価"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"⚠️必要な列 '{col}' が見つかりません。CSVを確認してください。")
            st.stop()
    df = df[required_cols].dropna()

    st.write("読み込みデータ（上位10件）")
    st.dataframe(df.head(10))

    with st.form("入力フォーム"):
        st.markdown("### 📝 共通項目の入力")
        生産着手日 = st.date_input("生産着手日", value=datetime.today())
        売上単価手動入力 = st.checkbox("売上単価を手動入力で上書きする")
        売上単価 = st.number_input("製品1個あたり売上（円）", value=0) if 売上単価手動入力 else None
        外注費単価 = st.number_input("製品1個あたり外注費（円）", value=0)
        submitted = st.form_submit_button("スループットを計算")

    if submitted:
        df["生産着手日"] = pd.to_datetime(生産着手日)
        df["リードタイム（日）"] = (df["出荷日"] - df["生産着手日"]).dt.days.clip(lower=1)
        df["材料費_1個あたり"] = df["材料費"] / df["出荷済数"]

        if 売上単価手動入力:
            df["売上単価"] = 売上単価  # 手動入力で一括上書き

        df["TP_1個あたり"] = df["売上単価"] - df["材料費_1個あたり"] - 外注費単価
        df["TP_合計"] = df["TP_1個あたり"] * df["出荷済数"]
        df["TP/LT"] = df["TP_合計"] / df["リードタイム（日）"]

        # 統計情報
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
