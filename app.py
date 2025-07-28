import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="キャッシュ生産性アプリ", layout="wide")
st.title("📊 キャッシュ生産性アプリ")

# --- 製品マスターの初期化 ---
if "product_master" not in st.session_state:
    st.session_state.product_master = {
        "製品A": {"単価売上": 1000, "材料費": 300, "外注費": 200},
        "製品B": {"単価売上": 2000, "材料費": 700, "外注費": 400}
    }

# --- 製品データの初期化 ---
if "product_data" not in st.session_state:
    st.session_state.product_data = []

# --- 製品マスター登録セクション ---
st.sidebar.header("🛠 製品マスター登録")
with st.sidebar.form("master_form"):
    new_name = st.text_input("製品名")
    new_price = st.number_input("単価売上", step=100, min_value=0)
    new_mat_cost = st.number_input("材料費", step=100, min_value=0)
    new_out_cost = st.number_input("外注費", step=100, min_value=0)
    submitted = st.form_submit_button("登録 / 上書き")

    if submitted and new_name:
        st.session_state.product_master[new_name] = {
            "単価売上": new_price,
            "材料費": new_mat_cost,
            "外注費": new_out_cost
        }
        st.sidebar.success(f"{new_name} をマスターに登録しました")

# --- 製品マスター表示 ---
st.sidebar.markdown("### 📋 製品マスター一覧")
st.sidebar.dataframe(pd.DataFrame(st.session_state.product_master).T)

# --- 製品データ登録フォーム ---
st.subheader("📥 製品データ登録（製品マスター使用）")
with st.form("entry_form"):
    col1, col2 = st.columns(2)

    with col1:
        product = st.selectbox("製品を選択", list(st.session_state.product_master.keys()))
        quantity = st.number_input("出荷数量", step=1, min_value=1, value=1)
        purchase_date = st.date_input("材料購入日", value=datetime.today())

    with col2:
        shipment_date = st.date_input("出荷日", value=datetime.today())

    submitted2 = st.form_submit_button("送信")

    if submitted2:
        if shipment_date < purchase_date:
            st.error("⚠ 出荷日は材料購入日以降にしてください。")
        else:
            master = st.session_state.product_master[product]
            unit_price = master["単価売上"]
            material_cost = master["材料費"]
            outsourcing_cost = master["外注費"]

            lt_days = max((shipment_date - purchase_date).days, 1)
            sales = unit_price * quantity
            tp = sales - material_cost * quantity - outsourcing_cost * quantity
            tp_per_lt = round(tp / lt_days, 2)
            tp_per_unit = round(tp / quantity, 2)
            tp_per_unit_per_lt = round(tp / quantity / lt_days, 2)

            new_entry = {
                "製品名": product,
                "出荷数量": quantity,
                "売上": sales,
                "材料費": material_cost * quantity,
                "外注費": outsourcing_cost * quantity,
                "材料購入日": purchase_date.strftime("%Y-%m-%d"),
                "出荷日": shipment_date.strftime("%Y-%m-%d"),
                "LT（日）": lt_days,
                "TP": tp,
                "TP/LT": tp_per_lt,
                "1個あたりTP": tp_per_unit,
                "1個あたりTP/LT": tp_per_unit_per_lt
            }

            st.session_state.product_data.append(new_entry)
            st.success("✅ データ登録完了")

# --- データ表示と分析 ---
st.markdown("---")
st.subheader("📋 製品データ一覧と分析")

if len(st.session_state.product_data) == 0:
    st.info("📭 まだデータが登録されていません。")
else:
    df = pd.DataFrame(st.session_state.product_data)
    st.dataframe(df, use_container_width=True)

    st.markdown("### 📌 製品別平均サマリー")
    summary_df = df.groupby("製品名").agg({
        "TP": "mean",
        "TP/LT": "mean",
        "1個あたりTP": "mean",
        "1個あたりTP/LT": "mean"
    }).rename(columns={
        "TP": "平均TP",
        "TP/LT": "平均TP/LT",
        "1個あたりTP": "平均1個あたりTP",
        "1個あたりTP/LT": "平均1個あたりTP/LT"
    }).reset_index()

    st.write(f"登録製品数：{summary_df.shape[0]} 製品")
    st.dataframe(summary_df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 CSVダウンロード", data=csv, file_name="tp_lt_data.csv", mime="text/csv")

    st.markdown("---")
    st.subheader("📈 TP/LT 分析グラフ（横軸：TP/LT、縦軸：TP）")

    fig = px.scatter(
        df,
        x="TP/LT",
        y="TP",
        size="TP",
        color="製品名",
        hover_name="製品名",
        title="TP vs TP/LT（製品別バブルチャート）",
        labels={"TP/LT": "キャッシュ生産性", "TP": "スループット（TP）"}
    )
    st.plotly_chart(fig, use_container_width=True)
