import streamlit as st
import pandas as pd
import sqlite3
import re

DB_NAME = "piter.db"

CATEGORY_CONFIG = {
    "Где покушать": {"icon": "fa-solid fa-utensils"},
    "Где погулять": {"icon": "fa-solid fa-map-location-dot"},
    "Выставки":     {"icon": "fa-solid fa-palette"}
}

# --- НАСТРОЙКА ---
st.set_page_config(page_title="Ходилки бродилки по Питеру", page_icon="❤️", layout="centered")

# --- CSS: СКРЫВАЕМ ЛИШНЕЕ, ОСТАВЛЯЕМ ВЫБОР ТЕМЫ ---
st.markdown("""
    <style>
        /* Скрываем всё, кроме заголовка с меню настроек */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        div[data-testid="stDecoration"] {display: none;}
        
        /* Принудительно скрываем иконку GitHub */
        a[href*="github.com"] { display: none !important; }
        
        /* Скрываем кнопку "View source code" */
        button[title="View source code"] { display: none !important; }
        
        /* Обеспечиваем видимость меню настроек (⋮) */
        header {visibility: visible !important; background: transparent !important;}
        [data-testid="stToolbar"] {visibility: visible !important;}

        .main-title {
            font-size: 2.8rem; font-weight: 700;
            background: linear-gradient(135deg, #FF4B4B, #FF8585);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .place-card { background-color: #ffffff !important; border: 1px solid #E0E0E0; border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05); }
        .random-card { background-color: #ffffff !important; border: 2px solid #FF4B4B !important; border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 0px 4px 25px rgba(255, 75, 75, 0.15); }
        .place-card h4, .random-card h4 { color: #1A1A1A !important; font-weight: 700 !important; margin: 0 0 8px 0; font-size: 1.5rem; display: flex; align-items: center; gap: 10px; }
        .card-icon { color: #FF4B4B !important; font-size: 1.35rem; }
        .place-img { object-fit: cover; border-radius: 12px; width: 100%; height: 200px; margin: 12px 0; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 500; margin-bottom: 10px; }
        .badge-love { background-color: #FFE5E5 !important; color: #FF4B4B !important; }
        .badge-plan { background-color: #EAF2FF !important; color: #1E62FF !important; }
        .place-desc { color: #444444 !important; font-size: 0.95rem; line-height: 1.5; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- ЛОГИКА ---
def remove_emojis(text): return re.sub(r'[\u2600-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDC00-\uDFFF]', '', text).strip()
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS places (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT NOT NULL, status TEXT NOT NULL, image TEXT, review TEXT)')

init_db()
df = pd.read_sql_query("SELECT * FROM places", sqlite3.connect(DB_NAME))

# --- ИНТЕРФЕЙС ---
st.markdown("<h1 class='main-title'>Ходилки бродилки по Питеру</h1>", unsafe_allow_html=True)

with st.expander("➕ Добавить новое место"):
    with st.form("add_place_form", clear_on_submit=True):
        new_name = st.text_input("Название:")
        col1, col2 = st.columns(2)
        new_cat = col1.selectbox("Категория:", list(CATEGORY_CONFIG.keys()))
        new_stat = col2.selectbox("Статус:", ["Хочу посетить", "Любимое место"])
        new_img = st.text_input("Ссылка на фото (URL):")
        new_rev = st.text_area("Описание:")
        if st.form_submit_button("Сохранить"):
            with sqlite3.connect(DB_NAME) as conn:
                conn.execute('INSERT INTO places (name, category, status, image, review) VALUES (?, ?, ?, ?, ?)', 
                             (remove_emojis(new_name), new_cat, new_stat, new_img or "https://images.unsplash.com/photo-1599946347371-68eb71b16afc?w=800", new_rev))
            st.rerun()

st.divider()

if not df.empty:
    if st.button("🎲 Выбрать случайное место"):
        st.session_state['random'] = df.sample(n=1).iloc[0]
    if 'random' in st.session_state:
        r = st.session_state['random']
        st.markdown(f"<div class='random-card'><span class='badge badge-love'>{r['status']}</span><h4>{r['name']}</h4><img class='place-img' src='{r['image']}'><p class='place-desc'>{r['review']}</p></div>", unsafe_allow_html=True)

    st.subheader("Подборка мест")
    tabs = st.tabs(list(CATEGORY_CONFIG.keys()))
    for tab, cat in zip(tabs, CATEGORY_CONFIG.keys()):
        with tab:
            for _, row in df[df["category"] == cat].iterrows():
                st.markdown(f"<div class='place-card'><h4>{row['name']}</h4><img class='place-img' src='{row['image']}'><p class='place-desc'>{row['review']}</p></div>", unsafe_allow_html=True)
                if st.button(f"🗑 Удалить {row['name']}", key=f"del_{row['id']}"):
                    with sqlite3.connect(DB_NAME) as conn: conn.execute("DELETE FROM places WHERE id = ?", (row['id'],))
                    st.rerun()
else:
    st.info("Добавьте первое место!")
