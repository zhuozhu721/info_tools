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

def fetch_article_links_with_titles(layout_url):
    try:
        resp = requests.get(layout_url)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        articles = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.endswith('.html') and 'node_' not in href:
                full_url = requests.compat.urljoin(layout_url, href)
                title = a.text.strip()
                if title:
                    articles.append((full_url, title))
        return articles
    except Exception as e:
        print(f"获取文章链接和标题失败: {e}")
        return []

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
    today = datetime.now()
    week_ago = today - timedelta(days=6)
    default_folder = os.getcwd()
    layout = [
        [sg.Text('起始日期(YYYY-MM-DD):'), sg.Input(default_text=week_ago.strftime("%Y-%m-%d"), key='start')],
        [sg.Text('结束日期(YYYY-MM-DD):'), sg.Input(default_text=today.strftime("%Y-%m-%d"), key='end')],
        [sg.Text('关键词(用中文逗号分隔):'), sg.Input(key='keywords')],
        [sg.Text('保存文件夹:'), sg.Input(default_text=default_folder, key='folder'), sg.FolderBrowse()],
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
            raw_keywords = keywords_input.replace('，', ',')
            keywords = [k.strip() for k in raw_keywords.split(",") if k.strip()]
            if not keywords:
                sg.popup_error("请输入至少一个关键词！")
                continue
            try:
                if not start_input:
                    start_date = today
                else:
                    start_date = datetime.strptime(start_input, "%Y-%m-%d")
                if not end_input:
                    end_date = today
                else:
                    end_date = datetime.strptime(end_input, "%Y-%m-%d")
            except Exception as e:
                print("日期格式错误，请输入YYYY-MM-DD格式")
                continue

            if start_date > end_date:
                print("起始日期不能晚于结束日期！")
                continue

            if start_date == end_date:
                save_folder = os.path.join(folder, start_date.strftime("%Y-%m-%d"))
            else:
                save_folder = os.path.join(folder, f"{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}")
            os.makedirs(save_folder, exist_ok=True)

            # 1. 收集所有文章链接和标题（带进度）
            window['-STATUS-'].update("正在收集文章链接 ...")
            date_list = [start_date + timedelta(n) for n in range((end_date - start_date).days + 1)]
            total_days = len(date_list)
            window['-PROGRESS-'].update_bar(0, total_days)
            window.refresh()
            article_info_list = []
            for day_idx, single_date in enumerate(date_list, 1):
                today_str = single_date.strftime("%Y-%m-%d")
                window['-STATUS-'].update(f"正在收集 {today_str} 的文章链接 ({day_idx}/{total_days}) ...")
                window['-PROGRESS-'].update_bar(day_idx)
                window.refresh()
                first_layout_url = get_layout_url(single_date)
                layout_urls = fetch_all_layout_urls(first_layout_url)
                for layout_url in layout_urls:
                    layout_name = layout_url.split('/')[-1].replace('.html', '')
                    articles = fetch_article_links_with_titles(layout_url)
                    for url, title in articles:
                        article_info_list.append((url, single_date.strftime("%Y-%m-%d"), layout_name, title))
            total_articles = len(article_info_list)
            if total_articles == 0:
                window['-STATUS-'].update("未找到任何文章，请检查日期范围。")
                continue

            window['-PROGRESS-'].update_bar(0, total_articles)
            window['-STATUS-'].update(f"共需筛选 {total_articles} 篇文章，开始筛选 ...")
            window.refresh()

            # 2. 只下载命中关键词的文章
            matched_count = 0
            for idx, (url, date_str, layout_name, title) in enumerate(article_info_list, 1):
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