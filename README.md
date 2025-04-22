# 微博爬虫与数据分析工具

这是一个功能完整的微博爬虫和数据分析工具，可以爬取指定用户的微博内容并进行多维度分析，生成直观的可视化报告。

## 功能特点

- **微博爬取**：通过用户ID爬取指定微博用户的全部或部分微博内容
- **数据存储**：将爬取的微博保存为文本文件，包含发布时间、微博内容、转发内容、图片链接等
- **多维度分析**：
  - 时间分布分析：按日期、小时、星期分析发布规律
  - 内容分析：生成词云和关键词提取
  - 引用人物分析：统计微博中引用的人物及频次
  - 图片使用分析：分析带图微博比例和图片数量分布
- **可视化报告**：自动生成HTML格式的分析报告，包含丰富的图表

## 环境要求

- Python 3.6+
- 依赖库：requests, jieba, matplotlib, numpy, wordcloud, pandas, seaborn

## 安装方法

1. 克隆或下载本仓库到本地
2. 安装所需依赖：

```bash
pip install requests jieba matplotlib numpy wordcloud pandas seaborn
```

3. 确保您的系统中安装了中文字体（例如SimHei）

## 使用方法

### 1. 爬取微博

```bash
python weibo_crawler.py 用户ID --cookie-file cookie.txt [--max-pages 页数]
```

参数说明：
- `用户ID`：必填，微博用户的数字ID
- `--cookie-file`：可选，包含登录cookie的文件路径
- `--max-pages`：可选，限制爬取的页数

例如：
```bash
python weibo_crawler.py 1004524612 --cookie-file cookie.txt --max-pages 10
```

### 2. 分析微博数据

```bash
python weibo_analysis.py
```

默认会分析名为`用户ID_weibos.txt`的文件，并生成以下分析结果：
- time_distribution.png：时间分布分析
- wordcloud.png：词云图
- keywords.png：关键词排名
- quotes.png：引用人物分析
- image_usage.png：图片使用情况
- image_count.png：图片数量分布
- weibo_analysis_report.html：完整HTML分析报告

## 分析报告示例

生成的HTML报告包含以下内容：
- 用户基本信息
- 微博发布时间分析
- 内容关键词与词云
- 引用人物统计
- 图片使用情况

## 注意事项

1. 爬取微博需要登录cookie，请确保您有合法的登录凭证
2. 爬取间隔已设置为1秒，请勿修改过小导致IP被封
3. 请遵守微博平台的使用条款，不要过度爬取数据
4. 本工具仅供学习和研究使用

## 文件说明

- `weibo_crawler.py`：微博爬虫主程序
- `weibo_analysis.py`：微博数据分析程序
- `stopwords.txt`：中文停用词表
- `cookie.txt`：存放微博登录cookie
- `*_weibos.txt`：爬取的微博数据文件
- `*.png`：生成的可视化图表
- `weibo_analysis_report.html`：生成的HTML分析报告

## 许可证

本项目仅供学习和个人研究使用，请勿用于商业目的。 