"""
TODO: Enter the catalogue, step through all categories
until we find parts table and blueprint(bp), save the bp,
step through all parts in the table, save images of parts
and their info and write all of it into xlsx file
""" 

import errno
import json
from math import pi
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
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://чинамобил.рф/"

with open("ignored.json", "r") as f:
    data = f.read()
    ignore_links = json.loads(data)["ignored"]

def timeout(seconds=100, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            print("Refreshing")
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
    if url in ignore_links:
        return

    page = connect_to(url, driver)
    soup = bs(page.page_source, "html.parser")
    
    if soup.find("div", class_="win") or soup.find("form", action="/magazin?mode=cart&action=add"):
        absolute_link = None

        try:
            save_part(page.current_url, page)
        except AttributeError:
            return

        try:
            for folder in soup.find_all("div", class_="block-main-img"):
                a = folder.find("a")["href"]

                absolute_link = urljoin(URL, a)
                if absolute_link in ignore_links:
                    continue

                parse(absolute_link, page)
        except Exception:
            pass

        add_link_to_ignored(absolute_link)
    elif soup.find("div", class_="block-main-img") is None:
        if soup.find("div", class_="wrap-img-main"):
            return

        categories = soup.find("nav", class_="kategor2")
        lis = categories.find_all("li")

        for li in lis:
            a = li.find("a")["href"]

            absolute_link = urljoin(URL, a)
            if absolute_link in ignore_links:
                continue

            parse(absolute_link, page)
            add_link_to_ignored(absolute_link)
    else:
        for found_div in soup.find_all("div", class_="block-main-img"):
            a = found_div.find("a")["href"]

            absolute_link = urljoin(URL, a)
            if absolute_link in ignore_links:
                continue

            parse(absolute_link, page)
            add_link_to_ignored(absolute_link)

#@timeout(30)
def save_part(url: str, driver: WebDriver):
    if url in ignore_links:
        return

    write_to_xls(url, driver)
        
    #write_to_xls(absolute_link, page)
    #add_link_to_ignored(absolute_link)

def write_to_xls(url: str, driver: WebDriver):
    try:
        wb = openpyxl.load_workbook("data.xlsx")
    except BadZipFile:
        os.remove("data.xlsx")
        os.rename("recovery_data.xlsx", "data.xlsx")
        wb = openpyxl.load_workbook("data.xlsx")

    page = wb.active
    soup = bs(driver.page_source, "html.parser")

    part_NO = ""
    part_name = ""
    manufacturer = ""
    category = ""

    path = soup.find("div", class_="site-path").text
    table = soup.find("form", action="/magazin?mode=cart&action=add")

    if table is None:
        desc = soup.find("div", class_="f_desc")
        p = desc.find("p")
        parts = p.get_text(strip=True, separator="\n").splitlines()

        for part in parts:
            part.replace("\xa0", " ")

            part_NO = part.split(" ")[-1]
            part_name = " ".join(part.split(" ")[:-1])
            category = path.replace("Главная \ ", "")
    else:
        tbody = table.find("tbody")
        oddtr = tbody.find_all("tr", class_="odd")
        eventr = tbody.find_all("tr", class_="even")
        tr = oddtr + eventr
        
        for element in tr:
            text = element.get_text("|", strip=True)
            text = text.split("|")
            
            part_NO = text[1]
            part_name = text[0]
            manufacturer = text[3]
            category = path.replace("Главная \ ", "")
        
        #print(tr[0].get_text("|", strip=True), "\n\n")
            
    shutil.copy("data.xlsx", "recovery_data.xlsx")
    page.append([part_NO, part_name, manufacturer, category])
    wb.save("data.xlsx")
    wb.close()

def connect_to(url: str, driver: WebDriver) -> Union[WebDriver, bool]:
    try:
        wait = WebDriverWait(driver, 10)
        driver.get(url)
        # if check_400(driver):
        #     return False
            
        # time.sleep(5)
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
        json.dump(d, f, indent=2, separators=(",", ": "))

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
        "Номер детали",
        "Название детали",
        "Название производителя",
        "Категория"
        ]
        
        wb = openpyxl.Workbook()
        page = wb.active
        page.append(headers)
        wb.save("data.xlsx")
        wb.close()

    opts = Options()
    ff_driver = os.getcwd() + "/geckodriver"
    driver = webdriver.Firefox(options=opts, executable_path=ff_driver)
    parse(URL, driver)
    driver.quit()
