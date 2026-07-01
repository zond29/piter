import streamlit as st
import pandas as pd
import sqlite3
import random
import re

DB_NAME = "piter.db"

# Конфигурация категорий: классы иконок Font Awesome для вкладок и карточек
CATEGORY_CONFIG = {
    "Где покушать": {"icon": "fa-solid fa-utensils"},
    "Где погулять": {"icon": "fa-solid fa-map-location-dot"},
    "Выставки":     {"icon": "fa-solid fa-palette"}
}

# Функция для удаления текстовых эмодзи из названия, чтобы они не двоились и не заменялись Windows-версией
def remove_emojis(text):
    if not text:
        return ""
    # Удаляем символы эмодзи из строки
    return re.sub(r'[\u2600-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDC00-\uDFFF]', '', text).strip()

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS places (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL,
                image TEXT,
                review TEXT
            )
        ''')

def load_data():
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query("SELECT * FROM places", conn)

def delete_place_from_db(place_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM places WHERE id = ?", (place_id,))

def add_place_to_db(name, category, status, image, review):
    # При сохранении тоже очищаем имя от случайно введенных эмодзи
    cleaned_name = remove_emojis(name)
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            INSERT INTO places (name, category, status, image, review)
            VALUES (?, ?, ?, ?, ?)
        ''', (cleaned_name, category, status, image, review))

# Инициализация базы данных
init_db()
df = load_data()

st.set_page_config(page_title="Мой идеальный Питер", page_icon="❤️", layout="centered")

# --- СТИЛИЗАЦИЯ ИНТЕРФЕЙСА (CSS) ---
st.markdown("""
    <style>
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
        
        * { font-family: 'Inter', sans-serif; }
        
        /* ПРЯЧЕМ СЛУЖЕБНЫЕ ЭЛЕМЕНТЫ STREAMLIT */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        div[data-testid="stDecoration"] {display: none;}
        button[title="View source code"] {display: none;}
        
        .main-title {
            font-size: 2.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #FF4B4B, #FF8585);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        /* ОБЫЧНАЯ КАРТОЧКА МЕСТА */
        .place-card {
            background-color: #ffffff !important;
            border: 1px solid #E0E0E0;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05);
        }
        
        /* РАНДОМНАЯ КАРТОЧКА С КРАСНОЙ РАМКОЙ */
        .random-card {
            background-color: #ffffff !important;
            border: 2px solid #FF4B4B !important;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0px 4px 25px rgba(255, 75, 75, 0.15);
        }
        
        .place-card h4, .random-card h4 { 
            color: #1A1A1A !important; 
            font-weight: 700 !important; 
            margin: 0 0 8px 0;
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        /* КРАСНЫЙ СТИЛЬ ДЛЯ ИКОНОК В ЗАГОЛОВКАХ КАРТОЧЕК */
        .card-icon {
            color: #FF4B4B !important;
            font-size: 1.35rem;
            display: inline-block;
        }
        
        .place-img { object-fit: cover; border-radius: 12px; width: 100%; height: 200px; margin: 12px 0; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 500; margin-bottom: 10px; }
        .badge-love { background-color: #FFE5E5 !important; color: #FF4B4B !important; }
        .badge-plan { background-color: #EAF2FF !important; color: #1E62FF !important; }
        .place-desc { color: #444444 !important; font-size: 0.95rem; line-height: 1.5; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>Ходилки бродилки по Питеру</h1>", unsafe_allow_html=True)

# --- ФОРМА ДОБАВЛЕНИЯ ---
with st.expander("➕ Добавить новое место", expanded=False):
    with st.form("add_place_form", clear_on_submit=True):
        new_name = st.text_input("Название места:")
        col_cat, col_stat = st.columns(2)
        with col_cat:
            new_category = st.selectbox("Категория:", list(CATEGORY_CONFIG.keys()))
        with col_stat:
            new_status = st.selectbox("Статус:", ["Хочу посетить", "Любимое место"])
            
        new_image = st.text_input("Ссылка на фото (URL):")
        new_review = st.text_area("Ваш комментарий / Описание:")
        submit_button = st.form_submit_button(label="Сохранить место", use_container_width=True)

if submit_button and new_name:
    if not new_image:
        new_image = "https://images.unsplash.com/photo-1599946347371-68eb71b16afc?w=800"
    add_place_to_db(new_name.strip(), new_category, new_status, new_image.strip(), new_review.strip())
    st.success(f"Место '{remove_emojis(new_name)}' сохранено!")
    st.rerun()

st.divider()

# --- БЛОК РАНДОМАЙЗЕРА ---
if not df.empty:
    st.markdown("<div style='background: #f9f9f9; padding: 20px; border-radius: 16px; border: 1px solid #eee; margin-bottom: 30px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-weight:700; margin-top:0;'> Не знаете куда пойти?</h3>", unsafe_allow_html=True)
    
    if st.button("Выбрать случайное место", use_container_width=True):
        random_place = df.sample(n=1).iloc[0]
        st.session_state['random_place'] = random_place

    if 'random_place' in st.session_state:
        r_row = st.session_state['random_place']
        if r_row['id'] in df['id'].values:
            status_class = "badge-love" if r_row['status'] == "Любимое место" else "badge-plan"
            r_review = r_row['review'] if r_row['review'] else "Без описания."
            r_icon_class = CATEGORY_CONFIG.get(r_row['category'], {}).get('icon', 'fa-solid fa-location-dot')
            
            # Очищаем имя от встроенных старых эмодзи перед выводом
            clean_r_name = remove_emojis(r_row['name'])
            
            st.markdown(f"""
            <div class='random-card'>
                <span class='badge {status_class}'>{r_row['status']}</span>
                <h4><i class='{r_icon_class} card-icon'></i> {clean_r_name}</h4>
                <img class='place-img' src='{r_row['image']}'>
                <p class='place-desc'>{r_review}</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- ВЫВОД ТАБОВ И ПОДБОРКИ ---
if not df.empty:
    st.markdown("<h3 style='font-weight:700;'>Подборка мест</h3>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Где покушать", "Где погулять", "Выставки"])
    
    def render_grid(filtered_df, icon_class):
        if filtered_df.empty:
            st.info("Тут пока пусто.")
            return
            
        cols = st.columns(2)
        
        for idx, (_, row) in enumerate(filtered_df.iterrows()):
            with cols[idx % 2]:
                status_class = "badge-love" if row['status'] == "Любимое место" else "badge-plan"
                review_text = row['review'] if row['review'] else "*Нет описания*"
                
                # Полностью убираем любые старые эмодзи из текста имени
                display_name = remove_emojis(row['name'])
                
                st.markdown(f"""
                <div class='place-card'>
                    <span class='badge {status_class}'>{row['status']}</span>
                    <h4><i class='{icon_class} card-icon'></i> {display_name}</h4>
                    <img class='place-img' src='{row['image']}'>
                    <p class='place-desc'>{review_text}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🗑 Удалить", key=f"del_{row['id']}", use_container_width=True):
                    delete_place_from_db(row['id'])
                    if 'random_place' in st.session_state and st.session_state['random_place']['id'] == row['id']:
                        del st.session_state['random_place']
                    st.rerun()

    for tab, category in zip(tabs, CATEGORY_CONFIG.keys()):
        with tab:
            render_grid(df[df["category"] == category], CATEGORY_CONFIG[category]['icon'])
else:
    st.info("В базе данных пока пусто. Добавьте первое место через форму выше!")
