from seleniumbase import SB
from bs4 import BeautifulSoup
import random
import logging
from time import time
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)
if os.getenv('IS_LOGGING', 'true').lower() == 'true':
    logging.basicConfig(filename='kinopoisk/kinopoisk_logs.txt',
                        encoding='utf-8',
                        level=os.getenv('LOGGING_LEVEL', 'INFO').upper(),
                        format='%(asctime)s %(message)s')
else:
    logger.disabled = True

browsers = ['chrome', 'brave']

films = []
page_time_processing = []

n=1000
page=1
success_films=0
failure_films=0
success_pages=0

start_time = time()
with SB(uc=True,
                browser=browsers[random.randint(0,1)],
                mobile=True,
                test=True,
                locale="ru") as sb:
    
    logger.info('===НАЧАЛО РАБОТЫ===')
    
    url = f'https://www.kinopoisk.ru/lists/movies/?b=foreign&page=1'
    sb.uc_open_with_cdp_mode(url)

    while page<=n:
        logger.info(f'Обработка страницы {page}/{n}...')

        page_time_start = time()

        sb.wait_for_element('[data-tid="4502216a"]', timeout=15)

        # имитируем действия человека
        sb.sleep(random.randint(1,3))
        sb.execute_script(f'window.scroll(0,{random.randint(0,10000)})')
        sb.scroll_to_bottom()
        sb.sleep(random.randint(1,3))

        with open(f'kinopoisk/results/pages/page_{page}.txt', 'w', encoding='utf-8') as f:
            # итерируемся по контейнерам каждого фильма
            for container in sb.find_elements('[class=styles_upper__E4_MJ]'):
                try:
                    soup = BeautifulSoup(container.get_html(), 'html.parser')
                    curr_success_films=0
                    # название на русском
                    tmp = soup.select_one('[data-tid="4502216a"]')
                    title = tmp.text if tmp else ''
                    if not title:
                        continue

                    # средняя оценка фильмов и сериалов
                    tmp = soup.select_one('span[aria-hidden="true"][class*="styles_kinopoiskValue"]')
                    rating = tmp.text if tmp else ''
                    # количество оценок на кинопоиске
                    tmp = soup.select_one('span[aria-hidden="true"][class*="styles_kinopoiskCount__b6MEL"]')
                    vote_count = tmp.text if tmp else ''
                    # название на английском
                    tmp = soup.select_one('[class="desktop-list-main-info_secondaryTitle__e5NG5"]')
                    english_name = tmp.text if tmp else ''
                    # фильмы: год выпуска + продолжительность (формат: ч. мин.); сериалы: года выпуска (например, 2017-2020)
                    tmp = soup.select_one('[class="desktop-list-main-info_secondaryText__gwhDJ"]')
                    duration = tmp.text if tmp else ''
                    # страна выпуска + жанр + режиссер (например, США • фантастика  Режиссёр: Дени Вильнёв)
                    # а также под таким же тегом найдется: актеры главных ролей (например, В ролях: Тимоти Шаламе, Ребекка Фергюсон)
                    tmp = soup.select('[class="desktop-list-main-info_truncatedText__DAuwA"]')
                    description = [el.text for el in tmp] if tmp else ['','']


                    f.write(f"{title}@@{rating}@@{vote_count}@@{english_name}@@{duration}@@{description[0]}@@{description[1]}\n")
                    curr_success_films+=1
                    success_films+=1

                except Exception as e:
                    failure_films+=1
                    logger.error(f'Ошибка получения информации с сайта: {e}')
            
            if curr_success_films>0: success_pages+=1

        print(f'Page {page}/{n}')
        sb.sleep(random.randint(1,3))

        page_time_processing.append(round(time()-page_time_start,3))

        page+=1
        try:
            sb.click(f'a[href*="page={page}"]')
        except Exception as e:
            logger.error(f'Ошибка нажатия кнопки перехода на новую страницу: {e}')
            break

logger.info('\n\n===КОНЕЦ РАБОТЫ===')
logger.info(f'Успешно обработано страниц = {success_pages}')
logger.info(f'Неуспешно обработано страниц = {n-success_pages}')
logger.info(f'Успешно обработано фильмов = {success_films}')
logger.info(f'Неуспешно обработано фильмов = {failure_films}')
logger.info(f'Время выполнения = {round((time()-start_time)/60, 3)} мин')
logger.info(f'Среднее время на страницу = {round(sum(page_time_processing)/len(page_time_processing), 2)} сек')