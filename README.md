# Sina-Finance-Spider

## 1. Introduction

爬取上市公司金融信息：股票信息、研究报告、相关新闻、招股说明书。

- 研究报告。爬取字段: industry_code, stock_code, stock_name, company_name, stock_exchange, research_title, research_time, research_link
- 相关新闻。爬取字段：stock_code, company_name, stock_name, news_title, news_time, news_link.

- 招股说明书。下载上市公司招股说明书pdf到指定路径。


## 2. Environment 

Python=3.8+

## 3. Structure

- code

  - stock_research_report_spider.py
    - 爬取上市公司研究报告。
  - stock_news_info_spider.py
    - 爬取上市公司相关新闻信息。
  - stock_news_content_spider.py
    -  根据上市公司相关新闻链接爬取新闻内容。
  - stock_prospectus_sipder.py
    - 爬取上市公司招股说明书。

## 4. Contact

Created by [OxCsea](https://github.com/OxCsea) - feel free to reach out!

> https://t.me/magic_Cxsea