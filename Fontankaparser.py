import re
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

def get_links(links, titles, times, imgs):
    try:
        url = "https://www.fontanka.ru/realty/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        cards = soup.find_all("div", class_=re.compile("wrap_"))

        # подключение к БД

        for el in cards:
            try:
                header = el.find("a", class_=re.compile("header_"))
                new_link = header.get("href")

                """# Проверка наличия в БД
                cursor.execute("SELECT 1 FROM news WHERE origin_link = %s", (new_link,))
                if cursor.fetchone():
                    continue"""

                # Добавляем в списки
                links.append(new_link)
                titles.append(header.get_text(strip=True))

                time_element = el.find("div", class_=re.compile("cell_")).get_text(strip=True).split()
                if len(time_element[0]) == 1:
                    date = f"{time_element[2].replace(',', '')}-{month_to_number[time_element[1].replace(',', '')]}-0{time_element[0]}"
                else:
                    date = f"{time_element[2].replace(',', '')}-{month_to_number[time_element[1].replace(',', '')]}-{time_element[0]}"
                times.append(date if date else "")

                img_tag = el.find("img")
                img_url = img_tag.get("src") if img_tag else ""
                imgs.append(img_url)

                #print(f"🆕 Найдена новая статья: {new_link}")
            except Exception as e:
                pass


    except Exception as e:
        print("❌ Ошибка при загрузке страницы:", e)

    return links, titles, times, imgs


def chek_news(link):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    text = ""

    try:
        response = requests.get(link, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        if 'longreads' in link:
            # Ищем все элементы с классом "tn-atom"
            content = soup.find_all(class_="tn-atom")
            for el in content:
                if el.get_text(strip=True):
                    text += el.get_text(strip=True) + " "
        else:
            # Обычная статья
            article = soup.find(class_=re.compile("articleContent_"))
            if article:
                text = article.get_text(strip=True)

        # Обрабатываем текст через summarizer (если есть)
        if text:
            print(text)
            text = summorize_text(text)

    except ReadTimeoutError:
        print("⏱ Превышено время ожидания при загрузке:", link)
    except Exception:
        traceback.print_exc()
        print("⚠️ Ошибка при получении статьи:", link)

    return text


links = []
titles = []
times = []
imgs = []
texts = []
count = 10
new_links, titles, times, imgs = get_links(links, titles, times, imgs)
zamena = ["Ключевые моменты:", "Основные моменты статьи:", "Краткая выжимка:", "Главные моменты:", " Суть статьи:",
          "Основные моменты:", "Основные пункты:", "Главные тезисы статьи:",
          "Вот краткая выжимка основных тезисов статьи:", "Основные тезисы статьи:", "Основные тезисы:"]

for link in range(10):
    text = chek_news(new_links[link])
    new_text = text
    for old in zamena:
        new_text = new_text.replace(old, "")

    #themetext = maintheme_text(new_text)
    #print(themetext.title())
    texts.append(new_text)


print("Len Links: ", len(links))
print("Len titles: ", len(titles))
print("Len times: ", len(times))
print("Len imgs: ", len(imgs))
print("Len texts: ", len(texts))
check_title = []
for i in range(len(texts)):
    check_title.append(titles[i])
    parametrs = (titles[i], times[i], texts[i], imgs[i], new_links[i])
    print(f"Link: {new_links[i]}\nTitle: {titles[i]}\nTime: {times[i]}\nImg Link{imgs[i]}\n Text: {texts[i]}\n\n")
    """cursor.execute('INSERT INTO news (title, date, text, image_link, origin_link) '
                   'VALUES (%s, %s, %s, %s, %s)', parametrs)
    conn.commit()
cursor.close()
conn.close()
    """