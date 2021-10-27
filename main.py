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
from typing import Union
from urllib.parse import urljoin
from zipfile import BadZipFile

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
            print("Refreshing ")
            try:
                for line in os.popen("ps ax | grep firefox | grep -v grep"):
                    fields = line.split()
                    pid = fields[0]
                    os.kill(int(pid), signal.SIGKILL)
            except Exception as e:
                print("An error encountered while closing Firefox processes:", e)
                exit(0)

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
        blueprint = driver.current_url
        save_part(blueprint, page)
        add_link_to_ignored(blueprint)

@timeout(30)
def save_part(url: str, driver: WebDriver):
    # Download blueprints first
    if url in ignore_links:
        return

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
        if not page:
            continue 

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
    try:
        wb = openpyxl.load_workbook("data.xlsx")
    except BadZipFile:
        os.remove("data.xlsx")
        os.rename("recovery_data.xlsx", "data.xlsx")
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

    shutil.copy("data.xlsx", "recovery_data.xlsx")
    page.append(info)
    wb.save("data.xlsx")
    wb.close()
    
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

def connect_to(url: str, driver: WebDriver) -> Union[WebDriver, bool]:
    try:
        wait = WebDriverWait(driver, 10)
        driver.get(url)
        if check_400(driver):
            return False
            
        time.sleep(5)
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))

        return driver
    except TimeoutException:
        print("Failed to connect to:", url, "\nRetrying...")
        connect_to(url, driver)

def add_link_to_ignored(url: str):
    if url in ignore_links:
        return

    ignore_links.append(url)
    d = {"ignored": ignore_links}

    with open("ignored.json", "w") as f:
        json.dump(d, f)

def check_400(driver: WebDriver) -> bool:
    soup = bs(driver.page_source, "html.parser")
    center = soup.find("center")
    try:
        h1 = center.find("h1").text
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
        wb.close()

    opts = Options()
    ff_driver = os.getcwd() + "/geckodriver"
    driver = webdriver.Firefox(options=opts, executable_path=ff_driver)
    parse("https://dealler.ru/katalog/haval/haval-haval-h1/haval-h1-left-hand-drive-model-blue-logo-hf-h1-2/haval-h1-left-hand-drive-model-blue-logo-haval-h1-cc7151bma0p-16-ch035-g87-16/haval-h1-left-hand-drive-model-blue-logo-haval-h1-cc7151bma0p-16-%D0%B2%D0%BD%D1%83%D1%82%D1%80%D0%B5%D0%BD%D0%BD%D1%8F%D1%8F-%D0%B8-%D0%B2%D0%BD%D0%B5%D1%88%D0%BD%D1%8F%D1%8F-%D0%BE%D1%82%D0%B4%D0%B5%D0%BB%D0%BA%D0%B0-ch035-4-g87-16/haval-h1-cc7151bma0p-16-%D0%B2%D0%BD%D1%83%D1%82%D1%80%D0%B5%D0%BD%D0%BD%D1%8F%D1%8F-%D0%B8-%D0%B2%D0%BD%D0%B5%D1%88%D0%BD%D1%8F%D1%8F-%D0%BE%D1%82%D0%B4%D0%B5%D0%BB%D0%BA%D0%B0-%D0%B7%D0%B0%D0%B4%D0%BD%D0%B8%D0%B9-%D1%80%D0%B5%D0%BC%D0%B5%D0%BD%D1%8C-%D0%B1%D0%B5%D0%B7%D0%BE%D0%BF%D0%B0%D1%81%D0%BD%D0%BE%D1%81%D1%82%D0%B8-g83-58-7.html", driver)
    driver.quit()
