# api/crawler_engine.py (WSJ 强过滤版)
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

def fetch_all_news():
    all_news = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    sources = [
        {"name": "华尔街日报", "url": "https://news.google.com/rss/search?q=site:wsj.com+china&hl=zh-CN&gl=CN&ceid=CN:zh-Hans", "type": "rss"},
        {"name": "金融时报", "url": "https://www.ft.com/?format=rss", "type": "rss"},
        {"name": "路透社", "url": "https://www.reuters.com/business/", "type": "html", "selector": 'a[data-testid="Heading"]', "time_selector": 'time'},
        {"name": "雅虎财经", "url": "https://finance.yahoo.com/news/", "type": "html", "selector": 'h3 > a', "time_selector": 'time'},
        {"name": "CNBC", "url": "https://www.cnbc.com/latest/", "type": "html", "selector": '.LatestNews-headline', "time_selector": '.LatestNews-timestamp'}
    ]

    # 定义最近 48 小时阈值
    time_threshold = datetime.now(timezone.utc) - timedelta(hours=48)

    for source in sources:
        try:
            response = requests.get(source["url"], headers=headers, timeout=15)
            if response.status_code != 200: continue

            # --- RSS 处理逻辑 (包括华尔街日报) ---
            if source["type"] == "rss":
                soup = BeautifulSoup(response.content, features="xml")
                items = soup.find_all('item')
                
                # 创建一个临时列表来过滤和排序
                filtered_items = []
                for item in items:
                    title = item.find('title').text if item.find('title') else "无标题"
                    pub_date_str = item.find('pubDate').text if item.find('pubDate') else None
                    
                    if pub_date_str:
                        pub_date = parsedate_to_datetime(pub_date_str)
                        # 只保留最近 48 小时内的
                        if pub_date > time_threshold:
                            filtered_items.append({"title": title, "pub_date": pub_date})
                
                # 按时间从新到旧排序
                filtered_items.sort(key=lambda x: x['pub_date'], reverse=True)
                
                # 取最新的前 3 条
                for item in filtered_items[:3]:
                    all_news.append({"source": source["name"], "title": item['title'], "time": item['pub_date'].strftime('%m-%d %H:%M')})

            # --- CNBC 实时流 (完全保持原样) ---
            elif source["name"] == "CNBC":
                soup = BeautifulSoup(response.content, 'html.parser')
                items = soup.select('.LatestNews-item')
                for item in items[:3]:
                    title_el = item.select_one('.LatestNews-headline')
                    time_el = item.select_one('.LatestNews-timestamp')
                    title = title_el.text.strip() if title_el else "无标题"
                    pub_time = time_el.text.strip() if time_el else "最新"
                    all_news.append({"source": source["name"], "title": title, "time": pub_time})

            # --- 其他网页源 ---
            else:
                soup = BeautifulSoup(response.content, 'html.parser')
                elements = soup.select(source["selector"])
                for el in elements[:3]:
                    title = el.text.strip()
                    time_tag = el.find_next('time') or el.find_parent().find('time')
                    pub_time = time_tag.get('datetime') if time_tag and time_tag.has_attr('datetime') else "网页抓取"
                    all_news.append({"source": source["name"], "title": title, "time": pub_time[:16].replace('T', ' ')})

        except Exception as e:
            print(f"采集异常 ({source['name']}): {e}")
            
    return all_news