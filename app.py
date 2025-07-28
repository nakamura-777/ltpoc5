
import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px

st.set_page_config(page_title="キャッシュ生産性アプリ v10", layout="wide")
st.title("📊 キャッシュ生産性アプリ v10 - 可視化＆分析")

uploaded_master = st.file_uploader("📁 製品マスターCSVをアップロードしてください", type="csv")

if uploaded_master:
    master_df = pd.read_csv(uploaded_master)
    st.success("製品マスターを読み込みました。")

    if "records" not in st.session_state:
        st.session_state.records = []

    with st.form("input_form"):
        st.subheader("📝 手動入力でデータ追加")
        col1, col2, col3 = st.columns(3)
        with col1:
            product_name = st.selectbox("品名", master_df["品名"].unique())
            quantity = st.number_input("出荷数", min_value=1, value=10)
        with col2:
            start_date = st.date_input("生産開始日", value=date.today())
            end_date = st.date_input("出荷日", value=date.today())
        with col3:
            selected = master_df[master_df["品名"] == product_name].iloc[0]
            unit_price = st.number_input("売上単価", value=float(selected["売上単価"]))
            material_cost = st.number_input("材料費", value=float(selected["材料費"]))
            outsourcing_cost = st.number_input("外注費用", value=float(selected["外注費用"]))

        submitted = st.form_submit_button("追加する")

    if submitted:
        revenue = unit_price * quantity
        tp = revenue - material_cost - outsourcing_cost
        lt = max((end_date - start_date).days, 1)
        tpl = tp / lt
        st.session_state.records.append({
            "品名": product_name,
            "出荷数": quantity,
            "売上金額": revenue,
            "材料費": material_cost,
            "外注費": outsourcing_cost,
            "生産開始日": start_date,
            "出荷日": end_date,
            "リードタイム": lt,
            "スループット": tp,
            "TP/LT": tpl
        })
        st.success("データを追加しました。")

    if st.session_state.records:
        df_records = pd.DataFrame(st.session_state.records)
        st.subheader("📋 登録データ一覧")
        st.dataframe(df_records, use_container_width=True)

        avg_tp = df_records["スループット"].mean()
        avg_tpl = df_records["TP/LT"].mean()
        total_products = len(df_records)
        st.markdown(f"✅ 製品数: **{total_products}**, 平均TP: **{avg_tp:.2f}**, 平均TP/LT: **{avg_tpl:.2f}**")

        st.subheader("📈 バブルチャート（出荷数×TP/LT×製品）")
        fig = px.scatter(
            df_records,
            x="TP/LT",
            y="スループット",
            size="出荷数",
            color="品名",
            hover_data=["リードタイム", "売上金額"],
            title="製品別キャッシュ生産性分析"
        )
        st.plotly_chart(fig, use_container_width=True)

        csv = df_records.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 結果CSVをダウンロード", csv, file_name="キャッシュ生産性結果.csv", mime="text/csv")
else:
    st.info("製品マスターをアップロードしてください。")
