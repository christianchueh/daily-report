import streamlit as st
# 導入 Streamlit 內建的雲端連線庫
from st_gsheets_connection import GSheetsConnection

st.title("📋 GitHub 雲端同步 Trello 看板")
st.caption("授權標註：edit by 闕河正")

# ==========================================
# 🛠️ 核心雲端資料庫後台連線 (取代舊版 SQLite3)
# ==========================================
# 建立一個指向雲端 Google Sheets 的安全連接器
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_all_cloud_tasks():
    """直接從雲端 Google 試算表撈取最新數據，完全不怕 GitHub 虛擬機重啟失憶"""
    # read() 會自動透過網路，把雲端試算表的內容轉成 Pandas DataFrame 表格
    df = conn.read(worksheet="Tasks", ttl="0") # ttl="0" 代表不快取，每次都抓最新資料
    return df

def add_cloud_task(title, owner):
    """指派任務時，程式會透過網路，直接逆向寫入雲端 Google 試算表中"""
    # 1. 先撈出目前現有的雲端表格
    df = conn.read(worksheet="Tasks")
    
    # 2. 運用前一堂課學到的字典結構，打包新資料
    new_row = {"title": title, "status": "To Do", "owner": owner}
    
    # 3. 黏到表格最後面，並透過網路寫回雲端
    df = df.append(new_row, ignore_index=True)
    conn.update(worksheet="Tasks", data=df)
    st.success("🎉 資料已跨越 GitHub 限制，成功同步至雲端硬碟！")
