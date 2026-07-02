# api/crawler_engine.py (全源均衡版)
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

def fetch_all_news():
    all_news = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    # 保持原有配置框架不动
    sources = [
        {"name": "华尔街日报", "url": "https://news.google.com/rss/search?q=site:wsj.com+china&hl=zh-CN&gl=CN&ceid=CN:zh-Hans", "type": "rss"},
        {"name": "路透社", "url": "https://news.google.com/rss/search?q=site:reuters.com+business&hl=zh-CN&gl=CN&ceid=CN:zh-Hans", "type": "rss"},
        {"name": "雅虎财经", "url": "https://news.google.com/rss/search?q=site:finance.yahoo.com&hl=zh-CN&gl=CN&ceid=CN:zh-Hans", "type": "rss"},
        {"name": "金融时报", "url": "https://www.ft.com/?format=rss", "type": "rss"},
        {"name": "CNBC", "url": "https://www.cnbc.com/latest/", "type": "html", "selector": '.LatestNews-headline', "time_selector": '.LatestNews-timestamp'}
    ]

    time_threshold = datetime.now(timezone.utc) - timedelta(hours=48)

    for source in sources:
        try:
            response = requests.get(source["url"], headers=headers, timeout=15)
            if response.status_code != 200: continue

            # 1. 统一 RSS 处理逻辑 (华尔街日报、路透社、雅虎财经、金融时报)
            if source["type"] == "rss":
                soup = BeautifulSoup(response.content, features="xml")
                items = soup.find_all('item')
                filtered_items = []
                for item in items:
                    title = item.find('title').text if item.find('title') else "无标题"
                    pub_date_str = item.find('pubDate').text if item.find('pubDate') else None
                    if pub_date_str:
                        pub_date = parsedate_to_datetime(pub_date_str)
                        if pub_date > time_threshold:
                            filtered_items.append({"title": title, "pub_date": pub_date})
                
                filtered_items.sort(key=lambda x: x['pub_date'], reverse=True)
                
                # 【修改点】：将 [:3] 修改为 [:2]，确保每家媒体最多贡献 2 条
                for item in filtered_items[:2]:
                    all_news.append({"source": source["name"], "title": item['title'], "time": item['pub_date'].strftime('%m-%d %H:%M')})

            # 2. CNBC 原生逻辑 (严格保持不动)
            elif source["name"] == "CNBC":
                soup = BeautifulSoup(response.content, 'html.parser')
                items = soup.select('.LatestNews-item')
                
                # 【修改点】：同样将 [:3] 修改为 [:2]
                for item in items[:2]:
                    title_el = item.select_one('.LatestNews-headline')
                    time_el = item.select_one('.LatestNews-timestamp')
                    title = title_el.text.strip() if title_el else "无标题"
                    pub_time = time_el.text.strip() if time_el else "最新"
                    all_news.append({"source": source["name"], "title": title, "time": pub_time})

        except Exception as e:
            print(f"采集异常 ({source['name']}): {e}")
            
    return all_news