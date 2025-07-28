
import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="キャッシュ生産性アプリ v9", layout="wide")

st.title("📊 キャッシュ生産性アプリ v9 - 製品マスター連携版")

# 製品マスター読み込み
uploaded_master = st.file_uploader("🔧 製品マスターCSVをアップロードしてください", type="csv")

if uploaded_master:
    master_df = pd.read_csv(uploaded_master)
    st.success("製品マスターを読み込みました。")

    # 入力フォーム
    with st.form("input_form"):
        st.subheader("📝 製品情報を手動入力")
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

    if "records" not in st.session_state:
        st.session_state.records = []

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

    # 入力済みデータ表示
    if st.session_state.records:
        df_records = pd.DataFrame(st.session_state.records)
        st.dataframe(df_records, use_container_width=True)

        # 平均表示
        avg_tp = df_records["スループット"].mean()
        avg_tpl = df_records["TP/LT"].mean()
        total_products = len(df_records)

        st.markdown(f"✅ 製品数: **{total_products}**, 平均TP: **{avg_tp:.2f}**, 平均TP/LT: **{avg_tpl:.2f}**")

        # CSVダウンロード
        csv = df_records.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 CSVでダウンロード", csv, file_name="キャッシュ生産性結果.csv", mime="text/csv")
else:
    st.info("製品マスターCSVをアップロードすると、入力フォームが表示されます。")
