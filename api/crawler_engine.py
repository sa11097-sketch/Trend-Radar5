# api/crawler_engine.py (CNBC 实时流优化版)
import requests
from bs4 import BeautifulSoup

def fetch_all_news():
    all_news = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    sources = [
        # 其他源保持原样
        {"name": "华尔街见闻", "url": "https://api.wallstreetcn.com/v1/livenews?channel=global", "type": "json"},
        {"name": "金融时报", "url": "https://www.ft.com/?format=rss", "type": "rss"},
        {"name": "路透社", "url": "https://www.reuters.com/business/", "type": "html", "selector": 'a[data-testid="Heading"]', "time_selector": 'time'},
        {"name": "雅虎财经", "url": "https://finance.yahoo.com/news/", "type": "html", "selector": 'h3 > a', "time_selector": 'time'},
        # CNBC 针对性更新：锁定最新流，使用更精准的选择器
        {"name": "CNBC", "url": "https://www.cnbc.com/latest/", "type": "html", "selector": '.LatestNews-headline', "time_selector": '.LatestNews-timestamp'}
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
                    pub_date = pub_date.split(', ')[-1].replace(' GMT', '') if ',' in pub_date else pub_date
                    all_news.append({"source": source["name"], "title": title, "time": pub_date})
            
            elif source["type"] == "html":
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 如果是 CNBC 的新布局，使用更精准的抓取方式
                if source["name"] == "CNBC":
                    items = soup.select('.LatestNews-item')
                    for item in items[:3]:
                        title_el = item.select_one('.LatestNews-headline')
                        time_el = item.select_one('.LatestNews-timestamp')
                        if title_el:
                            title = title_el.text.strip()
                            pub_time = time_el.text.strip() if time_el else "最新"
                            all_news.append({"source": source["name"], "title": title, "time": pub_time})
                else:
                    # 原有其他网站的逻辑保持不变
                    elements = soup.select(source["selector"])
                    for el in elements[:3]:
                        title = el.text.strip()
                        time_tag = el.find_next('time') or el.find_parent().find('time')
                        pub_time = time_tag.get('datetime') if time_tag and time_tag.has_attr('datetime') else "网页抓取"
                        all_news.append({"source": source["name"], "title": title, "time": pub_time[:16].replace('T', ' ')})
        except Exception as e:
            print(f"采集异常: {e}")
    return all_news
