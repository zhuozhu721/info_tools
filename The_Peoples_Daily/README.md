# 人民日报电子版下载与关键词检索工具

本文件夹包含两个主要脚本，分别用于自动下载人民日报电子版 PDF 及批量检索文章标题关键词并导出为 Word 文档。

## 1. pdf_download.py

- **功能**：自动下载指定日期的人民日报电子版 PDF，并自动合并为单个文件。
- **支持日期格式**：`YYYYMMDD`，可通过命令行参数 `-date` 或 `--date` 指定日期，默认下载当天报纸。
- **使用方法**：
  ```
  依赖库：pip install requests PyPDF2
  运行方式：python pdf_download.py -date 20240101
  ```

- **下载结果**：保存在 `./newspaper` 文件夹下，文件名如 `People's.Daily.20240101.pdf`。

## 2. keyword_search_extract.py

- **功能**：批量抓取人民日报电子版指定日期区间的所有文章，支持按关键词检索标题并将匹配文章导出为 Word 文档（.docx）。
- **支持自定义日期区间与多个关键词**（英文逗号分隔）。
- **使用方法**：

  ```
  依赖库：pip install requests beautifulsoup4 python-docx
  运行方式：python keyword_search_extract.py
  ```

  按提示输入起止日期和关键词，脚本会自动下载并筛选，结果按关键词分类保存。

## 注意事项

- 仅供学习与非盈利个人场合使用，禁止用于商业用途。
- 运行脚本前请确保已安装所需依赖库。
- 若遇到下载失败或网页结构变动，可关注脚本更新。

---