import json
from datetime import datetime

# Загружаем JSON-файл
with open('anime_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Функция для преобразования даты
def parse_date(item):
    date_str = item.get('aired_on')
    try:
        return datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.max
    except ValueError:
        return datetime.max

# Сортировка по aired_on
sorted_data = sorted(data, key=parse_date)

# 🔹 Перенумерация ID (по порядку после сортировки)
for i, item in enumerate(sorted_data, start=1):
    item['id'] = i

# Сохранение результата
with open('anime_data_sorted.json', 'w', encoding='utf-8') as f:
    json.dump(sorted_data, f, ensure_ascii=False, indent=4)

print("✅ Отсортировано по 'aired_on' и id перенумерованы по порядку.")
