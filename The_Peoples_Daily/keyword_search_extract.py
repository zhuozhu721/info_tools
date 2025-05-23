import os
import shutil
import requests
from bs4 import BeautifulSoup
from docx import Document
from datetime import datetime, timedelta

def get_layout_url(date_obj):
    date_str = date_obj.strftime("%Y%m/%d")
    return f"http://paper.people.com.cn/rmrb/pc/layout/{date_str}/node_01.html"

def fetch_all_layout_urls(first_layout_url):
    resp = requests.get(first_layout_url)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    layout_urls = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('node_') and href.endswith('.html'):
            full_url = requests.compat.urljoin(first_layout_url, href)
            layout_urls.add(full_url)
    layout_urls.add(first_layout_url)
    return list(layout_urls)

def fetch_article_links(layout_url):
    resp = requests.get(layout_url)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.endswith('.html') and 'node_' not in href:
            full_url = requests.compat.urljoin(layout_url, href)
            links.append(full_url)
    return list(set(links))

def fetch_article(url):
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    title_tag = (
        soup.find('h1', class_='news-title') or
        soup.find('h3', class_='article-title') or
        soup.find('h1') or
        soup.find('title')
    )
    title = title_tag.text.strip() if title_tag else "No Title"
    content_div = soup.find('div', id='ozoom')
    paragraphs = content_div.find_all('p') if content_div else []
    content = '\n'.join([p.text.strip() for p in paragraphs])
    return title, content

def save_to_docx(title, content, folder, date_str, layout_name):
    doc = Document()
    doc.add_heading(title, level=1)
    doc.add_paragraph(content)
    safe_title = "".join(c for c in title if c.isalnum() or c in " _-")
    filename = f"{date_str}_{layout_name}_{safe_title}.docx"
    filename = os.path.join(folder, filename)
    doc.save(filename)

def search_articles_by_keyword(folder, keywords):
    # keywords: list of str
    for keyword in keywords:
        keyword = keyword.strip()
        if not keyword:
            continue
        keyword_folder = os.path.join(folder, keyword)
        os.makedirs(keyword_folder, exist_ok=True)
        matched = []
        for filename in os.listdir(folder):
            if filename.endswith('.docx'):
                filepath = os.path.join(folder, filename)
                doc = Document(filepath)
                title = doc.paragraphs[0].text if doc.paragraphs else ""
                # 只筛选标题
                if keyword in title:
                    matched.append((title, filename))
                    out_path = os.path.join(keyword_folder, filename)
                    shutil.copy(filepath, out_path)
        print(f"共找到 {len(matched)} 篇标题包含“{keyword}”的文章，已分别保存到 {keyword_folder}")
    # 删除除关键词文件夹外的所有docx
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if filename.endswith('.docx'):
            os.remove(file_path)

def main():
    # 支持自定义日期区间
    start_input = input("请输入起始日期(YYYY-MM-DD)，直接回车为当天: ").strip()
    end_input = input("请输入结束日期(YYYY-MM-DD)，直接回车为当天: ").strip()
    keywords_input = input("请输入要筛选的关键词（多个用英文逗号分隔）: ").strip()
    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
    if not start_input:
        start_date = datetime.now()
    else:
        start_date = datetime.strptime(start_input, "%Y-%m-%d")
    if not end_input:
        end_date = start_date
    else:
        end_date = datetime.strptime(end_input, "%Y-%m-%d")

    # 统一区间文件夹
    if start_date == end_date:
        folder = os.path.join(os.getcwd(), start_date.strftime("%Y-%m-%d"))
    else:
        folder = os.path.join(os.getcwd(), f"{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}")
    os.makedirs(folder, exist_ok=True)

    for single_date in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
        today_str = single_date.strftime("%Y-%m-%d")
        first_layout_url = get_layout_url(single_date)
        print(f"\n{today_str} 头版链接: {first_layout_url}")
        layout_urls = fetch_all_layout_urls(first_layout_url)
        print(f"共找到 {len(layout_urls)} 个版面。")
        all_article_links = []
        for layout_url in layout_urls:
            article_links = fetch_article_links(layout_url)
            print(f"{layout_url} 找到 {len(article_links)} 篇文章。")
            layout_name = layout_url.split('/')[-1].replace('.html', '')
            for url in article_links:
                all_article_links.append((url, today_str, layout_name))
        print(f"{today_str} 共找到 {len(all_article_links)} 篇文章。")
        for url, date_str, layout_name in all_article_links:
            title, content = fetch_article(url)
            print(f"正在下载: {title}")
            save_to_docx(title, content, folder, date_str, layout_name)
            print(f"已保存: {title}.docx 到 {folder}")

    # 关键词检索并单独保存
    if keywords:
        search_articles_by_keyword(folder, keywords)

if __name__ == "__main__":
    main()