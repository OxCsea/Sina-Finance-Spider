# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 16:41:04 2021

"""
import requests
import re
from fake_useragent import UserAgent
import json
import csv
import time
import pandas as pd
import os
from bs4 import BeautifulSoup

# 生成目录
def generatePath(path):
    if not os.path.exists(path):
        os.mkdir(path)

def get_header():
    ua = UserAgent(verify_ssl=False)
    return {'User-Agent': ua.random}

def get_proxy():
    proxypool_url = 'http://127.0.0.1:5555/random'
    proxies = {'http': 'http://' + requests.get(proxypool_url).text.strip()}
    return proxies

"""
爬取公司研究报告基本信息
"""
def get_compReasearch(outpath,industry_code,stock_code,stock_name,company_name,stock_exchange):
    page = 1
    resData = pd.DataFrame(columns=("industry_code","stock_code","stock_name","company_name", \
                        "stock_exchange",'research_title','research_time','research_link'))
    research_title = []
    research_time = []
    research_link =[]
    fcnt = 0
    # requests.adapters.DEFAULT_RETRIES = 5
    while(True):
        baseUrl = 'http://stock.finance.sina.com.cn/stock/go.php/vReport_List/kind/search/index.phtml?symbol='+str(stock_code)+'&t1=all&p='+str(page)
        try:
            r = requests.get(baseUrl, headers=get_header())
            #cont -- content
            cont = r.text
            exist = re.findall(r'没有找到相关内容..',cont)
            if exist == []:
                tmpDic = {}
                plink = r'<a target=\"_blank\" title=\".*?\" href=\"(.*?)\">'
                link = re.findall(plink,cont)
                ptitle = r'<a target=\"_blank\" title=\"(.*?)\" href=.*?>'
                title = re.findall(ptitle,cont)
                ptime = r'<a target=\"_blank\" title=\".*?\" href=.*?>[\s\S]*?<td>(\d{4}-\d{2}-\d{2})</td>'
                times = re.findall(ptime,cont)
                research_title.extend(title)
                research_time.extend(times)
                research_link.extend(link)
                page += 1
                # time.sleep(300)
            else:
                break
        except:
            print(str(stock_code)+'-----------'+str(page)+'-----'+str(baseUrl))
            time.sleep(5)
            fcnt += 1
            if (fcnt >=3 ):
                page += 1
                fcnt = 0
            continue
    #上述操作完成后应该'news_title','news_time','news_link'存储了那家公司所有新闻信息
    listlen = len(research_time)
#    stock_name = [stockName]*listlen
    #对信息进行处理
    tmpDic = {
             "industry_code":[industry_code]*listlen,
             "stock_code":[stock_code]*listlen,
             "stock_name":[stock_name]*listlen,
             "company_name":[company_name]*listlen,
             "stock_exchange":[stock_exchange]*listlen,
             "research_title":research_title, 
             "research_time":research_time,
             "research_link":research_link
             }
    resdf = pd.DataFrame(tmpDic)
    resdf['research_link'] = 'http:' + resdf['research_link'].astype('str')
    resdf = resdf.sort_values(by = "research_time",ascending = False)
    resdf.to_csv(outpath,mode='a', header=False,index = False)

    jsonDic = { "research_title":research_title, 
             "research_time":research_time,
             "research_link":research_link
             }
    jsdf = pd.DataFrame(jsonDic)
    jsdf['research_link'] = 'http:' + jsdf['research_link'].astype('str')
    jsdf = jsdf.sort_values(by = "research_time",ascending = False)
    #将一家公司的所有研究报告转成一个list
    reps = [jsdf.to_dict(orient="records")]
    #一家公司的所有信息
    resDic_comp = {
            "industry_code":industry_code,
            "stock_code":stock_code,
            "stock_name":stock_name,
            "company_name":company_name,
            "stock_exchange":stock_exchange,
            "research":reps, 
            }
    #一家公司所有信息转成一个df
    resDf_comp = pd.DataFrame(resDic_comp)
    indpath = f'../data/research_json/'+f'{industry_code}/'
    stdpath = indpath+f'{stock_code}'+'.json'
    if not os.path.exists(indpath):
        generatePath(indpath)
    if os.path.exists(stdpath):
        return
    else:
        resDf_comp.to_json(stdpath,orient="records",force_ascii=False)
    print("完成"+str(stock_code))

# 生成目录
def generatePath(path):
    if not os.path.exists(path):
        os.mkdir(path)

"""
爬取公司研究报告的内容
"""
def get_compNews(compDf_all):

    for index, row in compDf_all.iterrows():       
        filename = ''
        industry_code = row['industry_code']
        stock_code = row['stock_code']
        news_title = row['research_title']
        news_link = row['research_link']
        try:
            r = requests.get(news_link, headers=get_header())
            r.encoding = r.apparent_encoding
            cont = r.text
            # 你的 IP 存在异常访问
            exist = re.findall(r'拒绝访问',cont)
            if exist != []:
                print(str(industry_code)+'\t'+str(stock_code)+'\t'+str(news_title)+'\t'+"拒绝访问")
                continue
            soup = BeautifulSoup(cont,'html.parser')
            indpath = f'../data/research/'+f'{industry_code}/'
            stdpath = indpath+f'{stock_code}/'
            if not os.path.exists(indpath):
                generatePath(indpath)
            if not os.path.exists(stdpath):
                generatePath(stdpath)
            filename = stdpath+f'{news_title}.txt'
            if os.path.exists(filename):
                continue
            else:
                article = soup.select('.blk_container p')
                if article == []:
                    time.sleep(50)
                with open(filename,'a',encoding='utf8') as f:
                    for p in article:
                        f.write(p.text)
                print(str(stock_code)+'\t'+str(news_title)+'\t'+"finish it")
        except:
            print(str(stock_code)+'\t'+str(news_title)+'\t'+"Connection refused by the server..")
            time.sleep(50)
            continue
    print('finish all research report download')

if __name__ == '__main__':
    stock = pd.read_csv('../data/stock_index.csv',dtype=str)
    info_datapath = '../data/stock_research_info.csv'
    for index, row in stock.iterrows():
        get_compReasearch(info_datapath,row['industry_code'],row['stock_code'],row['short_name'],row['company_name'],row['stock_exchange'])
    print('finish crawling all research report url basic info')

    compDf_all = pd.read_csv(info_datapath, dtype=str)
    get_compNews(compDf_all)
    print('finish crawling all research report content')  
