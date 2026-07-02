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
        .place-card {background: #fff; border: 1px solid #e0e0e0; border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);}
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

if st.button("Выбрать случайное место") and not data.empty:
    r = data.sample(1).iloc[0]
    st.markdown(f"<div class='place-card' style='border: 2px solid #FF4B4B'><h4>{r['name']}</h4><img class='place-img' src='{r['image']}'><p>{r['review']}</p></div>", unsafe_allow_html=True)

if not data.empty:
    tabs = st.tabs(CATEGORIES)
    for tab, cat in zip(tabs, CATEGORIES):
        with tab:
            for _, row in data[data["category"] == cat].iterrows():
                st.markdown(f"<div class='place-card'><h4>{row['name']}</h4><img class='place-img' src='{row['image']}'><p>{row['review']}</p></div>", unsafe_allow_html=True)
                if st.button(f"🗑 Удалить {row['name']}", key=f"del_{row['id']}"):
                    execute_query("DELETE FROM places WHERE id = ?", (row['id'],))
                    st.rerun()
else:
    st.info("Пока пусто.")
