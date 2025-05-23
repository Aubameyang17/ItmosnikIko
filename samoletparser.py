import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from urllib3.exceptions import ReadTimeoutError
import traceback
import psycopg2
import requests
from bs4 import BeautifulSoup

from OpenRouterApi import summorize_text, maintheme_text

conn = psycopg2.connect(dbname="ItmosnikIko", host="127.0.0.1", user="Alex", password="alex")
cursor = conn.cursor()
month_to_number = {'января': "01", 'февраля': "02", 'марта': "03", 'апреля': "04", 'мая': "05", 'июня': "06",
                   'июля': "07", 'августа': "08", 'сентября': "09", 'октября': "10", 'ноября': "11", 'декабря': "12"}

def get_links(links, titles, times):
    options = uc.ChromeOptions()
    # options.headless = True
    # options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=options)
    try:
        driver.get("https://samolet.ru/news/")
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "r-news-list__news")))
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        cards = soup.find_all("a", class_="r-news-card")
        print(f"✅ Найдено новостей: {len(cards)}")

        for el in cards:
            try:
                header = el.find("div", class_="r-news-card__title")
                title = header.get('title')
                new_link = el.get("href")


                # Проверка наличия в БД
                cursor.execute("SELECT 1 FROM news WHERE origin_link = %s", (new_link,))
                if cursor.fetchone():
                    continue

                # Добавляем в списки
                links.append(new_link)
                titles.append(title)

                time_element = el.find('time').get_text().split()
                if len(time_element[0]) == 1:
                    data = f"{time_element[2]}-{month_to_number[time_element[1]]}-0{time_element[0]}"
                else:
                    data = f"{time_element[2]}-{month_to_number[time_element[1]]}-{time_element[0]}"
                print(data)
                times.append(data)

            except Exception as e:
                pass


    except Exception as e:
        print("❌ Ошибка при загрузке страницы:", e)

    finally:
        driver.quit()

    return links, titles, times


def chek_news(link):
    options = uc.ChromeOptions()
    # options.headless = True
    # options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=options)
    text = ""
    try:
        driver.get(link)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".r-news-detail__content.r-content.js-appear")))
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        content = soup.find_all('p')
        for el in content:
            if el.get_text(strip=True):
                text += el.get_text(strip=True) + " "

        # Обрабатываем текст через summarizer (если есть)
        if text:
            text = summorize_text(text)

    except ReadTimeoutError:
        print("⏱ Превышено время ожидания при загрузке:", link)
    except Exception:
        traceback.print_exc()
        print("⚠️ Ошибка при получении статьи:", link)
    finally:
        driver.quit()
    return text


links = []
titles = []
times = []
texts = []
count = 10
new_links, titles, times = get_links(links, titles, times)
zamena = ["Ключевые моменты:", "Основные моменты статьи:", "Краткая выжимка:", "Главные моменты:", " Суть статьи:",
          "Основные моменты:", "Основные пункты:", "Главные тезисы статьи:",
          "Вот краткая выжимка основных тезисов статьи:", "Основные тезисы статьи:", "Основные тезисы:"]


for link in range(count):
    text = chek_news(new_links[link])
    new_text = text
    for old in zamena:
        new_text = new_text.replace(old, "")

    themetext = maintheme_text(new_text)
    print(themetext.title())

    texts.append(new_text)


print("Len Links: ", len(links))
print("Len titles: ", len(titles))
print("Len times: ", len(times))
print("Len texts: ", len(texts))
for i in range(len(texts)):
    parametrs = (titles[i], times[i], texts[i], "", new_links[i])
    print(f"Link: {new_links[i]}\nTitle: {titles[i]}\nTime: {times[i]}\n Text: {texts[i]}\n\n")
    cursor.execute('INSERT INTO news (title, date, text, image_link, origin_link) '
                   'VALUES (%s, %s, %s, %s, %s)', parametrs)
    conn.commit()

cursor.close()
conn.close()