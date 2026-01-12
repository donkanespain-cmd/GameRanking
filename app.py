import streamlit as st
import pandas as pd

st.title("🛠️ 列名诊断模式")

# 读取数据
@st.cache_data(ttl=600)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1oZnGZo6UdLcubLQiql_peS63ejwEz2SvbpiGQstZJMA/export?format=csv&gid=462611572"
    return pd.read_csv(url)

try:
    df = load_data()
    st.success("✅ 数据读取成功！")
    
    st.write("### 请把下面这行列表发给我：")
    st.code(str(df.columns.tolist()))
    
    st.write("### 数据预览（前5行）：")
    st.dataframe(df.head())

except Exception as e:
    st.error(f"读取出错: {e}")
