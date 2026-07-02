import streamlit as st
import pandas as pd
import sqlite3
import re

DB_PATH = "piter.db"
CATEGORIES = ["Где покушать", "Где погулять", "Выставки"]

st.set_page_config(page_title="Ходилки бродилки по Питеру", page_icon="❤️")

st.markdown("""
    <style>
        [data-testid="stToolbar"], [data-testid="stAppDeployButton"], #MainMenu, footer {display: none !important;}
        .main-title {font-size: 2.8rem; font-weight: 700; background: linear-gradient(135deg, #FF4B4B, #FF8585); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
        .place-card {background: var(--background-color); border: 1px solid var(--secondary-background-color); border-radius: 16px; padding: 20px; margin-bottom: 20px;}
        .place-img {object-fit: cover; border-radius: 12px; width: 100%; height: 200px; margin: 12px 0;}
    </style>
""", unsafe_allow_html=True)

def execute_query(query, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(query, params)

def init_db():
    execute_query('''CREATE TABLE IF NOT EXISTS places 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, status TEXT, image TEXT, review TEXT)''')

init_db()

st.markdown("<h1 class='main-title'>Ходилки бродилки по Питеру</h1>", unsafe_allow_html=True)

with st.expander("➕ Добавить новое место"):
    with st.form("add_form", clear_on_submit=True):
        name = re.sub(r'[^\w\s]', '', st.text_input("Название:"))
        col1, col2 = st.columns(2)
        cat = col1.selectbox("Категория:", CATEGORIES)
        stat = col2.selectbox("Статус:", ["Хочу посетить", "Любимое место"])
        img = st.text_input("Ссылка на фото (URL):")
        rev = st.text_area("Описание:")
        if st.form_submit_button("Сохранить"):
            execute_query('INSERT INTO places (name, category, status, image, review) VALUES (?, ?, ?, ?, ?)', (name, cat, stat, img, rev))
            st.rerun()

st.divider()

data = pd.read_sql_query("SELECT * FROM places", sqlite3.connect(DB_PATH))

if not data.empty:
    tabs = st.tabs(CATEGORIES)
    for tab, cat in zip(tabs, CATEGORIES):
        with tab:
            for _, row in data[data["category"] == cat].iterrows():
                st.markdown(f"<div class='place-card'><h4>{row['name']}</h4><img class='place-img' src='{row['image']}'><p>{row['review']}</p></div>", unsafe_allow_html=True)
                
              
                c1, c2 = st.columns(2)
                if c1.button("✏️ Редактировать", key=f"edit_{row['id']}"):
                    st.session_state[f"edit_mode_{row['id']}"] = True
                if c2.button("🗑 Удалить", key=f"del_{row['id']}"):
                    execute_query("DELETE FROM places WHERE id = ?", (row['id'],))
                    st.rerun()

            
                if st.session_state.get(f"edit_mode_{row['id']}"):
                    with st.form(f"edit_form_{row['id']}"):
                        new_name = st.text_input("Название", row['name'])
                        new_img = st.text_input("Ссылка на фото", row['image'])
                        new_rev = st.text_area("Описание", row['review'])
                        if st.form_submit_button("Сохранить изменения"):
                            execute_query("UPDATE places SET name=?, image=?, review=? WHERE id=?", (new_name, new_img, new_rev, row['id']))
                            st.session_state[f"edit_mode_{row['id']}"] = False
                            st.rerun()
else:
    st.info("Пока пусто.")
