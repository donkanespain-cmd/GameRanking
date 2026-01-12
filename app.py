import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 页面基本设置
st.set_page_config(page_title="应用排名数据看板", layout="wide")
st.title("📱 应用排名数据看板")

# 2. 读取数据
@st.cache_data(ttl=600)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1oZnGZo6UdLcubLQiql_peS63ejwEz2SvbpiGQstZJMA/export?format=csv&gid=462611572"
    df = pd.read_csv(url)
    
    # --- 关键修复：数据清洗与平台识别 ---
    
    # 1. 自动生成“平台”列：根据 URL 判断 iOS 还是 Android
    def detect_platform(url):
        url_str = str(url).lower()
        if 'apple.com' in url_str:
            return 'iOS'
        elif 'google' in url_str or 'play.google' in url_str:
            return 'Android'
        else:
            return '未知'
    
    df['平台'] = df['App URL'].apply(detect_platform)

    # 2. 处理日期格式
    if 'Release date' in df.columns:
        df['Release date'] = pd.to_datetime(df['Release date'], errors='coerce')

    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"数据读取失败: {e}")
    st.stop()

# --- 侧边栏：筛选区 ---
st.sidebar.header("🔍 筛选条件")

# 筛选1：平台
platform_options = df["平台"].unique().tolist()
selected_platform = st.sidebar.multiselect(
    "选择平台",
    options=platform_options,
    default=platform_options
)

# 筛选2：发布时间范围 (Release date)
if 'Release date' in df.columns:
    min_date = df["Release date"].min().date()
    max_date = df["Release date"].max().date()
    
    # 默认显示整个时间段
    date_range = st.sidebar.date_input(
        "发布时间范围",
        [min_date, max_date]
    )

# --- 数据过滤逻辑 ---
mask = (df["平台"].isin(selected_platform))

# 处理日期筛选的逻辑（防止用户只选了一个日期导致报错）
if 'Release date' in df.columns and len(date_range) == 2:
    start_date, end_date = date_range
    mask = mask & (df["Release date"].dt.date >= start_date) & (df["Release date"].dt.date <= end_date)

filtered_df = df[mask]

# --- 核心指标卡片 ---
col_metric1, col_metric2, col_metric3 = st.columns(3)
col_metric1.metric("应用总数", len(filtered_df))
if 'Current Rank' in filtered_df.columns:
    best_rank_app = filtered_df.loc[filtered_df['Current Rank'].idxmin()]
    col_metric2.metric("当前排名第一", best_rank_app['App name'])
    col_metric3.metric("其排名", int(best_rank_app['Current Rank']))

# --- 图表区 ---
st.divider()

# 分两栏展示：左边是 Top 榜单，右边是发布时间分布
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("🏆 Top 15 排名榜单")
    if not filtered_df.empty:
        # 按当前排名排序，取前15
        top_apps = filtered_df.sort_values(by="Current Rank", ascending=True).head(15)
        # 柱状图：横向
        fig_bar = px.bar(
            top_apps, 
            x="Current Rank", 
            y="App name", 
            orientation='h',
            color="平台",
            text="Current Rank",
            title="当前排名靠前的应用 (越靠上排名越好)"
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total descending'}) # 让排名好的在上面
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("无数据")

with chart_col2:
    st.subheader("📅 发布时间 vs 排名分布")
    if not filtered_df.empty and 'Release date' in df.columns:
        # 散点图：看发布时间和排名的关系
        fig_scatter = px.scatter(
            filtered_df,
            x="Release date",
            y="Current Rank",
            color="平台",
            hover_data=["App name", "Developer"],
            title="发布时间越近排名越高吗？"
        )
        fig_scatter.update_yaxes(autorange="reversed") # 排名1在最上面
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("无数据或缺少日期列")

# --- 详细数据表 ---
st.divider()
st.subheader("📋 详细数据列表")
st.caption("提示：点击表头可排序（如按 'Current Rank' 排序）")

# 展示给用户的列名可以优化一下，或者直接显示原数据
display_cols = ['App name', 'Platform', 'Current Rank', 'Release date', 'Developer', 'Ranking change', 'App URL']
# 确保列存在才显示
valid_cols = [c for c in display_cols if c in filtered_df.columns]

st.dataframe(
    filtered_df[valid_cols],
    use_container_width=True,
    hide_index=True,
    height=600
)
