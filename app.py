import streamlit as st
import pandas as pd
import sqlite3
import random

DB_NAME = "piter.db"

CATEGORY_ICONS = {
    "Где поесть": "fa-solid fa-burger",
    "Где погулять": "fa-solid fa-map-location-dot",
    "Музеи": "fa-solid fa-palette",
}

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1599946347371-68eb71b16afc?w=800"


def init_db():
    conn = sqlite3.connect(DB_NAME)
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
    conn.commit()
    conn.close()


def load_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM places", conn)
    conn.close()
    return df


def add_place_to_db(name, category, status, image, review):
    conn = sqlite3.connect(DB_NAME)
    conn.execute(
        "INSERT INTO places (name, category, status, image, review) VALUES (?, ?, ?, ?, ?)",
        (name, category, status, image, review)
    )
    conn.commit()
    conn.close()


def update_place_in_db(place_id, name, status, image, review):
    conn = sqlite3.connect(DB_NAME)
    conn.execute(
        "UPDATE places SET name=?, status=?, image=?, review=? WHERE id=?",
        (name, status, image, review, place_id)
    )
    conn.commit()
    conn.close()


def delete_place_from_db(place_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("DELETE FROM places WHERE id = ?", (place_id,))
    conn.commit()
    conn.close()


def clean_css(css: str) -> str:
    return "\n".join(line.strip() for line in css.strip("\n").split("\n"))


init_db()
df = load_data()

st.set_page_config(page_title="Ходилки бродилки по Питеру", page_icon="❤️", layout="centered")


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
}}

* {{ font-family: 'Inter', sans-serif; }}

[data-testid="stToolbar"], [data-testid="stAppDeployButton"], #MainMenu, footer {{ display: none !important; }}

[data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stSidebar"] {{
    background-color: var(--page-bg);
    color: var(--text);
}}

.main-title {{
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #FF4B4B, #FF8585);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}}

.subtitle {{
    font-weight: 700;
    font-size: 1.3rem;
    color: var(--text);
    margin: 6px 0 14px 0;
}}

.place-card {{
    background-color: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 16px 18px;
    margin-bottom: 16px;
    max-width: 420px;
    box-shadow: 0px 4px 16px var(--shadow);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}

.place-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0px 8px 24px var(--shadow-hover);
}}

.place-card i {{
    margin-right: 8px;
    color: #FF4B4B;
    font-size: 1.05rem;
}}

.place-card h3, .place-card h4 {{
    color: var(--text) !important;
    font-weight: 700 !important;
}}

.place-img {{
    object-fit: cover;
    border-radius: 12px;
    width: 100%;
    height: 170px;
    margin: 10px 0;
}}

.badge {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 10px;
}}
.badge-love {{ background-color: #FFE5E5; color: #FF4B4B; }}
.badge-plan {{ background-color: #EAF2FF; color: #1E62FF; }}

.place-desc {{
    color: var(--desc-text);
    font-size: 0.92rem;
    line-height: 1.5;
    margin-bottom: 10px;
}}


div[data-testid="stButton"] button {{
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    background-color: var(--card-bg) !important;
    color: var(--text) !important;
    font-weight: 500 !important;
    padding: 4px 0 !important;
    min-height: 0 !important;
    box-shadow: 0px 1px 4px var(--shadow) !important;
    transition: border-color 0.2s ease, color 0.2s ease !important;
}}
div[data-testid="stButton"] button:hover {{
    border-color: #FF4B4B !important;
    color: #FF4B4B !important;
}}
div[data-testid="stButton"] button p {{
    color: inherit !important;
    font-size: 0.82rem !important;
}}


div[class*="st-key-card_"] {{
    position: relative;
}}
div[class*="st-key-card_"] > div:nth-child(2) {{
    position: absolute;
    top: 14px;
    right: 54px;
    z-index: 2;
    width: auto !important;
}}
div[class*="st-key-card_"] > div:nth-child(3) {{
    position: absolute;
    top: 14px;
    right: 14px;
    z-index: 2;
    width: auto !important;
}}
div[class*="st-key-card_"] > div:nth-child(2) button,
div[class*="st-key-card_"] > div:nth-child(3) button {{
    width: 34px !important;
    height: 34px !important;
    padding: 0 !important;
    min-height: 0 !important;
    border-radius: 50% !important;
    border: 1px solid var(--border) !important;
    background-color: var(--card-bg) !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
    opacity: 0.5;
    filter: grayscale(1);
    transition: opacity 0.2s ease, filter 0.2s ease !important;
}}
div[class*="st-key-card_"] > div:nth-child(2) button:hover,
div[class*="st-key-card_"] > div:nth-child(3) button:hover {{
    opacity: 1;
    filter: none;
    border-color: #FF4B4B !important;
}}
div[class*="st-key-card_"] > div:nth-child(2) button p,
div[class*="st-key-card_"] > div:nth-child(3) button p {{
    font-size: 0.95rem !important;
}}
"""

st.markdown(f"<style>{clean_css(FULL_CSS)}</style>", unsafe_allow_html=True)


st.markdown("<h1 class='main-title'>Ходилки бродилки по Питеру</h1>", unsafe_allow_html=True)



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


if not df.empty:
    with st.container(border=True):
        st.subheader("🎲 Не знаете куда пойти?")
        if st.button("Выбрать случайное место", use_container_width=True):
            random_place = df.iloc[random.randint(0, len(df) - 1)]
            render_card(random_place)

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
