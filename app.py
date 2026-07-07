import streamlit as st
import pandas as pd
import sqlite3

DB_PATH = "piter.db"

DEFAULT_IMAGES = {
    "Где покушать": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800",
    "Где погулять": "https://images.unsplash.com/photo-1542273917363-3b1817f69a2d?w=800",
    "Выставки": "https://images.unsplash.com/photo-1572621483863-7186638061a7?w=800"
}
CATEGORY_CONFIG = {
    "Где покушать": "fa-solid fa-utensils",
    "Где погулять": "fa-solid fa-map-location-dot",
    "Выставки": "fa-solid fa-palette"
}
STATUS_CONFIG = {
    "Хочу посетить": "status-want",
    "Любимое место": "status-fav"
}

st.set_page_config(page_title="Ходилки бродилки по Питеру", page_icon="❤️", layout="centered")

# ---------- ТЕМА ----------
if "theme" not in st.session_state:
    st.session_state.theme = "Системная"

with st.sidebar:
    st.markdown("### ⚙️ Настройки")
    st.session_state.theme = st.selectbox(
        "Тема оформления:",
        ["Системная", "Светлая", "Тёмная"],
        index=["Системная", "Светлая", "Тёмная"].index(st.session_state.theme)
    )

LIGHT_VARS = """
    --bg: #FFFFFF;
    --card-bg: #FFFFFF;
    --text: #262730;
    --muted-text: #6b6b6b;
    --border: #E5E5E5;
    --shadow: rgba(0,0,0,0.06);
"""
DARK_VARS = """
    --bg: #0E1117;
    --card-bg: #1B1E27;
    --text: #FAFAFA;
    --muted-text: #A0A0A5;
    --border: #2E313C;
    --shadow: rgba(0,0,0,0.35);
"""

if st.session_state.theme == "Светлая":
    theme_css = f":root {{{LIGHT_VARS}}}"
elif st.session_state.theme == "Тёмная":
    theme_css = f":root {{{DARK_VARS}}}"
else:  # Системная
    theme_css = f"""
        :root {{{LIGHT_VARS}}}
        @media (prefers-color-scheme: dark) {{
            :root {{{DARK_VARS}}}
        }}
    """

st.markdown(f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        {theme_css}

        [data-testid="stToolbar"], [data-testid="stAppDeployButton"], #MainMenu, footer {{display: none !important;}}

        [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stSidebar"] {{
            background-color: var(--bg);
            color: var(--text);
        }}

        .main-title {{
            font-size: 2.6rem;
            font-weight: 700;
            background: linear-gradient(135deg, #FF4B4B, #FF8585);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
        }}
        .subtitle {{
            font-size: 1.4rem;
            font-weight: 600;
            color: var(--text);
            margin-top: 4px;
            margin-bottom: 18px;
        }}

        .place-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 16px 18px;
            margin-bottom: 16px;
            max-width: 420px;
            box-shadow: 0 3px 10px var(--shadow);
        }}
        .place-title {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--text);
            margin-top: 8px;
        }}
        .place-desc {{
            color: var(--muted-text);
            font-size: 0.95rem;
            margin-top: 6px;
        }}
        .place-img {{
            object-fit: cover;
            border-radius: 10px;
            width: 100%;
            height: 170px;
            margin: 10px 0;
        }}
        .icon-color {{color: #FF4B4B !important; margin-right: 8px;}}

        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
        }}
        .status-want {{background: #E7F0FF; color: #2563EB;}}
        .status-fav {{background: #FFE7EC; color: #E11D48;}}
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
st.markdown("<div class='subtitle'>📍 Подборка мест</div>", unsafe_allow_html=True)

with st.expander("➕ Добавить новое место"):
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Название:")
        c1, c2 = st.columns(2)
        cat = c1.selectbox("Категория:", list(CATEGORY_CONFIG.keys()))
        stat = c2.selectbox("Статус:", list(STATUS_CONFIG.keys()))
        img = st.text_input("Ссылка на фото (оставьте пустым для авто-заполнения):")
        rev = st.text_area("Описание:")
        if st.form_submit_button("Сохранить"):
            final_img = img if img else DEFAULT_IMAGES[cat]
            execute_query(
                'INSERT INTO places (name, category, status, image, review) VALUES (?, ?, ?, ?, ?)',
                (name, cat, stat, final_img, rev)
            )
            st.rerun()

data = pd.read_sql_query("SELECT * FROM places", sqlite3.connect(DB_PATH))


def render_card(row):
    badge_class = STATUS_CONFIG.get(row["status"], "status-want")
    desc = row["review"] if row["review"] else "*Нет описания*"
    st.markdown(f"""
        <div class='place-card'>
            <span class='status-badge {badge_class}'>{row['status']}</span>
            <div class='place-title'><i class='{CATEGORY_CONFIG[row['category']]} icon-color'></i>{row['name']}</div>
            <img class='place-img' src='{row['image']}'>
            <p class='place-desc'>{desc}</p>
        </div>
    """, unsafe_allow_html=True)


if st.button("🎲 Выбрать случайное место") and not data.empty:
    r = data.sample(1).iloc[0]
    render_card(r)

if not data.empty:
    tabs = st.tabs(list(CATEGORY_CONFIG.keys()))
    for tab, cat in zip(tabs, CATEGORY_CONFIG.keys()):
        with tab:
            for _, row in data[data["category"] == cat].iterrows():
                render_card(row)

                c1, c2 = st.columns(2)
                if c1.button("✏️ Редактировать", key=f"edit_{row['id']}"):
                    st.session_state[f"edit_{row['id']}"] = True
                if c2.button("🗑 Удалить", key=f"del_{row['id']}"):
                    execute_query("DELETE FROM places WHERE id = ?", (row['id'],))
                    st.rerun()

                if st.session_state.get(f"edit_{row['id']}"):
                    with st.form(f"f_{row['id']}"):
                        n_n = st.text_input("Название", row['name'])
                        n_s = st.selectbox(
                            "Статус",
                            list(STATUS_CONFIG.keys()),
                            index=list(STATUS_CONFIG.keys()).index(row['status']) if row['status'] in STATUS_CONFIG else 0
                        )
                        n_i = st.text_input("Фото", row['image'])
                        n_r = st.text_area("Описание", row['review'])
                        if st.form_submit_button("Сохранить"):
                            execute_query(
                                "UPDATE places SET name=?, status=?, image=?, review=? WHERE id=?",
                                (n_n, n_s, n_i, n_r, row['id'])
                            )
                            st.session_state[f"edit_{row['id']}"] = False
                            st.rerun()
else:
    st.info("Пока пусто.")
