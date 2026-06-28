# api/crawler_engine.py (更新源与时间提取版)
import requests
from bs4 import BeautifulSoup

def fetch_all_news():
    all_news = []
    # 使用更通用的浏览器标识，减少被拦截概率
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    # 更新为更稳定的源地址
    sources = [
        {"name": "华尔街见闻", "url": "https://api.wallstreetcn.com/v1/livenews?channel=global", "type": "json"},
        {"name": "路透社", "url": "https://www.reuters.com/business/feed", "type": "rss"}, # 替换了地址
        {"name": "雅虎财经", "url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=yahoofinance&region=US&lang=en-US", "type": "rss"}, # 替换了地址
        {"name": "CNBC", "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000311", "type": "rss"},
        {"name": "金融时报", "url": "https://www.ft.com/?format=rss", "type": "rss"}
    ]

    for source in sources:
        try:
            response = requests.get(source["url"], headers=headers, timeout=12)
            if response.status_code != 200:
                continue

            if source["type"] == "json":
                data = response.json()
                for item in data.get('data', {}).get('items', [])[:5]:
                    # JSON 源有时没有直接的时间，用当前占位
                    all_news.append({"source": source["name"], "title": item.get('title'), "time": "近期"})
            else:
                soup = BeautifulSoup(response.content, features="xml")
                for item in soup.find_all('item')[:5]:
                    title = item.find('title').text if item.find('title') else "无标题"
                    # 提取发布时间
                    pub_date = item.find('pubDate').text if item.find('pubDate') else "未知时间"
                    all_news.append({"source": source["name"], "title": title, "time": pub_date})
                    
        except Exception as e:
            print(f"!!! {source['name']} 采集异常: {e}")

    return all_news
