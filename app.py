import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="TP/LT 分析アプリ", layout="wide")
st.title("📊 TP/LT キャッシュ生産性アプリ")

# セッション状態に保存
if "product_data" not in st.session_state:
    st.session_state.product_data = []

st.subheader("📥 製品データ入力")
with st.form("entry_form"):
    product = st.text_input("製品名")
    sales = st.number_input("売上金額", step=1000)
    material_cost = st.number_input("材料費", step=1000)
    outsourcing_cost = st.number_input("外注費", step=1000)
    purchase_date = st.date_input("材料購入日", value=date.today())
    shipment_date = st.date_input("出荷日", value=date.today())
    submitted = st.form_submit_button("送信")

    if submitted:
        if shipment_date < purchase_date:
            st.error("⚠ 出荷日は材料購入日以降にしてください。")
        else:
            lt = (shipment_date - purchase_date).days
            tp = sales - material_cost - outsourcing_cost
            tp_per_lt = round(tp / lt, 2) if lt > 0 else 0

            new_entry = {
                "製品名": product,
                "売上": sales,
                "材料費": material_cost,
                "外注費": outsourcing_cost,
                "材料購入日": str(purchase_date),
                "出荷日": str(shipment_date),
                "LT（日数）": lt,
                "TP": tp,
                "TP/LT": tp_per_lt
            }

            st.session_state.product_data.append(new_entry)

            st.success("✅ 入力完了")
            st.write("**結果プレビュー**")
            st.json(new_entry)

st.markdown("---")
st.subheader("📋 製品データ一覧")

if len(st.session_state.product_data) == 0:
    st.info("📭 まだデータが登録されていません。")
else:
    df = pd.DataFrame(st.session_state.product_data)
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("📈 TP/LT 分析グラフ")

    fig = px.scatter(
        df,
        x="LT（日数）",
        y="TP/LT",
        size="TP",
        color="製品名",
        hover_name="製品名",
        title="製品別 TP/LT 分布",
        labels={"LT（日数）": "リードタイム", "TP/LT": "キャッシュ生産性"}
    )
    st.plotly_chart(fig, use_container_width=True)
