
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

st.set_page_config(page_title="キャッシュ生産性アプリ", layout="wide")

# 初期化
if "product_master_df" not in st.session_state:
    st.session_state.product_master_df = pd.DataFrame(columns=["品名", "材料費", "外注費用", "売上単価"])

# 製品マスター CSV アップロード
with st.sidebar.expander("📥 製品マスター登録（CSV）"):
    uploaded_master = st.file_uploader("CSVアップロード", type="csv", key="master")
    if uploaded_master:
        st.session_state.product_master_df = pd.read_csv(uploaded_master)

# 製品マスター手動登録
with st.sidebar.expander("✍️ 製品マスター登録（手動）"):
    with st.form("register_form"):
        new_name = st.text_input("品名")
        new_mat_cost = st.number_input("材料費", value=0)
        new_out_cost = st.number_input("外注費用", value=0)
        new_price = st.number_input("売上単価", value=0)
        reg_submit = st.form_submit_button("登録")
        if reg_submit and new_name:
            new_row = pd.DataFrame([{
                "品名": new_name,
                "材料費": new_mat_cost,
                "外注費用": new_out_cost,
                "売上単価": new_price
            }])
            st.session_state.product_master_df = pd.concat([st.session_state.product_master_df, new_row], ignore_index=True)

st.title("📊 キャッシュ生産性アプリ")

with st.form("data_entry_form"):
    col1, col2 = st.columns(2)
    with col1:
        product_name = st.selectbox("製品名", options=st.session_state.product_master_df["品名"].unique() if not st.session_state.product_master_df.empty else [])
    with col2:
        quantity = st.number_input("出荷数量", min_value=1, value=1)

    # 該当製品がマスターにあるか確認
    filtered = st.session_state.product_master_df[st.session_state.product_master_df["品名"] == product_name]
    if not filtered.empty:
        selected_row = filtered.iloc[0]
        default_material = selected_row["材料費"]
        default_outsource = selected_row["外注費用"]
        default_price = selected_row["売上単価"]
    else:
        st.warning("選択された製品が製品マスターに存在しません。")
        default_material = default_outsource = default_price = 0

    col3, col4 = st.columns(2)
    with col3:
        material_cost = st.number_input("材料費", value=default_material)
        outsource_cost = st.number_input("外注費用", value=default_outsource)
    with col4:
        unit_price = st.number_input("売上単価", value=default_price)

    col5, col6 = st.columns(2)
    with col5:
        start_date = st.date_input("生産開始日", value=datetime.today())
    with col6:
        ship_date = st.date_input("出荷日", value=datetime.today())

    submitted = st.form_submit_button("計算する")

if submitted:
    lt = max((ship_date - start_date).days, 1)
    tp = (unit_price - material_cost - outsource_cost) * quantity
    tpl = tp / lt

    result_df = pd.DataFrame([{
        "製品名": product_name,
        "数量": quantity,
        "材料費": material_cost,
        "外注費": outsource_cost,
        "売上単価": unit_price,
        "スループット": tp,
        "LT": lt,
        "TP/LT": tpl
    }])

    st.subheader("計算結果")
    st.dataframe(result_df)

    fig = px.scatter(
        result_df,
        x="TP/LT", y="スループット",
        size="数量", color="製品名",
        hover_data=["売上単価", "LT"]
    )
    st.plotly_chart(fig, use_container_width=True)

    # CSVダウンロード
    csv = result_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("結果をCSVでダウンロード", data=csv, file_name="result.csv", mime="text/csv")
