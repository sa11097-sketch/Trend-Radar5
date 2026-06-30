# api/crawler_engine.py (WSJ 绕过拦截版)
import requests
from bs4 import BeautifulSoup

def fetch_all_news():
    all_news = []
    # 模拟真实浏览器的请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    # 将 WSJ 目标地址切换为 Google News 聚合搜索，这能完美规避 401 拦截
    sources = [
        {"name": "华尔街日报", "url": "https://news.google.com/rss/search?q=site:wsj.com+china&hl=zh-CN&gl=CN&ceid=CN:zh-Hans", "type": "rss"},
        {"name": "金融时报", "url": "https://www.ft.com/?format=rss", "type": "rss"},
        {"name": "路透社", "url": "https://www.reuters.com/business/", "type": "html", "selector": 'a[data-testid="Heading"]', "time_selector": 'time'},
        {"name": "雅虎财经", "url": "https://finance.yahoo.com/news/", "type": "html", "selector": 'h3 > a', "time_selector": 'time'},
        {"name": "CNBC", "url": "https://www.cnbc.com/latest/", "type": "html", "selector": '.LatestNews-headline', "time_selector": '.LatestNews-timestamp'}
    ]

    for source in sources:
        try:
            response = requests.get(source["url"], headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"[{source['name']}] 状态码异常: {response.status_code}")
                continue

            if source["type"] == "rss":
                soup = BeautifulSoup(response.content, features="xml")
                items = soup.find_all('item')
                # 华尔街日报通过 Google News 抓取，直接提取标题和发布时间
                if source["name"] == "华尔街日报":
                    for item in items[:3]:
                        title = item.find('title').text if item.find('title') else "无标题"
                        pub_date = item.find('pubDate').text if item.find('pubDate') else "未知"
                        all_news.append({"source": source["name"], "title": title, "time": pub_date[:22]})
                # 金融时报保持原有 RSS 逻辑
                else:
                    for item in items[:3]:
                        title = item.find('title').text if item.find('title') else "无标题"
                        all_news.append({"source": source["name"], "title": title, "time": "RSS"})

            elif source["type"] == "html":
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # CNBC 实时流保持不动
                if source["name"] == "CNBC":
                    items = soup.select('.LatestNews-item')
                    for item in items[:3]:
                        title_el = item.select_one('.LatestNews-headline')
                        time_el = item.select_one('.LatestNews-timestamp')
                        title = title_el.text.strip() if title_el else "无标题"
                        pub_time = time_el.text.strip() if time_el else "最新"
                        all_news.append({"source": source["name"], "title": title, "time": pub_time})
                
                # 路透社、雅虎财经保持不动
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