import requests
from datetime import datetime, timedelta
import time

# 默认时间范围为最近一周
end_dt = datetime.today()
start_dt = end_dt - timedelta(days=7)
startdate = start_dt.strftime("%Y-%m-%d")
enddate = end_dt.strftime("%Y-%m-%d")

url = "https://www.drc.gov.cn/Json/GetPageDocuments.ashx"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.drc.gov.cn/Leaf.aspx?leafid=1338",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9"
    # 如遇403可加Cookie
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
    response = requests.get(url, params=params, headers=headers)
    print(f"请求第{page}页，状态码：{response.status_code}")
    if response.status_code != 200:
        print("请求失败，跳出循环")
        break
    try:
        data = response.json()
    except Exception as e:
        print(f"第{page}页解析JSON失败，原始内容：{response.text[:200]}")
        break

    if not (isinstance(data, list) and len(data) > 0 and "rows" in data[0]):
        break

    has_article_in_range = False

    for item in data[0]["rows"]:
        date_str = item.get("DelivedDate", "")[:10]
        title = item.get("Subject", "")
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            continue
        if start_dt <= dt <= end_dt:
            print(f"{date_str}  {title}")
            has_article_in_range = True

    # 如果本页所有文章都早于起始日期，直接退出
    all_earlier = all(
        datetime.strptime(item.get("DelivedDate", "")[:10], "%Y-%m-%d") < start_dt
        for item in data[0]["rows"] if item.get("DelivedDate", "")
    )
    if all_earlier:
        print("本页及以后都早于起始日期，结束。")
        break

    page += 1
    time.sleep(1)