# api/crawler_engine.py (全量覆盖版)
import requests
from bs4 import BeautifulSoup

def fetch_all_news():
    """从 6 大财经媒体 RSS 源获取新闻"""
    all_news = []
    
    # 定义来源配置 (RSS 地址)
    sources = [
        {"name": "华尔街见闻", "url": "https://api.wallstreetcn.com/v1/livenews?channel=global", "type": "json"},
        {"name": "CNBC", "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000311", "type": "rss"},
        {"name": "财新网", "url": "https://feeds.caixin.com/rss/headlines.xml", "type": "rss"},
        {"name": "金融时报", "url": "https://www.ft.com/?format=rss", "type": "rss"},
        {"name": "路透社", "url": "https://www.reutersagency.com/feed/?post_type=best", "type": "rss"},
        {"name": "雅虎财经", "url": "https://finance.yahoo.com/rss/headline", "type": "rss"}
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    for source in sources:
        try:
            response = requests.get(source["url"], headers=headers, timeout=8)
            if response.status_code != 200:
                continue

            if source["type"] == "json":
                # 解析华尔街见闻 JSON
                data = response.json()
                for item in data.get('data', {}).get('items', [])[:5]:
                    all_news.append({"source": source["name"], "title": item.get('title')})
            
            else:
                # 解析 RSS (XML)
                soup = BeautifulSoup(response.content, 'xml')
                for item in soup.find_all('item')[:5]:
                    title = item.find('title').text if item.find('title') else "无标题"
                    all_news.append({"source": source["name"], "title": title})
                    
        except Exception as e:
            print(f"!!! {source['name']} 采集异常: {e}")

    print(f">>> 成功汇总采集到 {len(all_news)} 条新闻")
    return all_news
