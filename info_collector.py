import importlib
from datetime import datetime, timedelta

INFO_SOURCES = {
    "赛迪研究院": "Source_pool.赛迪研究院",
    "国务院发展研究中心": "Source_pool.国务院发展研究中心",
    "白宫行政令": "Source_pool.白宫行政令",
}

def collect_from_source(source_name, start_dt, end_dt):
    try:
        module_path = INFO_SOURCES[source_name]
        module = importlib.import_module(module_path)
        if hasattr(module, "collect"):
            data = module.collect(start_dt=start_dt, end_dt=end_dt)
            return data
        else:
            print(f"{source_name} 未实现 collect() 方法")
            return []
    except Exception as e:
        print(f"导入或采集 {source_name} 时出错: {e}")
        return []

def main():
    print("信息搜集工具 - 汇总页面")
    print("=" * 40)
    end_dt = datetime.today()
    start_dt = end_dt - timedelta(days=15)
    print(f"统一采集时间范围: {start_dt.date()} ~ {end_dt.date()}")
    all_results = []
    for name in INFO_SOURCES:
        print(f"\n【{name}】")
        results = collect_from_source(name, start_dt=start_dt, end_dt=end_dt)
        if results:
            print(f"共采集到 {len(results)} 条信息：")
            for item in results:
                print(f"- {item['date']} | {item['title']} | {item['url']}")
        else:
            print("无数据或采集失败")
        all_results.extend(results)
    print("\n信息汇总完成，共采集到%d条信息。" % len(all_results))

if __name__ == "__main__":
    main()