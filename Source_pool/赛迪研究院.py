import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta

def collect(start_dt, end_dt):
    results = []
    url = "https://www.ccidgroup.com/system/resource/sdyjs/getListData.jsp"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.ccidgroup.com/sdyjcg.htm"
    }
    page = 1

    # PDF保存目录，分信息源子目录
    pdf_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../download/赛迪研究院'))
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    while True:
        data = {
            "owner": "1661492338",
            "ownerName": "dzxxyjy",
            "currentnum": page,
            "pagenum": 12,
            "newskeycode": "",
            "labalbq": "",
            "lxlababq": "",
            "lylababq": ""
        }
        try:
            response = requests.post(url, data=data, headers=headers, timeout=10)
            result = response.json()
        except Exception as e:
            print(f"赛迪研究院第{page}页请求失败: {e}")
            break

        items = result.get("data", [])
        if not items:
            break

        for item in items:
            date = item.get("showDate", "")
            title = item.get("title", "")
            detail_url = item.get("url", "")
            try:
                dt = datetime.strptime(date, "%Y-%m-%d")
            except Exception:
                continue
            if not (start_dt <= dt <= end_dt):
                continue

            # 查找并下载所有 download.jsp 相关PDF
            pdf_downloaded = False
            pdf_paths = []
            if detail_url and detail_url.startswith("http"):
                try:
                    detail_resp = requests.get(detail_url, headers=headers, timeout=10)
                    detail_resp.encoding = detail_resp.apparent_encoding
                    soup = BeautifulSoup(detail_resp.text, "html.parser")
                    # 优先查找 href 中包含 download.jsp 的 <a> 标签
                    for idx, a in enumerate(soup.find_all("a", href=True), 1):
                        href = a["href"]
                        if "download.jsp" in href:
                            pdf_url = href
                            if not pdf_url.startswith("http"):
                                pdf_url = requests.compat.urljoin(detail_url, pdf_url)
                            # 尝试获取文件名
                            link_text = a.get_text(strip=True) or f"{title[:30]}_{idx}"
                            ext = ".pdf" if ".pdf" in pdf_url.lower() else ""
                            pdf_name = f"赛迪研究院_{date}_{link_text}{ext}".replace("/", "_").replace("\\", "_").replace(":", "_")
                            pdf_path = os.path.join(pdf_dir, pdf_name)
                            try:
                                pdf_resp = requests.get(pdf_url, headers=headers, timeout=20)
                                with open(pdf_path, "wb") as f:
                                    f.write(pdf_resp.content)
                                print(f"已下载PDF: {pdf_path}")
                                pdf_downloaded = True
                                pdf_paths.append(pdf_path)
                            except Exception as e:
                                print(f"下载PDF失败: {pdf_url}，原因: {e}")
                except Exception as e:
                    print(f"获取详情页失败: {detail_url}，原因: {e}")

            results.append({
                "date": date,
                "title": title,
                "url": detail_url,
                "source": "赛迪研究院",
                "pdf_downloaded": pdf_downloaded,
                "pdf_paths": pdf_paths
            })

        all_earlier = all(
            datetime.strptime(item.get("showDate", ""), "%Y-%m-%d") < start_dt
            for item in items if item.get("showDate", "")
        )
        if all_earlier:
            break

        page += 1

    return results