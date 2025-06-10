
import importlib
import os
from datetime import datetime, timedelta

INFO_SOURCES = {
    "赛迪研究院": "Source_pool.赛迪研究院",
    "国务院发展研究中心": "Source_pool.国务院发展研究中心",
    "白宫行政令": "Source_pool.白宫行政令",
    "MIT科技评论10大热点": "Source_pool.MIT_Tech",
}

def collect_from_source(source_name, start_dt, end_dt, save_folder=None):
    try:
        module_path = INFO_SOURCES[source_name]
        print(f"[调试] 导入模块: {module_path}")
        module = importlib.import_module(module_path)
        if hasattr(module, "collect"):
            # 只对人民日报等支持关键词的采集源传递keywords
            if "MIT科技评论" in source_name or "MIT Tech" in source_name:
                print(f"[调试] 调用 {source_name} collect(save_folder={save_folder})")
                data = module.collect(save_folder=save_folder)
            else:
                print(f"[调试] 调用 {source_name} collect(start_dt, end_dt, save_folder={save_folder})")
                data = module.collect(start_dt=start_dt, end_dt=end_dt, save_folder=save_folder)
            print(f"[调试] {source_name} 返回 {len(data) if data else 0} 条数据")
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
    start_dt = end_dt - timedelta(days=15)
    # 默认保存到桌面download文件夹
    default_folder = os.path.join(os.path.expanduser("~"), "Desktop", "download")
    all_results = []
    for name in INFO_SOURCES:
        print(f"[{name}] 开始采集...")
        # 这里始终用default_folder作为保存目录
        results = collect_from_source(name, start_dt=start_dt, end_dt=end_dt, save_folder=default_folder)
        if results:
            print(f"[{name}] 完成，共 {len(results)} 篇。")
            for idx, item in enumerate(results, 1):
                print(f"  {idx}. {item.get('title', '[无标题]')}")
        else:
            print(f"[{name}] 无数据或采集失败")
        all_results.extend(results)
    print("全部采集完成。共%d篇。" % len(all_results))

if __name__ == "__main__":
    main()