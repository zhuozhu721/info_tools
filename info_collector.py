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
    print("信息采集进度：")
    end_dt = datetime.today()
    start_dt = end_dt - timedelta(days=10)
    all_results = []
    for name in INFO_SOURCES:
        print(f"[{name}] 开始采集...")
        results = collect_from_source(name, start_dt=start_dt, end_dt=end_dt)
        if results:
            print(f"[{name}] 完成，共 {len(results)} 篇。")
            for idx, item in enumerate(results, 1):
                print(f"  {idx}. {item['title']}")
        else:
            print(f"[{name}] 无数据或采集失败")
        all_results.extend(results)
    print("全部采集完成。共%d篇。" % len(all_results))

if __name__ == "__main__":
    main()