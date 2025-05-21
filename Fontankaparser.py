import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import traceback

from urllib3.exceptions import ReadTimeoutError

from OpenRouterApi import summorize_text

conn = psycopg2.connect(dbname="ItmosnikIko", host="127.0.0.1", user="Alex", password="alex")
cursor = conn.cursor()


def get_links(links, titles, times, imgs):
    options_chrome = webdriver.ChromeOptions()
    #options_chrome.add_argument("--headless")
    #options_chrome.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options_chrome)

    try:
        url = "https://www.fontanka.ru/realty/"
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "announcementList_3JPr4")))
        content = table.find_elements(By.CLASS_NAME, "wrap_DjvF8")

        for el in content:
            new_link = el.find_element(By.CLASS_NAME, "header_DjvF8").get_attribute("href")

            # 🔍 Проверка: есть ли такая ссылка в БД
            cursor.execute("SELECT 1 FROM news WHERE origin_link = %s", (new_link,))
            if cursor.fetchone():
                continue  # Ссылка уже есть в БД

            # Добавляем новую ссылку и сопутствующие данные
            links.append(new_link)
            titles.append(el.find_element(By.CLASS_NAME, "header_DjvF8").text)
            times.append(el.find_element(By.CLASS_NAME, "text_0UNFI").text)

            try:
                img = el.find_element(By.TAG_NAME, "img").get_attribute("src")
            except Exception:
                img = ""
            imgs.append(img)

            print(f"🆕 Найдена новая статья: {new_link}")

    except Exception:
        traceback.print_exc()
        print("⚠️ Ошибка при загрузке страницы Fontanka")

    finally:
        driver.quit()

    return links, titles, times, imgs


def chek_news(link):
    options_chrome = webdriver.ChromeOptions()
    #options_chrome.add_argument("--headless")
    #options_chrome.add_argument('--no-sandbox')
    driverpobeda = webdriver.Chrome(options=options_chrome)
    text = ""
    if 'longreads' in link:
        try:
            url = link
            driverpobeda.get(url)
            wait = WebDriverWait(driverpobeda, 20)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tn-atom")))
            content = driverpobeda.find_elements(By.CLASS_NAME, "tn-atom")
            for el in content:
                if len(el.text) > 0:
                    text += el.text + " "

            text = summorize_text(text)

        except ReadTimeoutError:
            driverpobeda.execute_script("window.stop();")
        except Exception as ex:
            traceback.print_exc()
            print("Рейсы не найдены")

        finally:
            driverpobeda.quit()  # Закрываем браузер


    else:
        try:
            url = link
            driverpobeda.get(url)
            wait = WebDriverWait(driverpobeda, 20)
            table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "gridContent_6I1dB")))
            content = table.find_element(By.CLASS_NAME, "articleContent_fefJj")
            text = summorize_text(content.text)

        except ReadTimeoutError:
            driverpobeda.execute_script("window.stop();")
        except Exception as ex:
            traceback.print_exc()
            print("Рейсы не найдены")

        finally:
            driverpobeda.quit()  # Закрываем браузер

    return text



links = []
titles = []
times = []
imgs = []
texts = []
count = 10
new_links, titles, times, imgs = get_links(links, titles, times, imgs)


for link in range(10):
    text = chek_news(new_links[link])
    texts.append(text)


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
    cursor.execute('INSERT INTO news (title, date, text, image_link, origin_link) '
                                               'VALUES (%s, %s, %s, %s, %s)', parametrs)
    conn.commit()
