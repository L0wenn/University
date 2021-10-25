"""
TODO: Enter the catalogue, step through all categories
until we find parts table and blueprint(bp), save the bp,
step through all parts in the table, save images of parts
and their info and write all of it into xlsx file
""" 

import errno
import json
import os
import shutil
import signal
import sys
import time
from functools import wraps
from urllib.parse import urljoin

import openpyxl
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://dealler.ru/katalog"

with open("ignored.json", "r") as f:
    data = f.read()
    ignore_links = json.loads(data)["ignored"]

def timeout(seconds=100, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            print("Script stuck! Restarting in 5 minutes")
            try:
                for line in os.popen("ps ax | grep firefox | grep -v grep"):
                    fields = line.split()
                    pid = fields[0]
                    os.kill(int(pid), signal.SIGKILL)
            except Exception as e:
                print("An error encountered while closing Firefox processes:", e)
                exit(0)

            #time.sleep(300)
            os.execv(sys.executable, ['python'] + sys.argv)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


def parse(url:str, driver: WebDriver):
    """
    TODO: Function must step through the catalogue
    recursively untill it finds div with class products-view
    """
    if url in ignore_links:
        return

    page = connect_to(url, driver)
    soup = bs(page.page_source, "html.parser")

    if soup.find("div", class_="products-view") is None:
        div = soup.find_all("div", class_="category")

        for category in div:
            a = category.find("a")

            absolute_link = urljoin(URL, a["href"])
            if absolute_link in ignore_links:
                continue
            
            parse(absolute_link, page)
            add_link_to_ignored(absolute_link)
    else:
        bp = driver.current_url
        save_part(bp, page)
        add_link_to_ignored(bp)

@timeout(30)
def save_part(url: str, driver: WebDriver):
    # Download blueprints first
    if url in ignore_links:
        return
    elif check_400(driver):
        add_link_to_ignored(driver.current_url)

    soup = bs(driver.page_source, "html.parser")
    bp_div = soup.find("div", class_="category_description")
    bp_img = bp_div.find("img")
    img_url = URL.replace("/katalog", bp_img["src"])
    download_image(img_url)

    # Next download all parts from tables
    products = soup.find_all("div", class_="product-name")
    for product in products:
        a = product.find("a")

        if a == None:
            continue

        absolute_link = urljoin(URL, a["href"])
        if absolute_link in ignore_links:
            continue

        page = connect_to(absolute_link, driver)
        soup = bs(page.page_source, "html.parser")
        img_div = soup.find("div", class_="main-image")

        try:
            img_url = img_div.find("a")["href"]
        except AttributeError:
            continue

        download_image(img_url)
        write_to_xls(absolute_link, img_url, page)
        add_link_to_ignored(absolute_link)

def write_to_xls(url: str, image, driver: WebDriver):
    wb = openpyxl.load_workbook("data.xlsx")
    page = wb.active
    filename = image.split("/")[-1]
    info = [filename if not filename.startswith("image not available") else "chinatown.jpg"]

    soup = bs(driver.page_source, "html.parser")

    product = soup.find("div", class_="product-area")
    manufacturer = product.find("div", class_="manufacturer")
    name = soup.find("h1")
    desc = product.find("div", "product-short-description")
    number = soup.find("b").text

    ul = soup.find("ul", class_="breadcrumb")
    a = ul.find_all("a")
    path = []

    for el in a:
        path.append(el.find("span").text)

    path = "/".join(path)

    try:
        comm = soup.find("div", class_="product-description").text
    except AttributeError:
        comm = "None"

    info.append(manufacturer.text)
    info.append(number)
    info.append(name.text)
    info.append(desc.text.replace("\n", "").replace("\t", ""))
    info.append(path.replace("Каталоги/", ""))
    info.append(comm.replace("\nОписание\n\t", ""))

    page.append(info)
    wb.save("data.xlsx")

def download_image(url: str):
    filename = url.split("/")[-1]
    path = f"images/{filename}"

    if filename == "image not available.png":
        return
    
    try:
        r = requests.get(url, stream=True)

        with open(path, "wb") as f:
            shutil.copyfileobj(r.raw, f)
    except requests.exceptions.ConnectionError:
        print("We are being ratelimited. Sleeping 1 minute")
        time.sleep(60)
        print("Retrying...")
        download_image(url)

def connect_to(url: str, driver: WebDriver) -> WebDriver:
    try:
        wait = WebDriverWait(driver, 10)
        driver.get(url)
        time.sleep(5)
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))

        return driver
    except TimeoutException:
        print("Failed to connect to:", url, "\nRetrying...")
        connect_to(url, driver)

def add_link_to_ignored(url: str):
    ignore_links.append(url)
    d = {"ignored": ignore_links}

    with open("ignored.json", "w") as f:
        json.dump(d, f)

def check_400(driver: WebDriver) -> bool:
    soup = bs(driver.page_source, "html.parser")
    try:
        h1 = soup.find("h1").text
    except AttributeError:
        return False

    return True if h1.lower() == "400 bad request" else False


if __name__ == "__main__":
    if not os.path.exists("data.xlsx"):
        headers = [
        "Название изображения",
        "Название производителя",
        "Номер детали",
        "Название детали",
        "Развёрнутое описание детали",
        "Категория",
        "Комментарий"
        ]
        
        wb = openpyxl.Workbook()
        page = wb.active
        page.append(headers)
        wb.save("data.xlsx")

    opts = Options()
    ff_driver = os.getcwd() + "/geckodriver"
    driver = webdriver.Firefox(options=opts, executable_path=ff_driver)
    parse(URL, driver)
    driver.quit()
