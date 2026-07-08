import streamlit as st
import pandas as pd
import random
from sqlalchemy import text

CATEGORY_ICONS = {
    "Где поесть": "fa-solid fa-burger",
    "Где погулять": "fa-solid fa-map-location-dot",
    "Музеи": "fa-solid fa-palette",
}

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1599946347371-68eb71b16afc?w=800"

conn = st.connection("sql", type="sql")


def init_db():
    with conn.session as s:
        s.execute(text('''
            CREATE TABLE IF NOT EXISTS places (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL,
                image TEXT,
                review TEXT
            )
        '''))
        s.commit()


def load_data():
    df = conn.query("SELECT * FROM places", ttl=0)
    return df


def get_data():
    return load_data()


def add_place_to_db(name, category, status, image, review):
    with conn.session as s:
        s.execute(
            text("""
                INSERT INTO places (name, category, status, image, review)
                VALUES (:name, :category, :status, :image, :review)
            """),
            {"name": name, "category": category, "status": status, "image": image, "review": review}
        )
        s.commit()


def update_place_in_db(place_id, name, status, image, review):
    with conn.session as s:
        s.execute(
            text("""
                UPDATE places SET name=:name, status=:status, image=:image, review=:review
                WHERE id=:id
            """),
            {"name": name, "status": status, "image": image, "review": review, "id": int(place_id)}
        )
        s.commit()


def delete_place_from_db(place_id):
    with conn.session as s:
        s.execute(text("DELETE FROM places WHERE id = :id"), {"id": int(place_id)})
        s.commit()


def clean_css(css: str) -> str:
    return "\n".join(line.strip() for line in css.strip("\n").split("\n"))


init_db()

st.set_page_config(page_title="Ходилки бродилки по Питеру", page_icon="❤️", layout="centered")


if "theme" not in st.session_state:
    st.session_state.theme = "Системная"


LIGHT_VARS = """
--page-bg: #FFFFFF;
--card-bg: #FFFFFF;
--text: #1A1A1A;
--desc-text: #444444;
--border: #E0E0E0;
--shadow: rgba(0,0,0,0.05);
--shadow-hover: rgba(0,0,0,0.1);
"""
DARK_VARS = """
--page-bg: #0E1117;
--card-bg: #1B1E27;
--text: #FAFAFA;
--desc-text: #C7C7CC;
--border: #2E313C;
--shadow: rgba(0,0,0,0.35);
--shadow-hover: rgba(0,0,0,0.5);
"""


LIGHT_STREAMLIT_VARS = """
--text-color: #1A1A1A;
--background-color: #FFFFFF;
--secondary-background-color: #F0F2F6;
"""
DARK_STREAMLIT_VARS = """
--text-color: #FAFAFA;
--background-color: #0E1117;
--secondary-background-color: #262730;
"""

if st.session_state.theme == "Светлая":
    theme_vars_css = f":root {{ {LIGHT_VARS} {LIGHT_STREAMLIT_VARS} }}"
elif st.session_state.theme == "Тёмная":
    theme_vars_css = f":root {{ {DARK_VARS} {DARK_STREAMLIT_VARS} }}"
else:
    theme_vars_css = f"""
    :root {{ {LIGHT_VARS} {LIGHT_STREAMLIT_VARS} }}
    @media (prefers-color-scheme: dark) {{
        :root {{ {DARK_VARS} {DARK_STREAMLIT_VARS} }}
    }}
    """


FULL_CSS = f"""
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');

:root {{
    --page-bg: #FFFFFF;
    --card-bg: #FFFFFF;
    --text: #1A1A1A;
    --desc-text: #444444;
    --border: #E0E0E0;
    --shadow: rgba(0,0,0,0.05);
    --shadow-hover: rgba(0,0,0,0.1);
    color-scheme: light dark;
}}

{theme_vars_css}

* {{ font-family: 'Inter', sans-serif; -webkit-tap-highlight-color: transparent; }}

[data-testid="stToolbar"], [data-testid="stAppDeployButton"], #MainMenu, footer {{ display: none !important; }}

[data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stSidebar"] {{
    background-color: var(--page-bg) !important;
    color: var(--text) !important;
}}


div[data-baseweb="tab-list"] {{ border-bottom: 1px solid var(--border) !important; background: transparent !important; }}
button[data-baseweb="tab"] {{ color: var(--text) !important; background-color: transparent !important; border: none !important; }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: #FF4B4B !important; border-bottom: 2px solid #FF4B4B !important; }}


p, div, span, h1, h2, h3, h4, label {{ color: var(--text) !important; }}
[data-testid="stExpander"], [data-testid="stVerticalBlock"] {{ border-color: var(--border) !important; }}

.main-title {{
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #FF4B4B, #FF8585);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}}

.subtitle {{ font-weight: 700; font-size: 1.3rem; color: var(--text); margin: 6px 0 14px 0; }}

.place-card {{
    background-color: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 16px 18px !important;
    margin-bottom: 16px !important;
    max-width: 420px;
    box-shadow: 0px 4px 16px var(--shadow) !important;
}}
.place-card i {{ margin-right: 8px; color: #FF4B4B; }}
.place-desc {{ color: var(--desc-text) !important; }}


.badge {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-bottom: 8px;
}}
.badge-love {{
    background-color: rgba(255, 75, 75, 0.12) !important;
    color: #FF4B4B !important;
}}
.badge-plan {{
    background-color: rgba(59, 130, 246, 0.12) !important;
    color: #3B82F6 !important;
}}


div[data-testid="stButton"] button {{
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    background-color: var(--card-bg) !important;
    color: var(--text) !important;
}}


div[class*="st-key-card_"] {{ position: relative; }}
div[class*="st-key-card_"] > div:nth-child(2) {{ position: absolute; top: 14px; right: 54px; z-index: 2; }}
div[class*="st-key-card_"] > div:nth-child(3) {{ position: absolute; top: 14px; right: 14px; z-index: 2; }}
div[class*="st-key-card_"] button {{
    width: 34px !important; height: 34px !important; padding: 0 !important; border-radius: 50% !important;
    border: 1px solid var(--border) !important; background-color: var(--card-bg) !important; opacity: 0.5;
}}

/* Фикс выпадающего меню селектов (ломалось в тёмной теме) */
div[data-baseweb="popover"],
ul[data-baseweb="menu"] {{
    background-color: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
}}
li[data-baseweb="menu-item"],
li[role="option"] {{
    background-color: var(--card-bg) !important;
    color: var(--text) !important;
}}
li[data-baseweb="menu-item"]:hover,
li[role="option"]:hover,
li[aria-selected="true"] {{
    background-color: var(--border) !important;
}}

/* Переключатель темы */
div[class*="st-key-theme_toggle_btn"] {{ position: fixed; top: 70px; right: 18px; z-index: 999999; }}
div[class*="st-key-theme_toggle_btn"] button {{
    width: 52px !important; height: 52px !important; border-radius: 50% !important;
    border: 1px solid var(--border) !important; background-color: var(--card-bg) !important;
}}
"""


st.markdown(f"<style>{clean_css(FULL_CSS)}</style>", unsafe_allow_html=True)


st.markdown("<h1 class='main-title'>Ходилки бродилки по Питеру</h1>", unsafe_allow_html=True)

theme_icon = "☽" if st.session_state.theme == "Тёмная" else "☀︎"
if st.button(theme_icon, key="theme_toggle_btn"):
    st.session_state.theme = "Светлая" if st.session_state.theme == "Тёмная" else "Тёмная"
    st.rerun()


with st.expander(" Добавить новое место", expanded=False):
    with st.form("add_place_form", clear_on_submit=True):
        new_name = st.text_input("Название места:")
        col_cat, col_stat = st.columns(2)
        with col_cat:
            new_category = st.selectbox("Категория:", list(CATEGORY_ICONS.keys()))
        with col_stat:
            new_status = st.selectbox("Статус:", ["Хочу посетить", "Любимое место"])

        new_image = st.text_input("Ссылка на фото (URL):")
        new_review = st.text_area("Ваш комментарий / Описание:")

        submit_button = st.form_submit_button(label="Сохранить место", use_container_width=True)

if submit_button:
    if new_name:
        final_image = new_image.strip() if new_image else DEFAULT_IMAGE
        add_place_to_db(
            new_name.strip(),
            new_category.strip(),
            new_status.strip(),
            final_image,
            new_review.strip()
        )
        st.success(f"Место «{new_name}» успешно сохранено!")
        st.balloons()
        st.rerun()
    else:
        st.error("Пожалуйста, введите название места!")

st.divider()


def badge_class(status):
    return "badge-love" if status == "Любимое место" else "badge-plan"


def render_card(row):
    icon = CATEGORY_ICONS.get(row["category"], "fa-solid fa-location-dot")
    desc_html = f"<p class='place-desc'>{row['review']}</p>" if row["review"] else ""
    st.markdown(f"""
    <div class='place-card'>
        <span class='badge {badge_class(row['status'])}'>{row['status']}</span>
        <h4 style='margin:0 0 8px 0;'><i class="{icon}"></i>{row['name']}</h4>
        <img class='place-img' src='{row['image']}'>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)


df = get_data()
df = df[df["category"].isin(CATEGORY_ICONS.keys())].reset_index(drop=True)

if not df.empty:
    with st.container(border=True):
        st.subheader("🎲 Не знаете куда пойти?")
        if st.button("Выбрать случайное место", use_container_width=True):
            random_place = df.iloc[random.randint(0, len(df) - 1)]
            st.session_state["random_place_id"] = random_place["id"]

        if st.session_state.get("random_place_id") is not None:
            match = df[df["id"] == st.session_state["random_place_id"]]
            if not match.empty:
                render_card(match.iloc[0])
                if st.button("Свернуть", key="collapse_random", use_container_width=True):
                    st.session_state["random_place_id"] = None
                    st.rerun()

    st.markdown("<br><h3 style='font-weight:700;'>Подборка мест</h3>", unsafe_allow_html=True)
    tab_eat, tab_walk, tab_exh = st.tabs([" Где поесть", " Где погулять", " Музеи"])

    def render_grid(filtered_df):
        if filtered_df.empty:
            st.info("Тут пока пусто.")
            return

        cols = st.columns(2)
        for idx, (_, row) in enumerate(filtered_df.iterrows()):
            with cols[idx % 2]:
                with st.container(key=f"card_{row['id']}"):
                    render_card(row)

                    if st.button("✏️", key=f"edit_{row['id']}"):
                        st.session_state[f"show_edit_{row['id']}"] = not st.session_state.get(f"show_edit_{row['id']}", False)
                        st.rerun()
                    if st.button("❌", key=f"del_{row['id']}"):
                        delete_place_from_db(row['id'])
                        st.rerun()

                if st.session_state.get(f"show_edit_{row['id']}"):
                    with st.form(f"f_{row['id']}"):
                        n_name = st.text_input("Название", row['name'])
                        n_status = st.selectbox(
                            "Статус",
                            ["Хочу посетить", "Любимое место"],
                            index=["Хочу посетить", "Любимое место"].index(row['status'])
                            if row['status'] in ["Хочу посетить", "Любимое место"] else 0
                        )
                        n_image = st.text_input("Фото", row['image'])
                        n_review = st.text_area("Описание", row['review'])
                        if st.form_submit_button("Сохранить"):
                            update_place_in_db(row['id'], n_name, n_status, n_image, n_review)
                            st.session_state[f"show_edit_{row['id']}"] = False
                            st.rerun()

    with tab_eat:
        render_grid(df[df["category"] == "Где поесть"])

    with tab_walk:
        render_grid(df[df["category"] == "Где погулять"])

    with tab_exh:
        render_grid(df[df["category"] == "Музеи"])
else:
    st.info("В базе данных пока пусто. Добавьте первое место через форму выше!")
