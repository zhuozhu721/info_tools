from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import os
import time
from datetime import datetime

def collect(start_dt, end_dt):
    results = []
    chromedriver_path = r"C:\Program Files\Google\Chrome_107.0.5304.122\Chrome-bin\chromedriver_win32\chromedriver.exe"
    chrome_path = r"C:\Program Files\Google\Chrome_107.0.5304.122\Chrome-bin\chrome.exe"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.binary_location = chrome_path
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    base_url = "https://www.whitehouse.gov"
    list_url = "https://www.whitehouse.gov/presidential-actions/executive-orders/"
    page = 1
    while True:
        url = list_url if page == 1 else f"{list_url}page/{page}/"
        driver.get(url)
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        blocks = soup.select('div.wp-block-group.wp-block-whitehouse-post-template__content')
        has_article_in_range = False
        for block in blocks:
            h2 = block.select_one('h2.wp-block-post-title')
            a = h2.find('a') if h2 else None
            title = a.get_text(strip=True) if a else ""
            href = a['href'] if a else ""
            if not href.startswith("http"):
                href = base_url + href
            category = ""
            cat_tag = block.select_one('.wp-block-post-terms a')
            if cat_tag:
                category = cat_tag.get_text(strip=True)
            else:
                cat_text = block.get_text(separator="|", strip=True)
                if "Executive Orders" in cat_text:
                    category = "Executive Orders"
            date_str = ""
            date_tag = block.select_one('time')
            if date_tag:
                date_str = date_tag.get_text(strip=True)
                try:
                    dt = datetime.strptime(date_str, "%B %d, %Y")
                except Exception:
                    try:
                        dt = datetime.strptime(date_str, "%b %d, %Y")
                    except Exception:
                        dt = None
            else:
                dt = None
            if not dt or not (start_dt <= dt <= end_dt):
                continue
            has_article_in_range = True
            summary = ""
            try:
                driver.get(href)
                time.sleep(2)
                detail_html = driver.page_source
                detail_soup = BeautifulSoup(detail_html, "html.parser")
                content = (
                    detail_soup.select_one(".wp-block-post-content") or
                    detail_soup.select_one(".page-content__content") or
                    detail_soup.select_one(".body-content")
                )
                if content:
                    text = content.get_text(separator="\n", strip=True)
                    summary = text[:200].replace('\n', ' ')
            except Exception:
                summary = ""
            results.append({
                "date": date_str,
                "title": title,
                "url": href,
                "source": "白宫行政令",
                "category": category,
                "summary": summary
            })
        if not has_article_in_range or len(blocks) == 0:
            break
        page += 1
    driver.quit()
    return results