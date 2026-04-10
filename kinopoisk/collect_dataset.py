import re
import pandas as pd
import logging
import time
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)
if os.getenv('IS_LOGGING', 'true').lower() == 'true':
    logging.basicConfig(filename='kinopoisk_dataset_logs.txt',
                        encoding='utf-8',
                        level=os.getenv('LOGGING_LEVEL', 'INFO').upper(),
                        format='%(asctime)s %(message)s')
else:
    logger.disabled = True

data_dir = 'results/pages'

columns=['russian_title',
         'english_title',
         'rating',
         'vote_count',
         'genre',
         'director',
         'is_film',
         'start_year',
         'end_year',
         'duration_minutes',
         'country',
         'actors']

data_list = []
success_films=0
failure_films=0
success_pages=0
start_time = time.time()

logger.info('===НАЧАЛО РАБОТЫ===')

for page_number in range(1, 1001):
    logger.info(f'==Обработка страницы {page_number}/1000...')
    with (open(data_dir + f'/page_{page_number}.txt', 'r', encoding='utf-8') as f):
        for film in f.readlines():
            elements = film.strip().split('@@')
            row = {}

            try:
                curr_success_films = 0
                film_title = elements[0].strip()
                logger.info(f'Обработка фильма: {film_title}')

                row['russian_title'] = film_title
                row['rating'] = float(elements[1]) if elements[1] else None
                row['vote_count'] = None if not elements[2] else \
                    int(elements[2][:-1].replace(' ', '')) * 1000 if elements[2][-1] == 'K' \
                    else int(elements[2].replace(' ', ''))
                row['english_title'] = elements[3].strip() if elements[3] else None

                years = elements[4].split(', ')
                if len(years) == 3:
                    row['is_film'] = True
                    row['start_year'] = int(years[1])
                    hours = re.search(r'(\d+)\s+ч', years[2])
                    minutes = re.search(r'(\d+)\s+мин', years[2])
                    row['duration_minutes'] = (int(hours.group(1)) * 60 if hours else 0) + \
                                              (int(minutes.group(1)) if minutes else 0)
                elif len(years) == 2:
                    row['is_film'] = False
                    start_year = re.search(r'(\d+)–', years[1])
                    end_year = re.search(r'(\d+)–', years[1])
                    row['start_year'] = int(start_year.group(1)) if start_year else None
                    row['end_year'] = int(end_year.group(1)) if end_year else None

                parts = elements[5].replace('  ', ' • ').split(' • ')
                row['country'] = parts[0] if len(parts) > 0 else None
                row['genre'] = parts[1] if len(parts) > 1 else None
                row['director'] = parts[2].replace('Режиссёр: ', '') if len(parts) > 2 else None

                row['actors'] = '|'.join(elements[6].replace('В ролях: ','').split(', '))

                curr_success_films += 1
                success_films += 1

                data_list.append(row)
                logger.info(f'Успешная обработка фильма: {film_title}')

            except Exception as e:
                logger.error(f'Ошибка при обработке: {e}')
                failure_films += 1
        if curr_success_films>0:
            success_pages += 1

logger.info('Сохраняем датасет в csv файл')
pd.DataFrame(data_list, columns=columns).to_csv('kinopoisk.csv', encoding='utf-8', index=False)
logger.info('Датасет сохранен в файл kinopoisk.csv')

logger.info('\n\n===КОНЕЦ РАБОТЫ===')
logger.info(f'Успешно обработано страниц = {success_pages}')
logger.info(f'Неуспешно обработано страниц = {1000-success_pages}')
logger.info(f'Успешно обработано фильмов = {success_films}')
logger.info(f'Неуспешно обработано фильмов = {failure_films}')
logger.info(f'Время выполнения = {round(time.time()-start_time, 3)} сек')
