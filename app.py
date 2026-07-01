import streamlit as st

# 1. Настройка заголовка
st.title("❤️ Мой идеальный Питер")

# 2. Создаем Хранилище Памяти сайта (Сессию)
# Так как сайт обновляется при каждом клике, нам нужна память, которая не стирается
if "my_places" not in st.session_state:
    st.session_state.my_places = [
        {
            "name": "Севкабель Порт",
            "category": "Где погулять",
            "status": "Любимое место",
            "image": "https://images.unsplash.com/photo-1620216445520-22d861611fa4?w=800",
            "review": "Потрясающий вид на Финский залив и классные закаты."
        }
    ]

# --- ОКНО ДОБАВЛЕНИЯ НОВОГО МЕСТА ---
st.subheader("➕ Добавить новое прикольное место")

# Открываем форму
with st.form("add_place_form", clear_on_submit=True):
    new_name = st.text_input("Название места:")
    new_category = st.selectbox("Категория:", ["Где покушать", "Где погулять", "Выставка"])
    new_status = st.selectbox("Статус:", ["Хочу посетить", "Любимое место"])
    new_image = st.text_input("Ссылка на фото (URL):")
    new_review = st.text_area("Ваш комментарий / Описание:")
    
    # Кнопка внутри формы
    submit_button = st.form_submit_button(label="Сохранить место")

# Логика: что происходит, когда нажали кнопку «Сохранить»
if submit_button:
    if new_name: # Проверяем, что ввели хотя бы название
        # Создаем новую карточку-словарь из того, что ввели в форму
        new_place = {
            "name": new_name,
            "category": new_category,
            "status": new_status,
            "image": new_image if new_image else "https://images.unsplash.com/photo-1599946347371-68eb71b16afc?w=800", # если нет фото, ставим заглушку Питера
            "review": new_review
        }
        # Добавляем её в наше хранилище
        st.session_state.my_places.append(new_place)
        st.success(f"Место '{new_name}' успешно добавлено!")
    else:
        st.error("Пожалуйста, введите название места!")


# --- ВЫВОД КАРТОЧЕК НА САЙТ ---
st.divider()
st.subheader("🗺 Моя подборка мест")

# Цикл: берем по очереди каждое место из нашего хранилища и рисуем его
for place in st.session_state.my_places:
    st.markdown(f"### {place['name']}")
    st.image(place['image'], use_container_width=True)
    st.caption(f"📍 {place['category']} | ⭐ {place['status']}")
    st.write(place['review'])
    st.divider()