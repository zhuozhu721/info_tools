import PySimpleGUI as sg
from datetime import datetime, timedelta
import os
import importlib

INFO_SOURCES = {
    "赛迪研究院": "Source_pool.赛迪研究院",
    "国务院发展研究中心": "Source_pool.国务院发展研究中心",
    "白宫行政令": "Source_pool.白宫行政令",
    "MIT科技评论10大热点": "Source_pool.MIT_Tech",
}

# 采集函数

def collect_from_source(source_name, start_dt, end_dt, keywords=None, save_folder=None):
    try:
        module_path = INFO_SOURCES[source_name]
        module = importlib.import_module(module_path)
        if hasattr(module, "collect"):
            # 只对人民日报等支持关键词的采集源传递keywords
            if keywords is not None and "人民日报" in source_name:
                data = module.collect(start_dt=start_dt, end_dt=end_dt, keywords=keywords, save_folder=save_folder)
            # MIT科技评论采集源只需要save_folder参数，且采集结果为docx且正文已自动过滤广告/推荐/订阅等
            elif "MIT科技评论" in source_name or "MIT Tech" in source_name:
                data = module.collect(save_folder=save_folder)
            else:
                data = module.collect(start_dt=start_dt, end_dt=end_dt, save_folder=save_folder)
            return data
        else:
            return []
    except Exception as e:
        return []

def main_gui():
    today = datetime.now()
    week_ago = today - timedelta(days=15)
    default_folder = os.path.join(os.path.expanduser("~"), "Desktop", "download")
    sg.theme('SystemDefault')
    layout = [
        [sg.Text('请选择信息源：')],
        [sg.Listbox(values=["全部"] + list(INFO_SOURCES.keys()), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, size=(30, 4), key='sources', default_values=["全部"] )],
        [sg.Text('起始日期(YYYY-MM-DD):'), sg.Input(default_text=week_ago.strftime("%Y-%m-%d"), key='start')],
        [sg.Text('结束日期(YYYY-MM-DD):'), sg.Input(default_text=today.strftime("%Y-%m-%d"), key='end')],
        [sg.Text('保存文件夹:'), sg.Input(default_text=default_folder, key='folder'), sg.FolderBrowse(target='folder')],
        [sg.Text('', size=(60,1), key='-STATUS-')],
        [sg.ProgressBar(100, orientation='h', size=(50, 20), key='-PROGRESS-')],
        [sg.Output(size=(80, 15))],
        [sg.Button('开始'), sg.Button('退出')],
    ]
    window = sg.Window('信息采集工具', layout, finalize=True)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, '退出'):
            break
        if event == '开始':
            start_input = values['start'].strip()
            end_input = values['end'].strip()
            folder = values['folder'].strip()
            sources = values['sources']
            if not sources or "全部" in sources:
                selected_sources = list(INFO_SOURCES.keys())
            else:
                selected_sources = sources
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
                window['-STATUS-'].update("日期格式错误，请输入YYYY-MM-DD格式")
                continue
            if start_date > end_date:
                window['-STATUS-'].update("起始日期不能晚于结束日期！")
                continue
            if not folder:
                window['-STATUS-'].update("请选择或输入保存文件夹路径！")
                continue
            try:
                os.makedirs(folder, exist_ok=True)
            except Exception as e:
                window['-STATUS-'].update(f"创建目录失败: {e}")
                continue
            window['-STATUS-'].update("开始采集...")
            window['-PROGRESS-'].update_bar(0, len(selected_sources))
            window.refresh()
            all_results = []
            for idx, name in enumerate(selected_sources, 1):
                print(f"[{name}] 开始采集...")
                results = collect_from_source(name, start_dt=start_date, end_dt=end_date, save_folder=folder)
                if results:
                    print(f"[{name}] 完成，共 {len(results)} 篇。")
                    for i, item in enumerate(results, 1):
                        print(f"  {i}. {item['title']}")
                else:
                    print(f"[{name}] 无数据或采集失败")
                all_results.extend(results)
                window['-PROGRESS-'].update_bar(idx)
                window.refresh()
            window['-STATUS-'].update(f"全部采集完成，共{len(all_results)}篇。")
    window.close()

if __name__ == "__main__":
    main_gui()
