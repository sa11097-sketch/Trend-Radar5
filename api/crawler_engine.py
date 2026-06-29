# api/crawler_engine.py (精准时间提取版)
import requests
from bs4 import BeautifulSoup

def fetch_all_news():
    all_news = []
    # 使用 Python 的 requests 库 [cite: 1] 和 beautifulsoup4 [cite: 1] 进行抓取
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    sources = [
        {"name": "华尔街见闻", "url": "https://api.wallstreetcn.com/v1/livenews?channel=global", "type": "json"},
        {"name": "金融时报", "url": "https://www.ft.com/?format=rss", "type": "rss"},
        {"name": "路透社", "url": "https://www.reuters.com/business/", "type": "html", "selector": 'a[data-testid="Heading"]', "time_selector": 'time'},
        {"name": "雅虎财经", "url": "https://finance.yahoo.com/news/", "type": "html", "selector": 'h3 > a', "time_selector": 'time'},
        {"name": "CNBC", "url": "https://www.cnbc.com/finance/", "type": "html", "selector": '.Card-title', "time_selector": 'time'}
    ]

    for source in sources:
        try:
            response = requests.get(source["url"], headers=headers, timeout=15)
            if response.status_code != 200: continue

            if source["type"] == "json":
                data = response.json()
                for item in data.get('data', {}).get('items', [])[:3]:
                    all_news.append({"source": source["name"], "title": item.get('title'), "time": "近期"})
            elif source["type"] == "rss":
                soup = BeautifulSoup(response.content, features="xml")
                for item in soup.find_all('item')[:3]:
                    title = item.find('title').text if item.find('title') else "无标题"
                    pub_date = item.find('pubDate').text if item.find('pubDate') else "未知"
                    # 清理RSS时间格式，只保留关键部分
                    pub_date = pub_date.split(', ')[-1].replace(' GMT', '') if ',' in pub_date else pub_date
                    all_news.append({"source": source["name"], "title": title, "time": pub_date})
            elif source["type"] == "html":
                soup = BeautifulSoup(response.content, 'html.parser')
                # 尝试获取标题的同时尝试获取对应的时间标签
                elements = soup.select(source["selector"])
                for el in elements[:3]:
                    title = el.text.strip()
                    # 尝试寻找父级或同级的时间标签
                    time_tag = el.find_next('time') or el.find_parent().find('time')
                    pub_time = time_tag.get('datetime') if time_tag and time_tag.has_attr('datetime') else "网页抓取"
                    all_news.append({"source": source["name"], "title": title, "time": pub_time[:16].replace('T', ' ')})
        except Exception as e:
            print(f"采集异常: {e}")
    return all_news
