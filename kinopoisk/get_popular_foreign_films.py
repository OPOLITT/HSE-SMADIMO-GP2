from seleniumbase import SB
import random

browsers = ['chrome', 'brave']

films = []
n=5

for page in range(1,n+1):

    url = f'https://www.kinopoisk.ru/lists/movies/?b=foreign&page={page}'

    try:
        with SB(uc=True,
                browser=browsers[random.randint(0,1)],
                mobile=True,
                test=True,
                locale="ru") as sb:
            sb.uc_open_with_cdp_mode(url)

            # sb.uc_open_with_reconnect(url, reconnect_time=5)
            
            # не работает
            # try:
            #     sb.uc_gui_handle_captcha()
            # except:
            #     sb.sleep(3)

            sb.wait_for_element('[data-tid="4502216a"]', timeout=15)

            # имитируем действия человека
            sb.sleep(random.randint(1,3))
            sb.execute_script(f'window.scroll(0,{random.randint(0,10000)})')
            sb.scroll_to_bottom()
            sb.sleep(random.randint(1,3))

            titles = sb.find_elements('[data-tid="4502216a"]')
            ratings = sb.find_elements('span[aria-hidden="true"][class*="styles_kinopoiskValue"]')

            films.extend(list(zip([title.text for title in titles],
                                  [rating.text for rating in ratings])))

            with open('kinopoisk/results/all_films.txt', 'a', encoding='utf-8') as f:
                for title, rating in films:
                    f.write(f'{title}@@{rating}\n')
            
            print(f'Page {page}/{n}')
            sb.sleep(random.randint(1,3))
    except Exception as e:
        print(f'ERROR: {e}')