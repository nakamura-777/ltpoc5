import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px

st.set_page_config(page_title="キャッシュ生産性計算ツール", layout="wide")
st.title("💰 キャッシュ生産性 (TP / LT) 計算ツール")

if "records" not in st.session_state:
    st.session_state.records = []

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# 入力フォーム
st.subheader("📥 製品データ入力")
with st.form("product_form"):
    col1, col2 = st.columns(2)
    with col1:
        product_name = st.text_input("製品名", value="")
        purchase_date = st.date_input("材料購入日", value=date.today())
        sales = st.number_input("売上金額（円）", min_value=0, step=1000)
    with col2:
        shipment_date = st.date_input("出荷日", value=date.today())
        material_cost = st.number_input("材料費（円）", min_value=0, step=1000)
        outsourcing_cost = st.number_input("外注費（円）", min_value=0, step=1000)

    submitted = st.form_submit_button("追加または更新")

    if submitted:
        if shipment_date < purchase_date:
            st.error("⚠ 出荷日は材料購入日以降にしてください。")
        elif sales < (material_cost + outsourcing_cost):
            st.error("⚠ 売上金額がコスト合計を下回っています。")
        else:
            lt = (shipment_date - purchase_date).days
            tp = sales - material_cost - outsourcing_cost
            tp_per_lt = tp / lt if lt > 0 else 0

            new_record = {
                "製品名": product_name,
                "材料購入日": purchase_date,
                "出荷日": shipment_date,
                "売上": sales,
                "材料費": material_cost,
                "外注費": outsourcing_cost,
                "LT（日数)": lt,
                "TP（スループット）": tp,
                "TP/LT（キャッシュ生産性）": round(tp_per_lt, 2)
            }

            if st.session_state.edit_index is not None:
                st.session_state.records[st.session_state.edit_index] = new_record
                st.success("✅ データが更新されました！")
                st.session_state.edit_index = None
            else:
                st.session_state.records.append(new_record)
                st.success("✅ データが追加されました！")

# 表示
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    st.subheader("📊 登録済データ")
    for i, row in df.iterrows():
        col1, col2, col3 = st.columns([4, 1, 1])
        col1.write(f"{i+1}. {row['製品名']}（TP/LT: {row['TP/LT（キャッシュ生産性）']}）")
        if col2.button("✏ 編集", key=f"edit_{i}"):
            st.session_state.edit_index = i
        if col3.button("🗑 削除", key=f"delete_{i}"):
            st.session_state.records.pop(i)
            st.experimental_rerun()

    st.markdown("---")
    st.subheader("📈 TP/LTランキング・統計")
    sorted_df = df.sort_values("TP/LT（キャッシュ生産性）", ascending=False).reset_index(drop=True)
    st.dataframe(sorted_df, use_container_width=True)

    st.markdown("### 📊 TP/LT バーグラフ")
    fig = px.bar(sorted_df, x="製品名", y="TP/LT（キャッシュ生産性）", color="TP/LT（キャッシュ生産性）", height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🧮 指標サマリー")
    col1, col2, col3 = st.columns(3)
    col1.metric("TP合計", f"{df['TP（スループット）'].sum():,.0f} 円")
    col2.metric("平均LT", f"{df['LT（日数)'].mean():.2f} 日")
    col3.metric("平均TP/LT", f"{df['TP/LT（キャッシュ生産性）'].mean():.2f}")

    st.markdown("### 🟠 TP/LT × 売上の気泡グラフ")
    fig2 = px.scatter(df, x="TP/LT（キャッシュ生産性）", y="売上", size="TP（スループット）", color="製品名",
                      labels={"TP/LT（キャッシュ生産性）": "TP/LT", "売上": "売上金額"}, height=400)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### 📤 CSVダウンロード")
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("CSVをダウンロード", data=csv, file_name="cash_productivity.csv", mime="text/csv")
