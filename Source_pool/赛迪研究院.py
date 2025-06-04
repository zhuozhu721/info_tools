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

            results.append({
                "date": date,
                "title": title,
                "url": detail_url,
                "source": "赛迪研究院"
            })

        all_earlier = all(
            datetime.strptime(item.get("showDate", ""), "%Y-%m-%d") < start_dt
            for item in items if item.get("showDate", "")
        )
        if all_earlier:
            break

        page += 1

    return results