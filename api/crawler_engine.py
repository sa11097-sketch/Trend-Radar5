# api/crawler_engine.py (时间对齐版)
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

def get_beijing_time():
    """获取东八区当前时间"""
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(tz).strftime('%m-%d %H:%M')

def fetch_all_news():
    """多源混合采集：HTML/RSS/JSON 统一时间戳"""
    all_news = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.google.com/"
    }

    sources = [
        {"name": "华尔街见闻", "url": "https://api.wallstreetcn.com/v1/livenews?channel=global", "type": "json"},
        {"name": "金融时报", "url": "https://www.ft.com/?format=rss", "type": "rss"},
        {"name": "路透社", "url": "https://www.reuters.com/business/", "type": "html", "selector": 'a[data-testid="Heading"]'},
        {"name": "雅虎财经", "url": "https://finance.yahoo.com/news/", "type": "html", "selector": 'h3 > a'},
        {"name": "CNBC", "url": "https://www.cnbc.com/finance/", "type": "html", "selector": '.Card-title'}
    ]

    print(f">>> 开始执行采集，当前时间: {get_beijing_time()}")

    for source in sources:
        try:
            response = requests.get(source["url"], headers=headers, timeout=15)
            if response.status_code != 200: continue

            count = 0
            if source["type"] == "json":
                data = response.json()
                for item in data.get('data', {}).get('items', [])[:3]:
                    all_news.append({"source": source["name"], "title": item.get('title'), "time": get_beijing_time()})
                    count += 1
            elif source["type"] == "rss":
                soup = BeautifulSoup(response.content, features="xml")
                for item in soup.find_all('item')[:3]:
                    title = item.find('title').text if item.find('title') else "无标题"
                    all_news.append({"source": source["name"], "title": title, "time": get_beijing_time()})
                    count += 1
            elif source["type"] == "html":
                soup = BeautifulSoup(response.content, 'html.parser')
                elements = soup.select(source["selector"])
                for el in elements[:3]:
                    title = el.text.strip()
                    if len(title) > 5:
                        all_news.append({"source": source["name"], "title": title, "time": get_beijing_time()})
                        count += 1
            print(f"  -> {source['name']} 已采集")
        except Exception as e:
            print(f"  -> {source['name']} 异常: {e}")

    return all_news
