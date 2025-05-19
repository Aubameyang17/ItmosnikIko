from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import traceback

from OpenRouterApi import summorize_text


def get_links(links, titles, times, imgs):
    options_chrome = webdriver.ChromeOptions()
    driverpobeda = webdriver.Chrome(options=options_chrome)

    try:
        url = "https://www.fontanka.ru/realty/"
        driverpobeda.get(url)
        wait = WebDriverWait(driverpobeda, 20)
        table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "announcementList_3JPr4")))
        content = table.find_elements(By.CLASS_NAME, "wrap_DjvF8")

        for el in content:
            new_link = el.find_element(By.CLASS_NAME, "header_DjvF8")
            time = el.find_element(By.CLASS_NAME, "text_0UNFI")
            try:
                img = el.find_element(By.TAG_NAME, "img").get_attribute("src")
            except Exception:
                img = ""
            links.append(new_link.get_attribute("href"))
            titles.append(new_link.text)
            times.append(time.text)
            imgs.append(img)
            print(f"Title: {new_link.text}\nTime: {time.text}\nImage Link: {img}\nOrigin Link: {new_link.get_attribute('href')}\n\n")

    except Exception as ex:
        traceback.print_exc()
        print("Рейсы не найдены")

    finally:
        driverpobeda.quit()  # Закрываем браузер

    return links, titles, times, imgs


def chek_news(link):
    options_chrome = webdriver.ChromeOptions()
    # options_chrome.add_argument("--headless")
    # options_chrome.add_argument('--no-sandbox')
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
            print(f"Text: {text}\n\n")


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
            print(f"Text: {text}\n\n")


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

new_links, titles, times, imgs = get_links(links, titles, times, imgs)

for link in new_links:
    text = chek_news(link)
    texts.append(text)

