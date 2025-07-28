
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="キャッシュ生産性アプリ v13", layout="wide")

st.title("📊 キャッシュ生産性アプリ v13")

# 製品マスターの読み込みまたは手動登録
st.sidebar.header("📦 製品マスター管理")
product_master_file = st.sidebar.file_uploader("製品マスターCSVをアップロード", type="csv")

if "product_master_df" not in st.session_state:
    st.session_state.product_master_df = pd.DataFrame(columns=["品名", "材料費", "外注費用", "売上単価"])

if product_master_file:
    uploaded_df = pd.read_csv(product_master_file)
    if set(["品名", "材料費", "外注費用", "売上単価"]).issubset(uploaded_df.columns):
        st.session_state.product_master_df = uploaded_df.drop_duplicates(subset=["品名"])
    else:
        st.sidebar.error("列名が正しくありません。['品名', '材料費', '外注費用', '売上単価'] を含めてください。")

with st.sidebar.expander("🔧 製品マスター手動登録"):
    with st.form("manual_register"):
        pname = st.text_input("品名")
        material_cost = st.number_input("材料費", min_value=0, value=0)
        outsourcing_cost = st.number_input("外注費用", min_value=0, value=0)
        sales_price = st.number_input("売上単価", min_value=0, value=0)
        submit = st.form_submit_button("登録")
        if submit and pname:
            new_entry = pd.DataFrame([[pname, material_cost, outsourcing_cost, sales_price]],
                                     columns=["品名", "材料費", "外注費用", "売上単価"])
            st.session_state.product_master_df = pd.concat([st.session_state.product_master_df, new_entry]).drop_duplicates(subset=["品名"])
            st.success(f"{pname} を登録しました。")

# データ入力フォーム
st.header("📝 生産データ入力")
with st.form("data_entry_form"):
    selected_product = st.selectbox("品名を選択", options=st.session_state.product_master_df["品名"].unique())
    selected_row = st.session_state.product_master_df[st.session_state.product_master_df["品名"] == selected_product].iloc[0]

    mat_cost = st.number_input("材料費", min_value=0, value=int(selected_row["材料費"]))
    out_cost = st.number_input("外注費", min_value=0, value=int(selected_row["外注費用"]))
    price = st.number_input("売上単価", min_value=0, value=int(selected_row["売上単価"]))
    qty = st.number_input("出荷数量", min_value=1, value=1)
    prod_date = st.date_input("生産開始日", value=datetime.today())
    ship_date = st.date_input("出荷日", value=datetime.today())

    submitted = st.form_submit_button("登録")

if "data_records" not in st.session_state:
    st.session_state.data_records = []

if submitted:
    lt = max((ship_date - prod_date).days, 1)
    tp = (price - mat_cost - out_cost) * qty
    tp_per_lt = tp / lt
    st.session_state.data_records.append({
        "品名": selected_product,
        "材料費": mat_cost,
        "外注費": out_cost,
        "売上単価": price,
        "出荷数量": qty,
        "生産開始日": prod_date,
        "出荷日": ship_date,
        "LT": lt,
        "TP": tp,
        "TP/LT": tp_per_lt
    })

# 表示・出力
if st.session_state.data_records:
    df = pd.DataFrame(st.session_state.data_records)
    st.subheader("📋 登録データ一覧")
    st.dataframe(df)

    st.download_button("📥 CSVダウンロード", data=df.to_csv(index=False), file_name="キャッシュ生産性結果.csv", mime="text/csv")

    st.subheader("📈 TP/LT バブルチャート")
    fig = px.scatter(df, x="TP/LT", y="TP", color="品名", size="出荷数量",
                     hover_name="品名", title="キャッシュ生産性バブルチャート")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 サマリー")
    st.write(f"✅ 登録製品数: {df['品名'].nunique()} 種類")
    st.write(f"✅ 平均TP: {df['TP'].mean():,.2f}")
    st.write(f"✅ 平均TP/LT: {df['TP/LT'].mean():,.2f}")
