import requests
import pandas as pd
import json
import time
import os
import math

# === Настройки ===
BASE_URL = "https://shikimori.one"
LIST_URL_TEMPLATE = BASE_URL + "/api/animes?order=popularity&page={}&limit=50"
DETAIL_URL_TEMPLATE = BASE_URL + "/api/animes/{}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/85.0.4183.121 Safari/537.36"
}


def replace_nan(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def load_cache(filename="jp_cache.json"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache, filename="jp_cache.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


# === Основной код ===
if os.path.exists('anime_data.csv') and os.path.getsize('anime_data.csv') > 0:
    existing_data = pd.read_csv('anime_data.csv')
    anime_data = existing_data.to_dict('records')
    last_page = (len(existing_data) // 50) + 1
    print(f"Продолжаем с страницы {last_page}")
else:
    anime_data = []
    last_page = 1

jp_cache = load_cache()

i = int(input("Введите количество страниц (по 50 аниме на странице): "))

for page in range(last_page, i + 1):
    url = LIST_URL_TEMPLATE.format(page)
    print(f"\n🔹 Загружается страница {page}...")

    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(
                f"Ошибка {response.status_code} при загрузке страницы {page}")
            continue

        anime_list = response.json()

        for anime_info in anime_list:
            anime_id = anime_info.get("id")

            # --- Получаем японское название и описание ---
            if str(anime_id) in jp_cache:
                title_jp = jp_cache[str(anime_id)].get("title_jp")
                description = jp_cache[str(anime_id)].get("description")
                details_data = {}  # пустой словарь для студий
            else:
                details_url = DETAIL_URL_TEMPLATE.format(anime_id)
                details_response = requests.get(details_url, headers=HEADERS)

                if details_response.status_code == 200:
                    details_data = details_response.json()
                    title_jp = details_data.get("japanese")
                    description = details_data.get("description")
                else:
                    details_data = {}
                    title_jp = None
                    description = None

                # сохраняем в кэш
                jp_cache[str(anime_id)] = {
                    "title_jp": title_jp,
                    "description": description
                }
                save_cache(jp_cache)

                time.sleep(0.3)

            # --- Получаем название студии ---
            studios_list = anime_info.get("studios", [])
            if not studios_list:
                studios_list = details_data.get("studios", [])
            studio = ", ".join([s['name']
                               for s in studios_list]) if studios_list else None

            # --- Формируем запись ---
            anime_data.append({
                "id": replace_nan(anime_id),
                "title_en": replace_nan(anime_info.get("name")),
                "title": replace_nan(anime_info.get("russian", "")),
                "title_jp": replace_nan(title_jp),
                "description": replace_nan(description),
                "studio": replace_nan(studio),
                "image_url": f"{BASE_URL}{anime_info['image']['original']}" if anime_info.get("image") else None,
                "url": f"{BASE_URL}{anime_info.get('url')}",
                "type": replace_nan(anime_info.get("kind")),
                "score": replace_nan(anime_info.get("score")),
                "status": replace_nan(anime_info.get("status")),
                "episodes": replace_nan(anime_info.get("episodes")),
                "episodes_aired": replace_nan(anime_info.get("episodes_aired", 0)),
                "episodes_duration": replace_nan(anime_info.get("episodes_duration")),
                "aired_on": replace_nan(anime_info.get("aired_on")),
                "released_on": replace_nan(anime_info.get("released_on"))
            })

        print(f"✅ Страница {page} успешно обработана")

        # сохраняем прогресс
        df = pd.DataFrame(anime_data)
        df.to_csv("anime_data.csv", index=False)
        with open("anime_data.json", "w", encoding="utf-8") as json_file:
            json.dump(anime_data, json_file, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"⚠️ Ошибка при обработке страницы {page}: {e}")

    time.sleep(1)

print("\n🎉 Сбор данных завершён! Файлы сохранены: 'anime_data.csv' и 'anime_data.json'")
