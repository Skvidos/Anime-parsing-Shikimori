import requests
import pandas as pd
import json
import time
import os
import math

# URL API Shikimori для пакетного получения данных
url_template = "https://shikimori.one/api/animes?order=popularity&page={}&limit=50"

# Заголовки с User-Agent(нужно для работы api)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
}

# Функция для замены NaN значений на None(иначе json фарнинги дает)
def replace_nan(value):
    if isinstance(value, float) and math.isnan(value):
        return None  # или можно заменить на пустую строку ''
    return value

# Проверка существования и наполненности CSV файла
if os.path.exists('anime_data.csv') and os.path.getsize('anime_data.csv') > 0:
    # Загружаем уже сохраненные данные
    existing_data = pd.read_csv('anime_data.csv')
    anime_data = existing_data.to_dict('records')
    last_page = (len(existing_data) // 50) + 1
    print(f"Продолжаем с страницы {last_page}")
else:
    anime_data = []
    last_page = 1

# выбор страниц, так же есть у вас есть уже файл то он найдет последнию страницу и начнет с нее.
i = int(input("Введите количество страниц для на которых есть 50 аниме сразу(на 13.11.2024 это 439): "))
for page in range(last_page, i+1):
    url = url_template.format(page)
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            anime_list = response.json()
            
            for anime_info in anime_list:
                anime_data.append({
                    'id': replace_nan(anime_info.get('id')),
                    'name': replace_nan(anime_info.get('name')),
                    'russian': replace_nan(anime_info.get('russian', '')),
                    'url': replace_nan(anime_info.get('url')),
                    'kind': replace_nan(anime_info.get('kind')),
                    'score': replace_nan(anime_info.get('score')),
                    'status': replace_nan(anime_info.get('status')),
                    'episodes': replace_nan(anime_info.get('episodes')),
                    'episodes_aired': replace_nan(anime_info.get('episodes_aired', 0)),
                    'aired_on': replace_nan(anime_info.get('aired_on')),
                    'released_on': replace_nan(anime_info.get('released_on'))
                })
            print(f"Страница {page} успешно получена")
        
        else:
            print(f"Страница {page} - ошибка {response.status_code}")
        
    except Exception as e:
        print(f"Ошибка при обработке страницы {page}: {e}")

    # если выдаст ошибку проверте не является ли файл пустым, если да то удалите его новый сам создастся.
    # Сохранение данных в CSV
    if len(anime_data) > 0:
        df = pd.DataFrame(anime_data)
        df.to_csv('anime_data.csv', index=False)

        # Сохранение данных в JSON
        with open('anime_data.json', 'w', encoding='utf-8') as json_file:
            json.dump(anime_data, json_file, ensure_ascii=False, indent=4)

    # задержка что бы не грузить серв(не рекомендую ставить меньше 1)
    time.sleep(1)

print("Сбор данных завершен. Данные сохранены в 'anime_data.csv' и 'anime_data.json'")
