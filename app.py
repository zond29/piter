import streamlit as st
import pandas as pd
import sqlite3
import random

DB_NAME = "piter.db"

# Конфигурация категорий и соответствующих красивых эмодзи для заголовков
CATEGORY_CONFIG = {
    "Где покушать": {"icon": "fa-solid fa-utensils", "emoji": "🍽️"},
    "Где погулять": {"icon": "fa-solid fa-map-location-dot", "emoji": "🗺️"},
    "Выставки":     {"icon": "fa-solid fa-palette", "emoji": "🎨"}
}

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
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            INSERT INTO places (name, category, status, image, review)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, category, status, image, review))

# Инициализация
init_db()
df = load_data()

st.set_page_config(page_title="Мой идеальный Питер", page_icon="❤️", layout="centered")

# --- СТИЛИЗАЦИЯ ИНТЕРФЕЙСА (CSS) ---
st.markdown("""
    <style>
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
        
        * { font-family: 'Inter', sans-serif; }
        
        /* ПРЯЧЕМ МЕНЮ STREAMLIT, ССЫЛКУ НА GITHUB И КНОПКУ ДЕПЛОЯ */
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
        
        /* СТИЛЬ ВКЛАДОК С ИКОНКАМИ */
        div[data-testid="stTabs"] button {
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }
        
        div[data-testid="stTabs"] button::before {
            content: "";
            display: inline-block;
            width: 20px;
            height: 20px;
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
        }
        
        /* Вкладка 1: Тарелка */
        div[data-testid="stTabs"] button:nth-of-type(1)::before {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' stroke='%23aaaaaa' stroke-width='2' viewBox='0 0 24 24'%3E%3Ccircle cx='12' cy='12' r='7'/%3E%3Cpath d='M3 4v5a3 3 0 0 0 3 3h0m-3-8h4m-2 0v12M21 3v9a2 2 0 0 1-2 2h-1V3'/%3E%3C/svg%3E");
        }
        div[data-testid="stTabs"] button:nth-of-type(1)[aria-selected="true"]::before {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' stroke='%23FF4B4B' stroke-width='2' viewBox='0 0 24 24'%3E%3Ccircle cx='12' cy='12' r='7'/%3E%3Cpath d='M3 4v5a3 3 0 0 0 3 3h0m-3-8h4m-2 0v12M21 3v9a2 2 0 0 1-2 2h-1V3'/%3E%3C/svg%3E");
        }

        /* Вкладка 2: Лес */
        div[data-testid="stTabs"] button:nth-of-type(2)::before {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' stroke='%23aaaaaa' stroke-width='2' viewBox='0 0 24 24'%3E%3Cpath d='m12 3-8 12h16L12 3zM12 15v5M12 7l-5 8h10l-5-8z'/%3E%3C/svg%3E");
        }
        div[data-testid="stTabs"] button:nth-of-type(2)[aria-selected="true"]::before {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' stroke='%23FF4B4B' stroke-width='2' viewBox='0 0 24 24'%3E%3Cpath d='m12 3-8 12h16L12 3zM12 15v5M12 7l-5 8h10l-5-8z'/%3E%3C/svg%3E");
        }

        /* Вкладка 3: Палитра */
        div[data-testid="stTabs"] button:nth-of-type(3)::before {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' stroke='%23aaaaaa' stroke-width='2' viewBox='0 0 24 24'%3E%3Cpath d='M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 14.7255 3.09032 17.1962 4.85857 19C5.03451 19.178 5.13254 19.4214 5.1192 19.6705C5.07431 20.5085 5.41473 21.3259 6.03553 21.8536C6.54546 22.2871 7.22106 22.4082 7.82855 22.1741C8.21251 22.0261 8.6366 21.9449 9.07899 21.9449C10.0526 21.9449 10.9419 22.3789 11.5543 23.0699'/%3E%3Ccircle cx='7.5' cy='10.5' r='1.5' fill='%23aaaaaa'/%3E%3Ccircle cx='11.5' cy='7.5' r='1.5' fill='%23aaaaaa'/%3E%3Ccircle cx='16.5' cy='9.5' r='1.5' fill='%23aaaaaa'/%3E%3C/svg%3E");
        }
        div[data-testid="stTabs"] button:nth-of-type(3)[aria-selected="true"]::before {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' stroke='%23FF4B4B' stroke-width='2' viewBox='0 0 24 24'%3E%3Cpath d='M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 14.7255 3.09032 17.1962 4.85857 19C5.03451 19.178 5.13254 19.4214 5.1192 19.6705C5.07431 20.5085 5.41473 21.3259 6.03553 21.8536C6.54546 22.2871 7.22106 22.4082 7.82855 22.1741C8.21251 22.0261 8.6366 21.9449 9.07899 21.9449C10.0526 21.9449 10.9419 22.3789 11.5543 23.0699'/%3E%3Ccircle cx='7.5' cy='10.5' r='1.5' fill='%23FF4B4B'/%3E%3Ccircle cx='11.5' cy='7.5' r='1.5' fill='%23FF4B4B'/%3E%3Ccircle cx='16.5' cy='9.5' r='1.5' fill='%23FF4B4B'/%3E%3C/svg%3E");
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
        }
        
        .place-img { object-fit: cover; border-radius: 12px; width: 100%; height: 200px; margin: 12px 0; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 500; margin-bottom: 10px; }
        .badge-love { background-color: #FFE5E5 !important; color: #FF4B4B !important; }
        .badge-plan { background-color: #EAF2FF !important; color: #1E62FF !important; }
        .place-desc { color: #444444 !important; font-size: 0.95rem; line-height: 1.5; margin-bottom: 15px; }
        
        /* Фикс бага с иконками на кнопках удаления */
        div[data-testid="stTabs"] button::before { content: none !important; }
        div[data-testid="stTabs"] [data-testid="stHorizontalBlock"] button::before { content: none !important; }
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
    st.success(f"Место '{new_name}' сохранено!")
    st.rerun()

st.divider()

# --- БЛОК «НЕ ЗНАЕТЕ КУДА ПОЙТИ?» (РАНДОМАЙЗЕР) ---
if not df.empty:
    st.markdown("<div style='background: #f9f9f9; padding: 20px; border-radius: 16px; border: 1px solid #eee; margin-bottom: 30px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-weight:700; margin-top:0;'>🎲 Не знаете куда пойти?</h3>", unsafe_allow_html=True)
    
    if st.button("Выбрать случайное место", use_container_width=True):
        random_place = df.sample(n=1).iloc[0]
        st.session_state['random_place'] = random_place

    if 'random_place' in st.session_state:
        r_row = st.session_state['random_place']
        if r_row['id'] in df['id'].values:
            status_class = "badge-love" if r_row['status'] == "Любимое место" else "badge-plan"
            r_review = r_row['review'] if r_row['review'] else "Без описания."
            # Подтягиваем правильный эмодзи по категории
            r_emoji = CATEGORY_CONFIG.get(r_row['category'], {}).get('emoji', '📍')
            
            st.markdown(f"""
            <div class='random-card'>
                <span class='badge {status_class}'>{r_row['status']}</span>
                <h4>{r_emoji} {r_row['name']}</h4>
                <img class='place-img' src='{r_row['image']}'>
                <p class='place-desc'>{r_review}</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- ВЫВОД ТАБОВ ---
if not df.empty:
    st.markdown("<h3 style='font-weight:700;'>Подборка мест</h3>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Где покушать", "Где погулять", "Выставки"])
    
    def render_grid(filtered_df, current_emoji):
        if filtered_df.empty:
            st.info("Тут пока пусто.")
            return
            
        cols = st.columns(2)
        
        for idx, (_, row) in enumerate(filtered_df.iterrows()):
            with cols[idx % 2]:
                status_class = "badge-love" if row['status'] == "Любимое место" else "badge-plan"
                review_text = row['review'] if row['review'] else "*Нет описания*"
                
                # Добавляем эмодзи категории прямо перед именем места
                st.markdown(f"""
                <div class='place-card'>
                    <span class='badge {status_class}'>{row['status']}</span>
                    <h4>{current_emoji} {row['name']}</h4>
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
            # Передаем эмодзи, соответствующий текущей вкладке
            render_grid(df[df["category"] == category], CATEGORY_CONFIG[category]['emoji'])
else:
    st.info("В базе данных пока пусто. Добавьте первое место через форму выше!")
