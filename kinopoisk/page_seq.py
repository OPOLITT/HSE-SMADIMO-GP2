from seleniumbase import SB
import random
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='kinopoisk/kinopoisk_logs.txt',
                    encoding='utf-8',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s')

browsers = ['chrome', 'brave']

films = []

n=50
page=1
success=0

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

        sb.wait_for_element('[data-tid="4502216a"]', timeout=15)

        # имитируем действия человека
        sb.sleep(random.randint(1,3))
        sb.execute_script(f'window.scroll(0,{random.randint(0,10000)})')
        sb.scroll_to_bottom()
        sb.sleep(random.randint(1,3))

        try:
            # названия на русском
            titles = [el.text for el in sb.find_elements('[data-tid="4502216a"]')]
            # средние оценки фильмов и сериалов
            ratings = [el.text for el in sb.find_elements('span[aria-hidden="true"][class*="styles_kinopoiskValue"]')]
            # количество оценок на кинопоиске
            vote_count = [el.text for el in sb.find_elements('span[aria-hidden="true"][class*="styles_kinopoiskCount__b6MEL"]')]
            # названия на английском
            english_name = [el.text for el in sb.find_elements('[class="desktop-list-main-info_secondaryTitle__e5NG5"]')]
            # фильмы: год выпуска + продолжительность (формат: ч. мин.); сериалы: года выпуска (например, 2017-2020)
            duration = [el.text for el in sb.find_elements('[class="desktop-list-main-info_secondaryText__gwhDJ"]')]
            # страна выпуска + жанр + режиссер (например, США • фантастика  Режиссёр: Дени Вильнёв)
            # а также под таким же тегом найдется: актеры главных ролей (например, В ролях: Тимоти Шаламе, Ребекка Фергюсон)
            description = [el.text for el in sb.find_elements('[class="desktop-list-main-info_truncatedText__DAuwA"]')]
        except Exception as e:
            logger.error(f'Ошибка получения информации с сайта: {e}')

        try:
            with open(f'kinopoisk/results/pages/page_{page}.txt', 'w', encoding='utf-8') as f:
                for ind in range(len(titles)):
                    f.write(f'{titles[ind]}@@{ratings[ind]}@@{vote_count[ind]}@@{english_name[ind]}@@{duration[ind]}@@{description[ind*2]}@@{description[ind*2+1]}\n')
            success+=1
        except Exception as e:
            logger.error(f'Ошибка сохранения в файл: {e}')

        print(f'Page {page}/{n}')
        sb.sleep(random.randint(1,3))

        page+=1
        try:
            sb.click(f'a[href*="page={page}"]')
        except Exception as e:
            logger.error(f'Ошибка нажатия кнопки перехода на новую страницу: {e}')

logger.info('\n\n===КОНЕЦ РАБОТЫ===')
logger.info(f'Успешно обработано страниц = {success}')
logger.info(f'Неуспешно обработано страниц = {n-success}')