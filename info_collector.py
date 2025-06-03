import importlib
from datetime import datetime, timedelta

INFO_SOURCES = {
    "赛迪研究院": "Source_pool.赛迪研究院",
    # 后续可继续添加其它信息源
}

def collect_from_source(source_name, start_dt=None, end_dt=None):
    module_path = INFO_SOURCES[source_name]
    module = importlib.import_module(module_path)
    if hasattr(module, "collect"):
        return module.collect(start_dt=start_dt, end_dt=end_dt)
    else:
        print(f"{source_name} 未实现 collect() 方法")
        return []

def main():
    print("信息搜集工具 - 汇总页面")
    print("=" * 40)
    # 默认最近一周
    end_dt = datetime.today()
    start_dt = end_dt - timedelta(days=6)
    all_results = []
    for name in INFO_SOURCES:
        print(f"\n正在收集: {name}")
        results = collect_from_source(name, start_dt=start_dt, end_dt=end_dt)
        if results:
            for item in results:
                print(f"[{item['source']}] {item['date']} {item['title']} {item['url']}")
            all_results.extend(results)
        else:
            print(f"{name} 无数据或采集失败")
    print("\n信息汇总完成，共采集到%d条信息。" % len(all_results))

if __name__ == "__main__":
    main()