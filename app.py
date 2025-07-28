import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="TP/LT 材料発注 PoC", layout="wide")
st.title("📊 製品別 TP/LT 一覧 と 材料発注 PoC")

# セッション状態に保存
if "product_data" not in st.session_state:
    st.session_state.product_data = []

st.subheader("📥 データ入力")
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
            st.session_state.product_data.append({
                "製品名": product,
                "売上": sales,
                "材料費": material_cost,
                "外注費": outsourcing_cost,
                "材料購入日": str(purchase_date),
                "出荷日": str(shipment_date),
                "LT（日数）": lt,
                "TP": tp,
                "TP/LT": tp_per_lt,
                "発注済": False,
                "発注日": ""
            })
            st.success("✅ 入力を保存しました")

# 一覧表示と発注ボタン
st.subheader("📋 製品一覧と材料発注")

if len(st.session_state.product_data) == 0:
    st.info("データがまだ登録されていません。")
else:
    for i, item in enumerate(st.session_state.product_data):
        cols = st.columns([2, 1, 1, 1, 1, 1, 1, 1.5])
        cols[0].markdown(f"**{item['製品名']}**")
        cols[1].write(item["売上"])
        cols[2].write(item["LT（日数）"])
        cols[3].write(item["TP"])
        cols[4].write(item["TP/LT"])
        if item["発注済"]:
            cols[5].success("✅ 発注済")
            cols[6].write(item["発注日"])
        else:
            if cols[5].button("📦 発注", key=f"order_{i}"):
                item["発注済"] = True
                item["発注日"] = str(date.today())
                st.experimental_rerun()
