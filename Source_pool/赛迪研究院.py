import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta

# 默认时间范围为最近一周
end_dt = datetime.today()
start_dt = end_dt - timedelta(days=7)
start_date = start_dt.strftime("%Y-%m-%d")
end_date = end_dt.strftime("%Y-%m-%d")

# 文件夹名包含日期范围
save_dir = f"赛迪PDF下载_{start_date}_{end_date}"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

url = "https://www.ccidgroup.com/system/resource/sdyjs/getListData.jsp"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.ccidgroup.com/sdyjcg.htm"
}

page = 1
while True:
    data = {
        "owner": "1661492338",
        "ownerName": "dzxxyjy",
        "currentnum": page,   # 页码
        "pagenum": 12,        # 每页条数
        "newskeycode": "",
        "labalbq": "",
        "lxlababq": "",
        "lylababq": ""
    }
    response = requests.post(url, data=data, headers=headers)
    try:
        result = response.json()
    except Exception as e:
        print("解析JSON失败，原始内容：", response.text)
        break

    items = result.get("data", [])
    if not items:
        print("没有更多数据，结束。")
        break

    has_in_range = False

    for item in items:
        date = item.get("showDate", "")
        title = item.get("title", "")
        detail_url = item.get("url", "")
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
        except Exception:
            print(f"日期格式错误，跳过：{date} {title}")
            continue
        if not (start_dt <= dt <= end_dt):
            continue

        has_in_range = True
        print(f"{date}  {title}  {detail_url}")

        # 下载PDF部分
        try:
            resp = requests.get(detail_url, headers=headers, timeout=10)
            resp.encoding = resp.apparent_encoding
            soup = BeautifulSoup(resp.text, "html.parser")
            pdf_link = None

            # 优先查找 download.jsp 相关链接
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "download.jsp" in href:
                    if not href.startswith("http"):
                        href = "https://www.ccidgroup.com" + href.lstrip(".")
                    pdf_link = href
                    print(f"  检查到download.jsp下载链接: {pdf_link}")
                    break
                if href.lower().endswith(".pdf"):
                    if not href.startswith("http"):
                        href = "https://www.ccidgroup.com" + href
                    pdf_link = href
                    print(f"  检查到.pdf下载链接: {pdf_link}")
                    break

            if pdf_link:
                print(f"  正在下载PDF: {pdf_link}")
                pdf_resp = requests.get(pdf_link, headers=headers, timeout=20)
                filename = f"{date}_{title}.pdf".replace("/", "_").replace("\\", "_").replace(":", "_")
                filepath = os.path.join(save_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(pdf_resp.content)
                print(f"  已保存为: {filepath}")
            else:
                print("  未找到PDF或download.jsp链接，尝试查找所有含.pdf的字符串...")
                pdf_candidates = [s for s in resp.text.split('"') if ".pdf" in s]
                if pdf_candidates:
                    print("  可能的PDF链接：", pdf_candidates)
                else:
                    print("  页面源码中也未发现.pdf")
        except Exception as e:
            print(f"  下载失败: {e}")

    # 判断是否全部早于起始日期，若是则退出
    all_earlier = all(
        datetime.strptime(item.get("showDate", ""), "%Y-%m-%d") < start_dt
        for item in items if item.get("showDate", "")
    )
    if all_earlier:
        print("本页及以后都早于起始日期，结束。")
        break

    page += 1