import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="キャッシュ生産性アプリ（CSV対応）", layout="wide")
st.title("📊 キャッシュ生産性アプリ（CSV連携版）")

# --- 製品マスター初期化 ---
if "product_master" not in st.session_state:
    st.session_state.product_master = {}

st.sidebar.header("🛠 製品マスター登録")
with st.sidebar.form("master_form"):
    product_name = st.text_input("製品名（品名）")
    weight_unit_price = st.number_input("重量単価（円／mm³）", min_value=0.0, step=0.01, format="%.4f")
    submitted = st.form_submit_button("登録 / 上書き")

    if submitted and product_name:
        st.session_state.product_master[product_name.strip()] = weight_unit_price
        st.sidebar.success(f"{product_name} を単価 {weight_unit_price:.4f} で登録しました")

st.sidebar.markdown("### 📋 製品マスター一覧")
if st.session_state.product_master:
    st.sidebar.dataframe(pd.DataFrame.from_dict(
        st.session_state.product_master, orient="index", columns=["重量単価"]
    ))
else:
    st.sidebar.info("製品マスターがまだ登録されていません")

# 材料購入日の一括入力
purchase_date = st.date_input("📆 材料購入日（すべての行に適用）", value=datetime.today())

# CSVアップロード
uploaded_file = st.file_uploader("📂 CSVファイルをアップロード（SJIS・R列=品名、IJK列=寸法、AI列=出荷日）", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="shift-jis", engine="python")

        # 対象列の抽出
        df = df[["品名", "厚み(表示)", "幅　(表示)", "長さ(表示)", "出荷日"]].copy()
        df = df.dropna(subset=["品名", "厚み(表示)", "幅　(表示)", "長さ(表示)", "出荷日"])

        df["製品名"] = df["品名"].str.strip()
        df["厚み"] = pd.to_numeric(df["厚み(表示)"], errors="coerce")
        df["幅"] = pd.to_numeric(df["幅　(表示)"], errors="coerce")
        df["長さ"] = pd.to_numeric(df["長さ(表示)"], errors="coerce")
        df["体積"] = df["厚み"] * df["幅"] * df["長さ"]
        df["材料購入日"] = purchase_date
        df["出荷日"] = pd.to_datetime(df["出荷日"], errors="coerce")

        # リードタイム
        df["LT（日）"] = (df["出荷日"] - df["材料購入日"]).dt.days.clip(lower=1)

        # 材料費計算（製品マスターから）
        def compute_cost(row):
            unit = st.session_state.product_master.get(row["製品名"], 0)
            return row["体積"] * unit

        df["材料費"] = df.apply(compute_cost, axis=1)
        df["売上"] = 0
        df["外注費"] = 0
        df["TP"] = df["売上"] - df["材料費"] - df["外注費"]
        df["TP/LT"] = (df["TP"] / df["LT（日）"]).round(2)
        df["1個あたりTP"] = df["TP"]
        df["1個あたりTP/LT"] = df["TP/LT"]

        st.success("✅ CSVデータの処理が完了しました")
        st.dataframe(df[[
            "製品名", "体積", "材料費", "材料購入日", "出荷日", "LT（日）", "TP", "TP/LT"
        ]], use_container_width=True)

        # 平均情報
        st.markdown("### 📊 製品別平均サマリー")
        summary = df.groupby("製品名").agg({
            "TP": "mean",
            "TP/LT": "mean",
            "1個あたりTP": "mean",
            "1個あたりTP/LT": "mean"
        }).rename(columns={
            "TP": "平均TP", "TP/LT": "平均TP/LT",
            "1個あたりTP": "平均1個あたりTP",
            "1個あたりTP/LT": "平均1個あたりTP/LT"
        }).reset_index()
        st.dataframe(summary)

        # CSV出力
        csv_data = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 処理済みデータをCSVでダウンロード", data=csv_data, file_name="processed_tp_lt.csv")

        # グラフ表示
        st.subheader("📈 TP vs TP/LT バブルチャート")
        fig = px.scatter(
            df, x="TP/LT", y="TP", color="製品名", size="TP", hover_name="製品名",
            labels={"TP/LT": "キャッシュ生産性", "TP": "スループット（TP）"}
        )
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ 読み込みエラー: {e}")
