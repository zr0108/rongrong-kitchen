# ==============================
# 荣荣厨房 - AI定制菜谱
# iOS 手机 APP 专用版
# ==============================
import streamlit as st

# ========== AI 模型配置 ==========
from openai import OpenAI
client = OpenAI(
    api_key=st.secrets.get("ARK_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

# ========== iOS APP 页面设置 ==========
st.set_page_config(
    page_title="荣荣厨房",
    page_icon="🍱",
    layout="centered",
    initial_sidebar_state="collapsed"
)
# ========== iPhone 风格样式 ==========
st.markdown("""
<style>
/* iOS 风格 */
body {
    background-color: #f2f2f7;
    font-family: "SF Pro Text", sans-serif;
}
/* 大按钮 */
.stButton>button {
    background-color: #FF5A5F;
    color: white;
    border-radius: 16px;
    height: 58px;
    font-size: 18px;
    font-weight: 500;
}
/* 卡片 */
.card {
    background: white;
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)



# ========== 初始化缓存 ==========
if "dish_list" not in st.session_state:
    st.session_state.dish_list = ""
if "final_recipe" not in st.session_state:
    st.session_state.final_recipe = ""
if "tip" not in st.session_state:
    st.session_state.tip = ""

# ========== APP 标题 ==========
st.title("🍱 荣荣厨房")
st.markdown("#### 荣荣定制菜谱 · 居家神器")

# ========== 客户功能区 ==========
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 🥕 您家里有什么食材？用空格或逗号分隔")

ingredients = st.text_input(
    "食材",
    placeholder="例如：玉米 土豆 鸡蛋 或 玉米,土豆,鸡蛋（逗号/空格分隔都可以）",
    label_visibility="collapsed"
)

taste = st.selectbox("口味偏好", ["家常", "清淡", "麻辣", "酸甜", "减脂少油"])
taboo = st.text_input("不吃/过敏/禁忌", "无")

# 选择：想做几道菜
dish_count = st.number_input("您想做几道菜？", min_value=1, max_value=10, value=1)

# 选择：食材使用方式
use_type = st.radio(
    "食材使用方式：",
    [
        "只用我现有的食材",
        "用现有食材 + 可以加其他食材"
    ],
    index=0
)

if st.button("🍽 推荐可以做的菜"):
    if ingredients:
        with st.spinner("荣荣大厨正在为您推荐..."):
            
            # 👇 你要的数量规则
            if dish_count <= 2:
                recommend_num = 3
            else:
                recommend_num = 5  # 3道以上 → 至少5个菜

            # 👇 食材规则
            if use_type == "只用我现有的食材":
                rule = "只使用用户提供的食材，调料佐料默认家里都有，不额外加食材"
                tip = ""
            else:
                rule = "主要使用用户提供的食材，可以合理增加其他搭配食材"
                tip = "⚠️ 记得提前购买需要额外准备的食材哦！"
           # 👇 动态生成菜名格式
            format_lines = "\n".join([f"{i}. 菜名" for i in range(1, recommend_num+1)])

            # 推荐指令
            prompt = f"""
用户有食材：{ingredients}
口味：{taste}
禁忌：{taboo}

请推荐{recommend_num}道【【全国最火、饭店和家庭都常做的经典菜】
要求：  
1. {rule}
2. 菜名必须是人人都听过的正常菜，绝对不要乱搭配食材
3. 做法家常、好吃、网上一搜就有
4. 如果用户说可以额外用其他食材，就不要拘泥于他现有的食材

只输出菜名，严格格式：
{format_lines}
"""
            res = client.chat.completions.create(
                model="deepseek-v3-2-251201",
                messages=[{"role":"user","content":prompt}]
            )
            st.session_state.dish_list = res.choices[0].message.content
            st.session_state.tip = tip
    else:
        st.warning("请输入食材！")

# 显示推荐结果（永远不消失）
if st.session_state.dish_list:
    st.success("✅ 为您推荐菜品：")
    st.markdown(st.session_state.dish_list)
    if st.session_state.tip:
        st.info(st.session_state.tip)

st.markdown('</div>', unsafe_allow_html=True)

# ========== 客户提示 ==========
st.markdown('<div class="card">', unsafe_allow_html=True)
st.info("📩 选好后，把菜名发给荣荣，即可获取完整菜谱；如果有想吃的其他菜，也可以直接输入菜名搜索")
st.markdown('</div>', unsafe_allow_html=True)

# ========== 生成菜谱 ==========
st.divider()

st.markdown('<div class="card" style="background:#fffbf5">', unsafe_allow_html=True)
st.markdown("### 👨🍳 荣荣大厨 - 生成菜谱")
selected_dish = st.text_input("请输入你选择的菜名")
people = st.selectbox("几人份", ["1人", "2人", "3-4人", "5人以上"])

if st.button("✨ 生成完整菜谱"):
    if selected_dish:
        with st.spinner("正在生成详细菜谱..."):
            prompt = f"""
你是专业的厨师，按照网上最常见、最标准的家常做法写菜谱。
菜名：{selected_dish}
用户有的主料：{ingredients}
分量：{people}
口味：{taste}
禁忌：{taboo}
食材规则：{use_type}（调料默认都有）
要求：
1. 菜名就用用户输入的「{selected_dish}」，不要加「麻辣」「无香菜版」这类后缀
2. 做法里避开用户禁忌食材，符合口味偏好
3. 步骤家常、简单、可操作
4. 只用这道菜【传统、正宗、标准】的食材和做法
5. 绝对不要自动加入用户提供的多余食材
6. 绝对不要乱改菜谱，不创新、不乱搭配，步骤简单家常，和网上正常教程一致
格式：
-------------------
🍱 菜名：
👥 分量：
🍽 食材与用量：
🔥 做法步骤：
💡 小贴士：
-------------------
"""
            res = client.chat.completions.create(
                model="deepseek-v3-2-251201",
                messages=[{"role":"user","content":prompt}]
            )
            st.session_state.final_recipe = res.choices[0].message.content

# 显示菜谱
if st.session_state.final_recipe:
    st.success("✅ 菜谱生成完成！")
    st.markdown(st.session_state.final_recipe)

st.markdown('</div>', unsafe_allow_html=True)
