import datetime
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from urllib3.exceptions import ReadTimeoutError
import traceback
import psycopg2
import requests
from bs4 import BeautifulSoup

from OpenRouterApi import summorize_text, maintheme_text

conn = psycopg2.connect(dbname="ItmosnikIko", host="127.0.0.1", user="Alex", password="alex")
cursor = conn.cursor()

year = datetime.date.today().year
month_to_number = {'января': "01", 'февраля': "02", 'марта': "03", 'апреля': "04", 'мая': "05", 'июня': "06",
                   'июля': "07", 'августа': "08", 'сентября': "09", 'октября': "10", 'ноября': "11", 'декабря': "12"}

def get_links(links, titles, imgs):
    try:
        url = "https://nsp.ru/analitika"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        cards = soup.find_all("app-material-card", class_="small")
        # подключение к БД

        for el in cards:
            try:
                header = el.find("div", class_="h5")
                a = el.find('a', href=True)
                href = a['href']
                if href:
                    new_link = "https://nsp.ru/" + href
                else:
                    new_link = ""

                """# Проверка наличия в БД
                cursor.execute("SELECT 1 FROM news WHERE origin_link = %s", (new_link,))
                if cursor.fetchone():
                    continue"""

                # Добавляем в списки
                links.append(new_link)
                titles.append(header.get_text(strip=True))

                img_tag = el.find("div", class_='card-img')
                source_tag = img_tag.find("source", attrs={"srcset": True})

                if source_tag:
                    img_url = source_tag["srcset"]
                else:
                    img_url = ""
                    print("❌ srcset не найден")
                imgs.append(img_url)


                #print(f"🆕 Найдена новая статья: {new_link}")
            except Exception as e:
                pass

        cursor.close()
        conn.close()

    except Exception as e:
        print("❌ Ошибка при загрузке страницы:", e)

    return links, titles, imgs


def chek_news(link, times):
    options = uc.ChromeOptions()
    # options.headless = True
    # options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=options)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    text = ""

    try:
        driver.get(link)
        time.sleep(2)

        # Находим все карточки
        wait = WebDriverWait(driver, 10)
        date_div = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "topline-info-date"))
        )

        # Получаем видимый текст (например: "14 мая в 16:46")
        date_text = date_div.text.strip()
        month = month_to_number[date_text.split()[1]]
        day = date_text.split()[0]
        date = f"{year}-{month}-{day}"
        times.append(date)



        response = requests.get(link, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        content = soup.find_all('p')
        for el in content:
            if el.get_text(strip=True):
                text += el.get_text(strip=True) + " "

        if text:
            text = summorize_text(text)


    except ReadTimeoutError:
        print("⏱ Превышено время ожидания при загрузке:", link)
    except Exception:
        traceback.print_exc()
        print("⚠️ Ошибка при получении статьи:", link)

    finally:
        driver.quit()

    return text, times


links = []
titles = []
times = []
imgs = []
texts = []
count = 10
new_links, titles, imgs = get_links(links, titles, imgs)
zamena = ["Ключевые моменты:", "Основные моменты статьи:", "Краткая выжимка:", "Главные моменты:", " Суть статьи:",
          "Основные моменты:", "Основные пункты:", "Главные тезисы статьи:",
          "Вот краткая выжимка основных тезисов статьи:", "Основные тезисы статьи:", "Основные тезисы:"]

for link in range(10):
    text, times = chek_news(new_links[link], times)
    new_text = text
    for old in zamena:
        new_text = new_text.replace(old, "")

    themetext = maintheme_text(new_text)
    print(themetext.title())

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
    print(f"Link: {new_links[i]}\nTitle: {titles[i]}\nTime: {times[i]}\nImg Link: {imgs[i]}\n Text: {texts[i]}\n\n")
    """cursor.execute('INSERT INTO news (title, date, text, image_link, origin_link) '
                   'VALUES (%s, %s, %s, %s, %s)', parametrs)
    conn.commit()"""
