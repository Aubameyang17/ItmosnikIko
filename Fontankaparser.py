from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import traceback
import urllib.request

def get_links(links):
    options_chrome = webdriver.ChromeOptions()
    #options_chrome.add_argument("--headless")
    #options_chrome.add_argument('--no-sandbox')
    driverpobeda = webdriver.Chrome(options=options_chrome)

    try:
        url = "https://www.fontanka.ru/realty/"
        driverpobeda.get(url)
        wait = WebDriverWait(driverpobeda, 20)
        table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "announcementList_3JPr4")))
        content = table.find_elements(By.CLASS_NAME, "wrap_DjvF8")

        for el in content:
            new_link = el.find_element(By.CLASS_NAME, "header_DjvF8").get_attribute('href')
            links.append(new_link)
            print(new_link)

    except Exception as ex:
        traceback.print_exc()
        print("Рейсы не найдены")

    finally:
        driverpobeda.quit()  # Закрываем браузер

    return links


def chek_news(link, count):
    options_chrome = webdriver.ChromeOptions()
    # options_chrome.add_argument("--headless")
    # options_chrome.add_argument('--no-sandbox')
    driverpobeda = webdriver.Chrome(options=options_chrome)

    try:
        url = link
        driverpobeda.get(url)
        wait = WebDriverWait(driverpobeda, 20)
        table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "gridContent_6I1dB")))
        title = table.find_element(By.CLASS_NAME, "title_Gq8Rx")
        time = table.find_element(By.CLASS_NAME, "item_VmtHQ")
        text = table.find_element(By.CLASS_NAME, "articleContent_fefJj")
        img = table.find_element(By.CLASS_NAME, "image_nZVrb")
        print(f"Title: {title.text}\nTime: {time.text}\nText: {text.text}\n\n")
        src = img.get_attribute('src')
        name = str(count) + "titleimg.png"
        urllib.request.urlretrieve(src, name)

    except Exception as ex:
        traceback.print_exc()
        print("Рейсы не найдены")

    finally:
        driverpobeda.quit()  # Закрываем браузер



links = []

new_links = get_links(links)
count = 0

for link in new_links:
    chek_news(link, count)
    count += 1
