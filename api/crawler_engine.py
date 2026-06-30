# api/crawler_engine.py (华尔街见闻替换为 WSJ China 版)
import requests
from bs4 import BeautifulSoup

def fetch_all_news():
    all_news = []
    # 增加更通用的浏览器 Header，避免被识别为简单脚本
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://www.wsj.com/",
    }

    # 配置项：仅修改了第一个源 (华尔街见闻 -> WSJ China)，其他保持原样
    sources = [
        {"name": "华尔街见闻(WSJ)", "url": "https://www.wsj.com/world/china", "type": "html", "selector": 'h3'},
        {"name": "金融时报", "url": "https://www.ft.com/?format=rss", "type": "rss"},
        {"name": "路透社", "url": "https://www.reuters.com/business/", "type": "html", "selector": 'a[data-testid="Heading"]', "time_selector": 'time'},
        {"name": "雅虎财经", "url": "https://finance.yahoo.com/news/", "type": "html", "selector": 'h3 > a', "time_selector": 'time'},
        {"name": "CNBC", "url": "https://www.cnbc.com/latest/", "type": "html", "selector": '.LatestNews-headline', "time_selector": '.LatestNews-timestamp'}
    ]

    for source in sources:
        try:
            response = requests.get(source["url"], headers=headers, timeout=15)
            if response.status_code != 200: continue

            # --- 金融时报 (RSS) ---
            if source["name"] == "金融时报":
                soup = BeautifulSoup(response.content, features="xml")
                for item in soup.find_all('item')[:3]:
                    title = item.find('title').text if item.find('title') else "无标题"
                    all_news.append({"source": source["name"], "title": title, "time": "RSS"})

            # --- CNBC (实时流) ---
            elif source["name"] == "CNBC":
                soup = BeautifulSoup(response.content, 'html.parser')
                items = soup.select('.LatestNews-item')
                for item in items[:3]:
                    title_el = item.select_one('.LatestNews-headline')
                    time_el = item.select_one('.LatestNews-timestamp')
                    title = title_el.text.strip() if title_el else "无标题"
                    pub_time = time_el.text.strip() if time_el else "最新"
                    all_news.append({"source": source["name"], "title": title, "time": pub_time})

            # --- WSJ China (新目标) ---
            elif source["name"] == "华尔街见闻(WSJ)":
                soup = BeautifulSoup(response.content, 'html.parser')
                # 抓取 h3 标题，过滤掉过短的无意义文本
                for el in soup.select(source["selector"])[:5]:
                    title = el.text.strip()
                    if len(title) > 10:
                        all_news.append({"source": source["name"], "title": title, "time": "网页抓取"})

            # --- 其他通用 HTML 源 (路透、雅虎) ---
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