import PySimpleGUI as sg
from datetime import datetime, timedelta
import os
import requests
from bs4 import BeautifulSoup
from docx import Document

def get_layout_url(date_obj):
    date_str = date_obj.strftime("%Y%m/%d")
    return f"http://paper.people.com.cn/rmrb/pc/layout/{date_str}/node_01.html"

def fetch_all_layout_urls(first_layout_url):
    try:
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
    except Exception as e:
        print(f"获取版面链接失败: {e}")
        return []

def fetch_article_links(layout_url):
    try:
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
    except Exception as e:
        print(f"获取文章链接失败: {e}")
        return []

def fetch_title_only(url):
    try:
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
        return title
    except Exception as e:
        print(f"获取标题失败: {e}")
        return "No Title"

def fetch_article_content(url):
    try:
        resp = requests.get(url)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        content_div = soup.find('div', id='ozoom')
        paragraphs = content_div.find_all('p') if content_div else []
        content = '\n'.join([p.text.strip() for p in paragraphs])
        return content
    except Exception as e:
        print(f"获取正文失败: {e}")
        return ""

def save_to_docx(title, content, folder, date_str, layout_name):
    # layout_name 形如 node_01，转换为“第1版”
    if layout_name.startswith("node_"):
        try:
            num = int(layout_name.replace("node_", ""))
            layout_str = f"第{num}版"
        except:
            layout_str = layout_name
    else:
        layout_str = layout_name
    safe_title = "".join(c for c in title if c.isalnum() or c in " _-")
    filename = f"{date_str}_{layout_str}_{safe_title}.docx"
    filename = os.path.join(folder, filename)
    doc = Document()
    doc.add_heading(title, level=1)
    doc.add_paragraph(content)
    doc.save(filename)

def main_gui():
    layout = [
        [sg.Text('起始日期(YYYY-MM-DD):'), sg.Input(key='start')],
        [sg.Text('结束日期(YYYY-MM-DD):'), sg.Input(key='end')],
        [sg.Text('关键词(用中文逗号分隔):'), sg.Input(key='keywords')],
        [sg.Text('保存文件夹:'), sg.Input(key='folder'), sg.FolderBrowse()],
        [sg.Text('', size=(60,1), key='-STATUS-')],
        [sg.ProgressBar(100, orientation='h', size=(50, 20), key='-PROGRESS-')],
        [sg.Output(size=(90, 15))],
        [sg.Button('开始'), sg.Button('退出')]
    ]
    window = sg.Window('人民日报文章筛选下载', layout, finalize=True)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, '退出'):
            break
        if event == '开始':
            start_input = values['start'].strip()
            end_input = values['end'].strip()
            keywords_input = values['keywords'].strip()
            folder = values['folder'].strip()
            if not folder:
                sg.popup_error("请选择保存文件夹！")
                continue
            # 支持中文逗号和英文逗号
            raw_keywords = keywords_input.replace('，', ',')
            keywords = [k.strip() for k in raw_keywords.split(",") if k.strip()]
            if not keywords:
                sg.popup_error("请输入至少一个关键词！")
                continue
            # 日期处理
            try:
                if not start_input:
                    start_date = datetime.now()
                else:
                    start_date = datetime.strptime(start_input, "%Y-%m-%d")
                if not end_input:
                    end_date = start_date
                else:
                    end_date = datetime.strptime(end_input, "%Y-%m-%d")
            except Exception as e:
                print("日期格式错误，请输入YYYY-MM-DD格式")
                continue

            if start_date > end_date:
                print("起始日期不能晚于结束日期！")
                continue

            # 生成保存子文件夹
            if start_date == end_date:
                save_folder = os.path.join(folder, start_date.strftime("%Y-%m-%d"))
            else:
                save_folder = os.path.join(folder, f"{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}")
            os.makedirs(save_folder, exist_ok=True)

            # 1. 收集所有文章链接
            window['-STATUS-'].update("正在收集文章链接 ...")
            window['-PROGRESS-'].update_bar(0, 1)
            window.refresh()
            article_info_list = []
            date_list = [start_date + timedelta(n) for n in range((end_date - start_date).days + 1)]
            for single_date in date_list:
                first_layout_url = get_layout_url(single_date)
                layout_urls = fetch_all_layout_urls(first_layout_url)
                for layout_url in layout_urls:
                    article_links = fetch_article_links(layout_url)
                    layout_name = layout_url.split('/')[-1].replace('.html', '')
                    for url in article_links:
                        article_info_list.append((url, single_date.strftime("%Y-%m-%d"), layout_name))
            total_articles = len(article_info_list)
            if total_articles == 0:
                window['-STATUS-'].update("未找到任何文章，请检查日期范围。")
                continue

            window['-PROGRESS-'].update_bar(0, total_articles)
            window['-STATUS-'].update(f"共需筛选 {total_articles} 篇文章，开始筛选 ...")
            window.refresh()

            # 2. 只下载命中关键词的文章
            matched_count = 0
            for idx, (url, date_str, layout_name) in enumerate(article_info_list, 1):
                title = fetch_title_only(url)
                if any(kw in title for kw in keywords):
                    content = fetch_article_content(url)
                    save_to_docx(title, content, save_folder, date_str, layout_name)
                    matched_count += 1
                    print(f"[{matched_count}] {date_str} 命中: {title}")
                window['-PROGRESS-'].update_bar(idx)
                if idx % 10 == 0 or idx == total_articles:
                    window['-STATUS-'].update(f"已筛选 {idx}/{total_articles} 篇，命中 {matched_count} 篇 ...")
                    window.refresh()
            window['-STATUS-'].update(f"全部完成！共保存 {matched_count} 篇命中文章。")
            print(f"全部完成！共保存 {matched_count} 篇命中文章。")

    window.close()

if __name__ == "__main__":
    main_gui()