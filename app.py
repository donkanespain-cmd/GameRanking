import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 页面基本设置
st.set_page_config(page_title="应用排名数据看板", layout="wide")
st.title("📱 应用排名趋势与数据分析")

# 2. 读取在线数据
# ttl=600 表示缓存 10 分钟，避免频繁请求导致卡顿，想实时刷新可以去掉这个参数
@st.cache_data(ttl=600)
def load_data():
    # 这是你那个表格的专用 CSV 导出链接
    url = "https://docs.google.com/spreadsheets/d/1oZnGZo6UdLcubLQiql_peS63ejwEz2SvbpiGQstZJMA/export?format=csv&gid=462611572"
    return pd.read_csv(url)

try:
    df = load_data()
    # 强制把日期列转为日期格式，防止报错
    if '日期' in df.columns:
        df['日期'] = pd.to_datetime(df['日期'])
    if '上架时间' in df.columns:
        df['上架时间'] = pd.to_datetime(df['上架时间'])
except:
    st.error("请确保目录下有 data.csv 文件，且格式正确。")
    st.stop()

# --- 侧边栏：筛选区 ---
st.sidebar.header("🔍 筛选条件")

# 筛选1：平台选择
platform = st.sidebar.multiselect(
    "选择平台",
    options=df["平台"].unique(),
    default=df["平台"].unique()
)

# 筛选2：上架时间范围
if '上架时间' in df.columns:
    min_date = df["上架时间"].min().date()
    max_date = df["上架时间"].max().date()
    start_date, end_date = st.sidebar.date_input(
        "上架时间范围",
        [min_date, max_date]
    )

# --- 数据处理 ---
# 根据筛选条件过滤数据
mask = (df["平台"].isin(platform))
if '上架时间' in df.columns:
    mask = mask & (df["上架时间"].dt.date >= start_date) & (df["上架时间"].dt.date <= end_date)

filtered_df = df[mask]

# --- 主页面：图表区 (分开展示) ---
st.subheader("📈 排名趋势图")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### iOS 趋势")
    ios_data = filtered_df[filtered_df['平台'] == 'iOS']
    if not ios_data.empty:
        fig_ios = px.line(ios_data, x='日期', y='排名', color='应用名称', title="iOS 排名走势")
        fig_ios.update_yaxes(autorange="reversed") # 排名通常越小越好，所以翻转Y轴
        st.plotly_chart(fig_ios, use_container_width=True)
    else:
        st.info("暂无 iOS 数据")

with col2:
    st.markdown("#### Android 趋势")
    android_data = filtered_df[filtered_df['平台'] == 'Android']
    if not android_data.empty:
        fig_android = px.line(android_data, x='日期', y='排名', color='应用名称', title="Android 排名走势")
        fig_android.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_android, use_container_width=True)
    else:
        st.info("暂无 Android 数据")

# --- 主页面：详细数据表 ---
st.divider()
st.subheader("📋 详细数据列表")
st.caption("💡 提示：点击表头可以进行排序（如按排名、时间等）")

# 显示表格
st.dataframe(
    filtered_df,
    use_container_width=True,
    height=500,
    hide_index=True
)
