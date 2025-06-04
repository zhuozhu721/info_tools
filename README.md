# 信息搜集工具（info_collector）

## 简介

本工具用于自动化采集多个权威信息源（如赛迪研究院、国务院发展研究中心、白宫行政令等）最新发布的报告、政策、新闻等内容，并统一输出，便于信息整合与分析。架构支持后续灵活扩展更多信息源。

---

## 目录结构

```
info_tools/
├── info_collector.py                # 主控程序，统一调度各信息源采集
└── Source_pool/
    ├── 赛迪研究院.py                # 赛迪研究院采集模块
    ├── 国务院发展研究中心.py        # 国务院发展研究中心采集模块
    ├── 白宫行政令.py                # 白宫行政令采集模块
    └── __init__.py                  # 包初始化文件
```

---

## 使用方法

1. **安装依赖**

   需 Python 3.7+，并安装相关依赖：

   ```bash
   pip install requests beautifulsoup4 selenium
   ```

   如需采集白宫行政令，请确保本地已安装 Chrome 浏览器及对应版本的 chromedriver，并在 `白宫行政令.py` 中配置好路径。

2. **运行主程序**

   ```bash
   python info_collector.py
   ```

   程序将自动采集最近 15 天（可在代码中调整）的信息，并按来源输出结果。

---

## 扩展信息源

如需增加新的信息源，只需在 `Source_pool/` 目录下新增模块，并实现如下接口：

```python
def collect(start_dt, end_dt):
    # 返回一个信息字典列表，每条字典包含至少 date/title/url/source 字段
    return [
        {"date": "...", "title": "...", "url": "...", "source": "信息源名称"},
        ...
    ]
```
并在 `info_collector.py` 的 `INFO_SOURCES` 字典中注册即可。

---

## 输出示例

```
信息搜集工具 - 汇总页面
========================================
统一采集时间范围: 2025-05-20 ~ 2025-06-04

【赛迪研究院】
共采集到 24 条信息：
- 2025-05-29 | 具身智能产业发展趋势研究及安全威胁分析报告 | http://www.ccidgroup.com/info/1207/43858.htm
...

【国务院发展研究中心】
共采集到 4 条信息：
- 2025-06-03 | 赵峥：持续推进城市更新行动 建设高品质生活空间 | https://www.drc.gov.cn/...
...

【白宫行政令】
共采集到 1 条信息：
- 2025-06-01 | Ordering the Reform of the Nuclear Regulatory Commission | https://www.whitehouse.gov/...
...

信息汇总完成，共采集到29条信息。
```

---

## 注意事项

- 部分信息采集需配置科学上网环境。
- 部分信息采集可能因反爬虫机制被屏蔽。
- 若需调整采集时间范围，请修改 `info_collector.py` 中的 `start_dt` 和 `end_dt`。
- 若遇到网络或接口变动导致采集失败，请检查相关模块实现或接口返回格式。
