# api/crawler_engine.py
import requests
from bs4 import BeautifulSoup

def fetch_all_news():
    all_news = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    sources = [
        {"name": "华尔街见闻", "url": "https://api.wallstreetcn.com/v1/livenews?channel=global", "type": "json"},
        {"name": "CNBC", "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000311", "type": "rss"},
        {"name": "财新网", "url": "https://feeds.caixin.com/rss/headlines.xml", "type": "rss"},
        {"name": "金融时报", "url": "https://www.ft.com/?format=rss", "type": "rss"},
        {"name": "路透社", "url": "https://www.reutersagency.com/feed/?post_type=best", "type": "rss"},
        {"name": "雅虎财经", "url": "https://finance.yahoo.com/rss/headline", "type": "rss"}
    ]

    for source in sources:
        try:
            response = requests.get(source["url"], headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"!!! {source['name']} 响应错误: {response.status_code}")
                continue

            if source["type"] == "json":
                data = response.json()
                for item in data.get('data', {}).get('items', [])[:5]:
                    all_news.append({"source": source["name"], "title": item.get('title') or item.get('content_text')})
            else:
                # 优先尝试 lxml，失败则使用 html.parser
                try:
                    soup = BeautifulSoup(response.content, 'lxml') # 改为 lxml
                except:
                    soup = BeautifulSoup(response.content, 'html.parser')
                
                for item in soup.find_all('item')[:5]:
                    title = item.find('title').text if item.find('title') else "无标题"
                    all_news.append({"source": source["name"], "title": title})
                    
        except Exception as e:
            print(f"!!! {source['name']} 采集异常: {e}")

    print(f">>> 最终汇总采集到 {len(all_news)} 条新闻")
    return all_news
