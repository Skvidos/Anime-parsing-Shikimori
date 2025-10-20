import json
import mysql.connector

# Подключение к MySQL
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="admin",
    database="mirimori"
)
cursor = conn.cursor()

# Загрузка данных из JSON
with open("anime_data_sorted.json", "r", encoding="utf-8") as f:
    data = json.load(f)


def to_str(value):
    if isinstance(value, list):
        return ', '.join(map(str, value))
    return str(value) if value is not None else ''


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_date(value):
    if value and isinstance(value, str) and len(value) >= 8:
        return value
    return None


def normalize_type(anime_type):
    if not anime_type:
        return "TV"
    anime_type = anime_type.lower()
    if "tv" in anime_type:
        return "TV"
    elif "movie" in anime_type or "film" in anime_type:
        return "Movie"
    elif "ova" in anime_type:
        return "OVA"
    elif "ona" in anime_type:
        return "ONA"
    elif "special" in anime_type:
        return "Special"
    else:
        return "TV"


confirm = input(
    "Очистить таблицу anime перед импортом? (y/n): ").strip().lower()
if confirm == 'y':
    cursor.execute("DELETE FROM anime;")
    conn.commit()
    print("🧹 Таблица anime очищена.\n")

for anime in data:
    cursor.execute('''
        INSERT INTO anime
        (title, title_jp, title_en, alt_titles, description, poster, type, episodes_total, episode_duration, release_date, studio, source, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        to_str(anime.get('title')),
        to_str(anime.get('title_jp')),
        to_str(anime.get('title_en')),
        to_str(anime.get('alt_titles')),
        to_str(anime.get('description')),
        to_str(anime.get('image_url')),
        normalize_type(anime.get('type')),
        to_int(anime.get('episodes')),
        to_int(anime.get('episode_duration')),
        to_date(anime.get('released_on')),
        to_str(anime.get('studio')),
        to_str(anime.get('source')),
        to_str(anime.get('status'))
    ))

conn.commit()
cursor.close()
conn.close()

print("✅ Импорт завершён успешно!")
