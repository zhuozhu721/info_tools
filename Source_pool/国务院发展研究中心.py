import requests
from datetime import datetime
import time

def collect(start_dt, end_dt):
    results = []
    url = "https://www.drc.gov.cn/Json/GetPageDocuments.ashx"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.drc.gov.cn/Leaf.aspx?leafid=1338",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    page = 1
    while True:
        params = {
            "chnid": 378,
            "leafid": 1338,
            "page": page,
            "pagesize": 10,
            "sublen": 21,
            "sumlen": 230,
            "keyword": "",
            "expertid": 0
        }
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code != 200:
                break
            data = response.json()
        except Exception as e:
            print(f"国务院发展研究中心第{page}页请求失败: {e}")
            break

        if not (isinstance(data, list) and len(data) > 0 and "rows" in data[0]):
            break

        for item in data[0]["rows"]:
            date_str = item.get("DelivedDate", "")[:10]
            title = item.get("Subject", "")
            url_detail = item.get("Url", "")
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                continue
            if start_dt <= dt <= end_dt:
                results.append({
                    "date": date_str,
                    "title": title,
                    "url": url_detail,
                    "source": "国务院发展研究中心",
                    "category": "",
                    "summary": ""
                })

        all_earlier = all(
            datetime.strptime(item.get("DelivedDate", "")[:10], "%Y-%m-%d") < start_dt
            for item in data[0]["rows"] if item.get("DelivedDate", "")
        )
        if all_earlier:
            break

        page += 1
        time.sleep(1)

    return results