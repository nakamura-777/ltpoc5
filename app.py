
import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px

st.set_page_config(page_title="キャッシュ生産性アプリ v12", layout="wide")
st.title("📊 キャッシュ生産性アプリ v12（製品マスター登録付き）")

if "product_master" not in st.session_state:
    st.session_state.product_master = pd.DataFrame(columns=["品名", "材料費", "外注費用", "売上単価"])
if "records" not in st.session_state:
    st.session_state.records = []

st.sidebar.header("📁 製品マスターの管理")

# CSVアップロード
uploaded_master = st.sidebar.file_uploader("CSVからマスター読込", type="csv")
if uploaded_master:
    st.session_state.product_master = pd.read_csv(uploaded_master)
    st.sidebar.success("✅ 製品マスターを読み込みました")

# 手動登録
with st.sidebar.form("product_form"):
    st.markdown("🔧 製品マスター手動登録")
    pname = st.text_input("品名")
    mcost = st.number_input("材料費", value=0.0, format="%.2f")
    ocost = st.number_input("外注費用", value=0.0, format="%.2f")
    uprice = st.number_input("売上単価", value=0.0, format="%.2f")
    add_master = st.form_submit_button("マスターに追加")
    if add_master and pname:
        st.session_state.product_master.loc[len(st.session_state.product_master)] = [pname, mcost, ocost, uprice]
        st.sidebar.success(f"✅ {pname} をマスターに追加しました")

# メイン機能
if not st.session_state.product_master.empty:
    st.subheader("📝 製品データ入力")

    with st.form("entry_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            product_name = st.selectbox("品名", st.session_state.product_master["品名"].unique())
            quantity = st.number_input("出荷数", min_value=1, value=10)

        with col2:
            start_date = st.date_input("生産開始日", value=date.today())
            end_date = st.date_input("出荷日", value=date.today())

        with col3:
            if product_name in st.session_state.product_master["品名"].values:
                selected = st.session_state.product_master[st.session_state.product_master["品名"] == product_name].iloc[0]
                unit_price_default = float(selected["売上単価"])
                material_cost_default = float(selected["材料費"])
                outsourcing_cost_default = float(selected["外注費用"])
            else:
                unit_price_default = 0.0
                material_cost_default = 0.0
                outsourcing_cost_default = 0.0

            unit_price = st.number_input("売上単価", value=unit_price_default, format="%.2f")
            material_cost = st.number_input("材料費", value=material_cost_default, format="%.2f")
            outsourcing_cost = st.number_input("外注費用", value=outsourcing_cost_default, format="%.2f")

        submitted = st.form_submit_button("追加")

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
        st.success("✅ データを追加しました")

    if st.session_state.records:
        df = pd.DataFrame(st.session_state.records)
        st.subheader("📋 登録済データ")
        st.dataframe(df, use_container_width=True)

        avg_tp = df["スループット"].mean()
        avg_tpl = df["TP/LT"].mean()
        total_products = len(df)
        st.markdown(f"✅ 製品数: **{total_products}**, 平均TP: **{avg_tp:.2f}**, 平均TP/LT: **{avg_tpl:.2f}**")

        st.subheader("📈 バブルチャート")
        fig = px.scatter(
            df,
            x="TP/LT",
            y="スループット",
            size="出荷数",
            color="品名",
            hover_data=["リードタイム", "売上金額"],
            title="製品別キャッシュ生産性分析"
        )
        st.plotly_chart(fig, use_container_width=True)

        csv = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 結果CSVをダウンロード", csv, file_name="キャッシュ生産性結果.csv", mime="text/csv")
else:
    st.info("📌 左のサイドバーから製品マスターを登録してください。")
