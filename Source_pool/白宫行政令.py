from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import os
import time
from datetime import datetime, timedelta

# 默认时间范围为最近一周
end_dt = datetime.today()
start_dt = end_dt - timedelta(days=31)
start_date = start_dt.strftime("%Y-%m-%d")
end_date = end_dt.strftime("%Y-%m-%d")

save_dir = f"白宫行政令_{start_date}_{end_date}"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# 指定chromedriver和chrome路径
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
    print(f"抓取第{page}页: {url}")
    driver.get(url)
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    blocks = soup.select('div.wp-block-group.wp-block-whitehouse-post-template__content')
    print(f"本页抓到{len(blocks)}个行政令内容块")
    has_article_in_range = False
    for block in blocks:
        # 文件名称
        h2 = block.select_one('h2.wp-block-post-title')
        a = h2.find('a') if h2 else None
        title = a.get_text(strip=True) if a else ""
        href = a['href'] if a else ""
        if not href.startswith("http"):
            href = base_url + href

        # 文件类别
        category = ""
        cat_tag = block.select_one('.wp-block-post-terms a')
        if cat_tag:
            category = cat_tag.get_text(strip=True)
        else:
            cat_text = block.get_text(separator="|", strip=True)
            if "Executive Orders" in cat_text:
                category = "Executive Orders"

        # 发布时间
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

        # 按时间范围筛选
        if not dt or not (start_dt <= dt <= end_dt):
            continue

        has_article_in_range = True
        print(f"文件名称: {title}")
        print(f"文件类别: {category}")
        print(f"发布时间: {date_str}")

        # 获取详情页正文（支持多种选择器）
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
                print("正文摘要:", text[:200].replace('\n', ' '))
            else:
                print("正文内容节点: None")
        except Exception as e:
            print(f"  正文保存失败: {e}")

        print("-" * 40)

    # 如果本页没有任何文章在时间范围内，或者本页所有文章都早于起始日期，则停止
    if not has_article_in_range or len(blocks) == 0:
        print("没有更多符合时间范围的行政令，结束。")
        break

    page += 1

driver.quit()