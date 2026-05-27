import streamlit as st
import requests
import base64
import io
import time
import random
from PIL import Image
import json
from datetime import datetime
from pathlib import Path
import os

# Конфигурация страницы
st.set_page_config(
    page_title="Voice2Art | Голос в Искусство",
    page_icon=":art:",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Загрузка стилей
def load_css():
    with open("frontend/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()

# Инициализация сессии
if 'history' not in st.session_state:
    st.session_state.history = []
if 'total_generations' not in st.session_state:
    st.session_state.total_generations = 0
if 'api_url' not in st.session_state:
    st.session_state.api_url = os.getenv("API_URL_BACK", "http://localhost:8000")
if 'current_seed' not in st.session_state:
    st.session_state.current_seed = None


# Функции
def check_api_health():
    """Проверка доступности API"""
    try:
        response = requests.get(f"{st.session_state.api_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def display_image_from_path(image_path):
    """Отображение изображения по пути"""
    try:
        image = Image.open(image_path)
        st.image(image, use_container_width=True, caption="Ваше произведение искусства")

        # Кнопка скачивания
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="Скачать изображение",
            data=byte_im,
            file_name=f"voice2art_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            mime="image/png",
            use_container_width=True
        )
        return True
    except Exception as e:
        st.error(f"Ошибка загрузки изображения: {e}")
        return False


def add_to_history(result):
    """Добавление результата в историю"""
    st.session_state.history.insert(0, {
        "timestamp": datetime.now().isoformat(),
        "russian_text": result.get("russian_text", ""),
        "english_text": result.get("english_text", ""),
        "image_path": result.get("image_path", ""),
        "style": result.get("style_used", "realistic"),
        "generation_time": result.get("generation_time", 0)
    })
    st.session_state.total_generations += 1


# Боковая панель
with st.sidebar:
    # Заголовок
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px;'>
        <h1 style='color: white; margin-bottom: 0.5rem; font-size: 1.8rem;'>Voice2Art</h1>
        <p style='color: rgba(255,255,255,0.9); font-size: 0.9rem;'>Голос → Текст → Искусство</p>
    </div>
    """, unsafe_allow_html=True)

    # Статус API
    api_status = check_api_health()
    status_icon = "✓" if api_status else "✗"
    status_text = "API активен" if api_status else "API недоступен"
    st.markdown(f"### Статус системы: {status_icon} {status_text}")

    if not api_status:
        st.warning("Запустите бэкенд: uvicorn backend.main:app --reload")
        st.session_state.api_url = st.text_input(
            "URL API",
            value="http://localhost:8000",
            help="Введите адрес вашего FastAPI сервера"
        )

    st.divider()

    # Навигация
    page = st.radio(
        "Режим работы",
        ["Голос в картину", "Текст в картину", "Галерея", "Настройки"],
        label_visibility="collapsed"
    )

    st.divider()

    # Статистика
    st.markdown("### Статистика")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Всего создано", st.session_state.total_generations)
    with col2:
        st.metric("В истории", len(st.session_state.history))

    st.divider()
    st.caption("© 2024 Voice2Art | v2.0")

# Основное содержимое в зависимости от страницы
if page == "Голос в картину":
    st.markdown("""
    <div style='text-align: center; margin-bottom: 3rem;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 1rem; color: #6a11cb;'>Говори, и мы нарисуем</h1>
        <p style='font-size: 1.2rem; color: #666;'>Запишите голосовое описание → получите уникальное изображение</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Шаг 1: Запишите описание")

        # Варианты загрузки
        upload_option = st.radio(
            "Выберите способ:",
            ["Загрузить аудиофайл", "Использовать пример"]
        )

        audio_file = None

        if upload_option == "Загрузить аудиофайл":
            audio_file = st.file_uploader(
                "Перетащите файл или нажмите для выбора",
                type=["wav", "mp3", "m4a", "ogg", "flac"],
                help="Поддерживаются форматы: WAV, MP3, M4A, OGG, FLAC",
                label_visibility="collapsed"
            )

            if audio_file:
                st.audio(audio_file, format=audio_file.type)

        elif upload_option == "Использовать пример":
            example = st.selectbox(
                "Выберите пример описания:",
                [
                    "Космический кот в скафандре летит на ракете",
                    "Замок из облаков на фоне заката",
                    "Робот-садовник сажает цветы на Марсе",
                    "Подводный город с сияющими кораллами"
                ]
            )

            if st.button("Сгенерировать по примеру", use_container_width=True):
                st.session_state.text_input = example

        # Настройки генерации - ВЫНЕСЕМ ИЗ expander В ВИДИМУЮ ОБЛАСТЬ
        st.markdown("### Настройки генерации")

        col_settings1, col_settings2 = st.columns(2)
        with col_settings1:
            style = st.selectbox(
                "Стиль изображения",
                ["realistic", "anime", "painting", "digital", "fantasy"],
                format_func=lambda x: {
                    "realistic": "Реализм",
                    "anime": "Аниме",
                    "painting": "Картина",
                    "digital": "Цифровое искусство",
                    "fantasy": "Фэнтези"
                }[x],
                key="audio_style"
            )
            num_steps = st.slider("Качество", 1, 10, 4,
                                  help="Больше шагов = лучше качество, но дольше генерация",
                                  key="audio_steps")

        with col_settings2:
            guidance_scale = st.slider("Контроль генерации", 1.0, 20.0, 7.5, 0.5,
                                       key="audio_guidance")

            # Seed с кнопкой рандомизации
            st.markdown("**Seed (для воспроизводимости)**")
            seed_col1, seed_col2 = st.columns([3, 1])
            with seed_col1:
                seed = st.number_input("Введите seed или оставьте пустым для случайного",
                                       value=st.session_state.current_seed if st.session_state.current_seed else None,
                                       placeholder="Случайный",
                                       help="Оставьте пустым для случайной генерации",
                                       label_visibility="collapsed",
                                       key="audio_seed_input")
            with seed_col2:
                if st.button("Случайный", use_container_width=True, key="random_seed_audio"):
                    new_seed = random.randint(0, 2 ** 32 - 1)
                    st.session_state.current_seed = new_seed
                    st.rerun()

    with col2:
        st.markdown("### Шаг 2: Результат")

        # Место для результата
        result_placeholder = st.empty()
        status_placeholder = st.empty()

        # Кнопка генерации
        if st.button("Начать генерацию",
                     type="primary",
                     use_container_width=True,
                     disabled=not api_status,
                     key="generate_audio"):

            if audio_file or 'text_input' in st.session_state:
                with status_placeholder.container():
                    with st.spinner("Обработка..."):
                        # Прогресс бар
                        progress_bar = st.progress(0)

                        try:
                            # Подготовка seed
                            current_seed = seed if seed is not None else random.randint(0, 2 ** 32 - 1)

                            # Шаг 1: Отправка запроса
                            progress_bar.progress(25)

                            if audio_file:
                                # ПЕРЕДАЕМ ВСЕ ПАРАМЕТРЫ ЧЕРЕЗ FormData
                                files = {"file": audio_file}
                                data = {
                                    "style": style,
                                    "num_steps": num_steps,
                                    "guidance_scale": guidance_scale,
                                    "seed": str(current_seed),
                                    "negative_prompt": ""
                                }

                                response = requests.post(
                                    f"{st.session_state.api_url}/generate",
                                    files=files,
                                    data=data,
                                    timeout=120
                                )
                            else:
                                # Текстовый режим с примером
                                data = {
                                    "prompt": st.session_state.text_input,
                                    "style": style,
                                    "num_steps": num_steps,
                                    "guidance_scale": guidance_scale,
                                    "seed": str(current_seed)
                                }

                                response = requests.post(
                                    f"{st.session_state.api_url}/generate",
                                    data=data,
                                    timeout=120
                                )

                            progress_bar.progress(50)

                            if response.status_code == 200:
                                result = response.json()
                                progress_bar.progress(75)

                                # Сохраняем seed для повторного использования
                                st.session_state.current_seed = current_seed

                                # Добавляем в историю
                                add_to_history(result)

                                # Отображаем результат
                                progress_bar.progress(100)
                                time.sleep(0.5)
                                progress_bar.empty()

                                with result_placeholder.container():
                                    st.success("Изображение успешно создано!")

                                    # Информация о генерации
                                    info_col1, info_col2 = st.columns(2)
                                    with info_col1:
                                        st.markdown("#### Параметры")
                                        st.info(f"Стиль: {result.get('style_used', 'realistic')}")
                                        st.info(f"Seed: {current_seed}")
                                        st.info(f"Время: {result.get('generation_time', 0)} сек")

                                    with info_col2:
                                        st.markdown("#### Текст")
                                        st.text_area("Распознано:", result["russian_text"], height=100,
                                                     key="ru_result1")
                                        st.text_area("Перевод:", result["english_text"], height=100, key="en_result1")

                                    # Отображаем изображение
                                    if display_image_from_path(result["image_path"]):
                                        # Дополнительные действия
                                        action_col1, action_col2, action_col3 = st.columns(3)
                                        with action_col1:
                                            if st.button("В избранное", use_container_width=True, key="fav1"):
                                                st.success("Добавлено в избранное!")

                                        with action_col2:
                                            if st.button("Новая генерация", use_container_width=True,
                                                         key="regenerate1"):
                                                st.session_state.current_seed = None
                                                st.rerun()

                                        with action_col3:
                                            if st.button("Поделиться", use_container_width=True, key="share1"):
                                                st.info("Функция шаринга в разработке")

                            else:
                                progress_bar.empty()
                                st.error(f"Ошибка API: {response.status_code}")
                                if response.text:
                                    st.error(f"Детали: {response.text[:200]}")

                        except requests.exceptions.Timeout:
                            progress_bar.empty()
                            st.error("Таймаут. Попробуйте еще раз или уменьшите качество.")
                        except Exception as e:
                            progress_bar.empty()
                            st.error(f"Ошибка: {str(e)}")
            else:
                st.warning("Пожалуйста, загрузите аудио или выберите пример")

elif page == "Текст в картину":
    st.markdown("""
    <div style='text-align: center; margin-bottom: 3rem;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 1rem; color: #00b09b;'>Опиши словами</h1>
        <p style='font-size: 1.2rem; color: #666;'>Напишите описание на русском или английском</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Русский текст")
        russian_text = st.text_area(
            "Введите описание на русском:",
            placeholder="Например: 'Космический кот в скафандре летит на ракете среди звезд'",
            height=150,
            key="ru_text"
        )

        st.markdown("### Или английский текст")
        english_text = st.text_area(
            "Or enter English text:",
            placeholder="Example: 'A majestic dragon flying over ancient mountains at sunset, digital art'",
            height=150,
            key="en_text"
        )

        # Настройки
        st.markdown("### Настройки стиля")
        style = st.selectbox(
            "Стиль изображения",
            ["realistic", "anime", "painting", "digital", "fantasy"],
            format_func=lambda x: {
                "realistic": "Фотореализм",
                "anime": "Аниме стиль",
                "painting": "Картина маслом",
                "digital": "Цифровое искусство",
                "fantasy": "Фэнтези"
            }[x],
            key="text_style"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            num_steps = st.slider("Шаги генерации", 1, 10, 6, key="text_steps")

            # Seed для текстового режима
            st.markdown("**Seed**")
            seed_col1, seed_col2 = st.columns([3, 1])
            with seed_col1:
                seed = st.number_input("Введите seed или оставьте пустым для случайного",
                                       value=st.session_state.current_seed if st.session_state.current_seed else None,
                                       placeholder="Случайный",
                                       label_visibility="collapsed",
                                       key="text_seed_input")
            with seed_col2:
                if st.button("Случайный", use_container_width=True, key="random_seed_text"):
                    new_seed = random.randint(0, 2 ** 32 - 1)
                    st.session_state.current_seed = new_seed
                    st.rerun()

        with col_b:
            guidance_scale = st.slider("Guidance scale", 1.0, 20.0, 7.5, 0.5, key="text_guidance")
            negative_prompt = st.text_input("Negative prompt",
                                            placeholder="Чего избегать в изображении...",
                                            key="neg_prompt")

    with col2:
        st.markdown("### Результат")

        generate_text = st.button(
            "Создать изображение из текста",
            type="primary",
            use_container_width=True,
            disabled=not (russian_text or english_text) or not api_status,
            key="generate_text"
        )

        if generate_text:
            with st.spinner("Генерация изображения..."):
                try:
                    # Подготовка данных
                    current_seed = seed if seed is not None else random.randint(0, 2 ** 32 - 1)

                    data = {
                        "prompt": russian_text if russian_text else english_text,
                        "style": style,
                        "num_steps": num_steps,
                        "guidance_scale": guidance_scale,
                        "seed": str(current_seed)
                    }

                    if negative_prompt:
                        data["negative_prompt"] = negative_prompt

                    response = requests.post(
                        f"{st.session_state.api_url}/generate",
                        data=data,
                        timeout=120
                    )

                    if response.status_code == 200:
                        result = response.json()

                        # Сохраняем seed
                        st.session_state.current_seed = current_seed

                        # Добавляем в историю
                        add_to_history(result)

                        st.success("Изображение создано!")

                        # Информация
                        info_col1, info_col2 = st.columns(2)
                        with info_col1:
                            st.markdown("#### Детали")
                            st.info(f"Стиль: {style}")
                            st.info(f"Seed: {current_seed}")
                            st.info(f"Шаги: {num_steps}")

                        with info_col2:
                            st.markdown("#### Текст")
                            if english_text:
                                st.text_area("Промпт:", english_text, height=100, key="prompt_display")
                            else:
                                st.text_area("Перевод:", result.get('english_text', ''), height=100,
                                             key="translation_display")

                        # Показываем изображение
                        display_image_from_path(result["image_path"])

                        # Дополнительные действия
                        action_col1, action_col2, action_col3 = st.columns(3)
                        with action_col1:
                            if st.button("В избранное", use_container_width=True, key="fav2"):
                                st.success("Добавлено в избранное!")

                        with action_col2:
                            if st.button("Новая генерация", use_container_width=True, key="regenerate2"):
                                st.session_state.current_seed = None
                                st.rerun()

                        with action_col3:
                            if st.button("Поделиться", use_container_width=True, key="share2"):
                                st.info("Функция шаринга в разработке")

                    else:
                        st.error(f"Ошибка: {response.status_code}")
                        if response.text:
                            st.error(f"Детали: {response.text[:200]}")

                except requests.exceptions.Timeout:
                    st.error("Таймаут. Попробуйте еще раз или уменьшите количество шагов.")
                except Exception as e:
                    st.error(f"Ошибка генерации: {str(e)}")

elif page == "Галерея":
    st.markdown("""
    <div style='text-align: center; margin-bottom: 3rem;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 1rem; color: #FF416C;'>Ваша галерея</h1>
        <p style='font-size: 1.2rem; color: #666;'>История созданных изображений</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.history:
        st.info("Ваша галерея пуста. Создайте первое изображение!")
    else:
        # Фильтры
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        with col_filter1:
            filter_style = st.selectbox("Фильтр по стилю", ["Все"] +
                                        list(set([h["style"] for h in st.session_state.history])),
                                        key="filter_style")
        with col_filter2:
            sort_by = st.selectbox("Сортировка", ["Новые сначала", "Старые сначала"],
                                   key="sort_by")
        with col_filter3:
            items_per_page = st.slider("Изображений на странице", 3, 12, 6, key="items_per_page")

        # Фильтрация и сортировка
        filtered_history = st.session_state.history
        if filter_style != "Все":
            filtered_history = [h for h in filtered_history if h["style"] == filter_style]

        if sort_by == "Старые сначала":
            filtered_history = list(reversed(filtered_history))

        # Пагинация
        total_pages = max(1, (len(filtered_history) + items_per_page - 1) // items_per_page)
        page_number = st.number_input("Страница", 1, total_pages, 1, label_visibility="collapsed",
                                      key="page_number")

        start_idx = (page_number - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(filtered_history))

        # Отображение галереи
        st.markdown(f"### Показано {start_idx + 1}-{end_idx} из {len(filtered_history)} работ")

        items = filtered_history[start_idx:end_idx]
        cols_per_row = 3
        rows = (len(items) + cols_per_row - 1) // cols_per_row

        for row in range(rows):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                item_idx = row * cols_per_row + col_idx
                if item_idx < len(items):
                    item = items[item_idx]
                    with cols[col_idx]:
                        # Карточка изображения
                        with st.container():
                            st.markdown(f"""
                            <div style='
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                border-radius: 10px;
                                padding: 1rem;
                                margin-bottom: 1rem;
                                color: white;
                            '>
                                <p style='font-size: 0.9rem; margin-bottom: 0.5rem;'>{item["russian_text"][:50]}...</p>
                                <div style='display: flex; justify-content: space-between; font-size: 0.8rem;'>
                                    <span>Стиль: {item["style"]}</span>
                                    <span>Время: {item["generation_time"]}с</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            # Показ изображения
                            try:
                                image = Image.open(item["image_path"])
                                st.image(image, use_container_width=True)

                                # Действия
                                col_act1, col_act2 = st.columns(2)
                                with col_act1:
                                    if st.button("Открыть", key=f"view_{item_idx}"):
                                        st.session_state.current_image = item
                                        st.rerun()
                                with col_act2:
                                    if st.button("Удалить", key=f"del_{item_idx}"):
                                        st.session_state.history.remove(item)
                                        st.success("Удалено!")
                                        st.rerun()
                            except:
                                st.warning("Изображение не найдено")

        # Навигация по страницам
        if total_pages > 1:
            col_prev, col_page, col_next = st.columns([1, 2, 1])
            with col_prev:
                if page_number > 1 and st.button("Предыдущая", key="prev_page"):
                    st.session_state.gallery_page = page_number - 1
                    st.rerun()
            with col_page:
                st.markdown(f"**Страница {page_number} из {total_pages}**")
            with col_next:
                if page_number < total_pages and st.button("Следующая", key="next_page"):
                    st.session_state.gallery_page = page_number + 1
                    st.rerun()

elif page == "Настройки":
    st.markdown("""
    <div style='text-align: center; margin-bottom: 3rem;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 1rem; color: #8E2DE2;'>Настройки системы</h1>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["API", "Генерация", "Система"])

    with tab1:
        st.markdown("### Настройки API")

        new_api_url = st.text_input(
            "URL API сервера",
            value=st.session_state.api_url,
            help="Адрес вашего FastAPI бэкенда",
            key="api_url_input"
        )

        if new_api_url != st.session_state.api_url:
            st.session_state.api_url = new_api_url
            st.success("URL обновлен!")

        # Тест соединения
        if st.button("Проверить соединение", use_container_width=True, key="test_connection"):
            if check_api_health():
                st.success("Соединение с API установлено!")
            else:
                st.error("Не удалось подключиться к API")

        st.divider()
        st.markdown("### История API запросов")
        if st.button("Очистить историю сессии", use_container_width=True, key="clear_history"):
            st.session_state.history = []
            st.session_state.total_generations = 0
            st.success("История очищена!")

    with tab2:
        st.markdown("### Параметры генерации по умолчанию")

        col1, col2 = st.columns(2)
        with col1:
            default_style = st.selectbox(
                "Стиль по умолчанию",
                ["realistic", "anime", "painting", "digital", "fantasy"],
                index=0,
                key="default_style"
            )
            default_steps = st.slider("Шаги по умолчанию", 1, 10, 4, key="default_steps")

        with col2:
            default_guidance = st.slider("Guidance scale по умолчанию", 1.0, 20.0, 7.5, 0.5, key="default_guidance")
            auto_save = st.checkbox("Автосохранение всех результатов", value=True, key="auto_save")

        if st.button("Сохранить настройки", use_container_width=True, key="save_settings"):
            st.success("Настройки сохранены!")

    with tab3:
        st.markdown("### Информация о системе")

        # Информация о сессии
        st.json({
            "total_generations": st.session_state.total_generations,
            "history_size": len(st.session_state.history),
            "api_url": st.session_state.api_url,
            "api_status": "online" if check_api_health() else "offline"
        })

        st.divider()
        st.markdown("### Экспорт данных")

        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            if st.button("Экспорт истории", use_container_width=True, key="export_history"):
                # Экспорт истории в JSON
                history_data = {
                    "export_date": datetime.now().isoformat(),
                    "total_items": len(st.session_state.history),
                    "history": st.session_state.history
                }

                st.download_button(
                    label="Скачать JSON",
                    data=json.dumps(history_data, indent=2, ensure_ascii=False),
                    file_name=f"voice2art_history_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True,
                    key="download_json"
                )

# Футер
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><b>Voice2Art v2.0</b> | Превратите голос в искусство с помощью ИИ</p>
    <p style='font-size: 0.9rem;'>
        Powered by FastAPI • Streamlit • Whisper • FLUX.1 • Transformers
    </p>
</div>
""", unsafe_allow_html=True)

# Запуск бэкенда по требованию
if not check_api_health():
    st.sidebar.warning("""
    **Для запуска бэкенда выполните:**
    ```
    cd voice2art
    uvicorn backend.main:app --reload --port 8000
    ```
    """)