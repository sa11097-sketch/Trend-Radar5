# api/crawler_engine.py (华尔街见闻 攻克版)
import requests
from bs4 import BeautifulSoup

def fetch_all_news():
    all_news = []
    
    # 全局通用的浏览器 User-Agent
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    # 华尔街见闻 专用 Headers，必须带 Referer
    wscn_headers = headers.copy()
    wscn_headers["Referer"] = "https://wallstreetcn.com/"
    wscn_headers["Origin"] = "https://wallstreetcn.com/"

    sources = [
        {"name": "华尔街见闻", "url": "https://api.wallstreetcn.com/v1/livenews?channel=global", "type": "json", "headers": wscn_headers},
        {"name": "金融时报", "url": "https://www.ft.com/?format=rss", "type": "rss"},
        {"name": "路透社", "url": "https://www.reuters.com/business/", "type": "html", "selector": 'a[data-testid="Heading"]', "time_selector": 'time'},
        {"name": "雅虎财经", "url": "https://finance.yahoo.com/news/", "type": "html", "selector": 'h3 > a', "time_selector": 'time'},
        {"name": "CNBC", "url": "https://www.cnbc.com/latest/", "type": "html", "selector": '.LatestNews-headline', "time_selector": '.LatestNews-timestamp'}
    ]

    for source in sources:
        try:
            # 优先使用源特定的 headers，没有则使用通用 headers
            use_headers = source.get("headers", headers)
            response = requests.get(source["url"], headers=use_headers, timeout=15)
            
            if response.status_code != 200: 
                print(f"  -> {source['name']} 失败 (状态码: {response.status_code})")
                continue

            if source["type"] == "json":
                data = response.json()
                # 兼容性处理：尝试获取 data.items，如果没有则尝试 data.data.items
                items = data.get('data', {}).get('items', [])
                if not items: items = data.get('items', [])
                
                for item in items[:3]:
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
                # 针对 CNBC 和其他源的特殊处理保持逻辑一致
                if source["name"] == "CNBC":
                    items = soup.select('.LatestNews-item')
                    for item in items[:3]:
                        title_el = item.select_one('.LatestNews-headline')
                        time_el = item.select_one('.LatestNews-timestamp')
                        if title_el:
                            all_news.append({"source": source["name"], "title": title_el.text.strip(), "time": time_el.text.strip() if time_el else "最新"})
                else:
                    elements = soup.select(source["selector"])
                    for el in elements[:3]:
                        title = el.text.strip()
                        time_tag = el.find_next('time') or el.find_parent().find('time')
                        pub_time = time_tag.get('datetime') if time_tag and time_tag.has_attr('datetime') else "网页抓取"
                        all_news.append({"source": source["name"], "title": title, "time": pub_time[:16].replace('T', ' ')})
        except Exception as e:
            print(f"采集异常 ({source['name']}): {e}")
            
    return all_news
