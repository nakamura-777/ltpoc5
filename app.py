import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="TP/LT 分析アプリ", layout="wide")
st.title("📊 TP/LT キャッシュ生産性アプリ（時間対応・CSV出力付）")

if "product_data" not in st.session_state:
    st.session_state.product_data = []

st.subheader("📥 製品データ入力")
with st.form("entry_form"):
    product = st.text_input("製品名")
    sales = st.number_input("売上金額", step=1000)
    material_cost = st.number_input("材料費", step=1000)
    outsourcing_cost = st.number_input("外注費", step=1000)
    purchase_dt = st.datetime_input("材料購入日時", value=datetime.now())
    shipment_dt = st.datetime_input("出荷日時", value=datetime.now())
    submitted = st.form_submit_button("送信")

    if submitted:
        if shipment_dt < purchase_dt:
            st.error("⚠ 出荷日時は材料購入日時以降にしてください。")
        else:
            lt_hours = (shipment_dt - purchase_dt).total_seconds() / 3600
            tp = sales - material_cost - outsourcing_cost
            tp_per_lt = round(tp / lt_hours, 2) if lt_hours > 0 else 0

            new_entry = {
                "製品名": product,
                "売上": sales,
                "材料費": material_cost,
                "外注費": outsourcing_cost,
                "材料購入日時": purchase_dt.strftime("%Y-%m-%d %H:%M"),
                "出荷日時": shipment_dt.strftime("%Y-%m-%d %H:%M"),
                "LT（時間）": round(lt_hours, 2),
                "TP": tp,
                "TP/LT": tp_per_lt
            }

            st.session_state.product_data.append(new_entry)
            st.success("✅ 入力完了")

st.markdown("---")
st.subheader("📋 製品データ一覧")

if len(st.session_state.product_data) == 0:
    st.info("📭 まだデータが登録されていません。")
else:
    df = pd.DataFrame(st.session_state.product_data)
    st.dataframe(df, use_container_width=True)

    # CSV出力
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 CSVダウンロード",
        data=csv,
        file_name="tp_lt_data.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.subheader("📈 TP/LT 分析グラフ")

    fig = px.scatter(
        df,
        x="LT（時間）",
        y="TP/LT",
        size="TP",
        color="製品名",
        hover_name="製品名",
        title="製品別 TP/LT 分布（時間単位）",
        labels={"LT（時間）": "リードタイム（時間）", "TP/LT": "キャッシュ生産性"}
    )
    st.plotly_chart(fig, use_container_width=True)
