import streamlit as st
import pandas as pd
from gsheets_connection import GSheetsConnection

# 網頁大標題與授權標註
st.set_page_config(layout="wide") # 寬螢幕佈局，最適合看板
st.title("📋 GitHub 雲端同步 Trello 看板")
st.caption("授權標註：edit by 闕河正")

# ==========================================
# 🛠️ 建立雲端資料庫安全連接器
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_all_cloud_tasks():
    """從 Google 試算表讀取 Tasks 工作表"""
    try:
        # ttl="0" 代表不快取，每次重新整理都強迫去雲端抓最新資料
        df = conn.read(worksheet="Tasks", ttl="0")
        # 預防萬一：如果讀出來是空的，自動建立標準欄位骨架
        if df.empty:
            df = pd.DataFrame(columns=["title", "status", "owner"])
        return df
    except Exception as e:
        st.error(f"雲端資料庫讀取失敗，請檢查 Secrets 配置。錯誤訊息: {e}")
        return pd.DataFrame(columns=["title", "status", "owner"])

def add_cloud_task(title, status, owner):
    """指派任務時，運用最新的 pd.concat 安全寫回雲端試算表"""
    df = fetch_all_cloud_tasks()
    
    # 打包新資料
    new_row = pd.DataFrame([{"title": title, "status": status, "owner": owner}])
    
    # 修正盲點：改用新版 Pandas 的 pd.concat 取代舊的 .append()
    updated_df = pd.concat([df, new_row], ignore_index=True)
    
    # 逆向寫回雲端 Google Sheets
    conn.update(worksheet="Tasks", data=updated_df)
    st.success(f"🎉 任務「{title}」已跨越限制，成功同步至雲端！")
    st.rerun() # 強制網頁立刻刷新，看到最新看板狀態

# ==========================================
# 📥 撈取最新資料並進行前端排版
# ==========================================
df_tasks = fetch_all_cloud_tasks()

# ─── 區塊一：新增任務輸入表單 ───
st.write("### ➕ 指派新任務")
with st.form("task_form", clear_on_submit=True):
    col_t, col_s, col_o = st.columns([2, 1, 1])
    with col_t:
        new_title = st.text_input("任務名稱", placeholder="例如：準備段考題目...")
    with col_s:
        new_status = st.selectbox("初始狀態", ["To Do", "In Progress", "Done"])
    with col_o:
        new_owner = st.text_input("負責人", placeholder="例如：張同學")
    
    submit_button = st.form_submit_button("確認指派並同步雲端")
    
    if submit_button and new_title and new_owner:
        add_cloud_task(new_title, new_status, new_owner)

st.write("---")

# ─── 區塊二：Trello 經典三縱欄畫布 ───
st.write("### 🗂️ 看板動態狀態監控")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🔴 To Do")
    # 過濾出狀態為 To Do 的任務
    todo_list = df_tasks[df_tasks["status"] == "To Do"]
    if not todo_list.empty:
        for idx, row in todo_list.iterrows():
            with st.container(border=True):
                st.write(f"**📌 {row['title']}**")
                st.caption(f"👤 負責人: {row['owner']}")
    else:
        st.info("暫無任務")

with col2:
    st.markdown("### 🟡 In Progress")
    # 過濾出狀態為 In Progress 的任務
    ip_list = df_tasks[df_tasks["status"] == "In Progress"]
    if not ip_list.empty:
        for idx, row in ip_list.iterrows():
            with st.container(border=True):
                st.write(f"**⚡ {row['title']}**")
                st.caption(f"👤 負責人: {row['owner']}")
    else:
        st.info("暫無任務")

with col3:
    st.markdown("### 🟢 Done")
    # 過濾出狀態為 Done 的任務
    done_list = df_tasks[df_tasks["status"] == "Done"]
    if not done_list.empty:
        for idx, row in done_list.iterrows():
            with st.container(border=True):
                st.write(f"**✅ ~~{row['title']}~~**")
                st.caption(f"👤 負責人: {row['owner']}")
    else:
        st.info("暫無任務")
