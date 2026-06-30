# api/crawler_engine.py (华尔街日报 深度伪装版)
import requests
from bs4 import BeautifulSoup
import time

def fetch_all_news():
    all_news = []
    # 模拟真实浏览器的完整请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.wsj.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    sources = [
        {"name": "华尔街日报", "url": "https://www.wsj.com/world/china", "type": "html", "selector": 'h3'},
        {"name": "金融时报", "url": "https://www.ft.com/?format=rss", "type": "rss"},
        {"name": "路透社", "url": "https://www.reuters.com/business/", "type": "html", "selector": 'a[data-testid="Heading"]', "time_selector": 'time'},
        {"name": "雅虎财经", "url": "https://finance.yahoo.com/news/", "type": "html", "selector": 'h3 > a', "time_selector": 'time'},
        {"name": "CNBC", "url": "https://www.cnbc.com/latest/", "type": "html", "selector": '.LatestNews-headline', "time_selector": '.LatestNews-timestamp'}
    ]

    for source in sources:
        try:
            # 增加一个延时，避免被服务器瞬时拦截
            time.sleep(1) 
            response = requests.get(source["url"], headers=headers, timeout=20)
            
            if response.status_code != 200:
                print(f"[{source['name']}] 状态码异常: {response.status_code}")
                continue

            if source["name"] == "金融时报":
                soup = BeautifulSoup(response.content, features="xml")
                for item in soup.find_all('item')[:3]:
                    title = item.find('title').text if item.find('title') else "无标题"
                    all_news.append({"source": source["name"], "title": title, "time": "RSS"})

            elif source["name"] == "CNBC":
                soup = BeautifulSoup(response.content, 'html.parser')
                items = soup.select('.LatestNews-item')
                for item in items[:3]:
                    title_el = item.select_one('.LatestNews-headline')
                    time_el = item.select_one('.LatestNews-timestamp')
                    title = title_el.text.strip() if title_el else "无标题"
                    pub_time = time_el.text.strip() if time_el else "最新"
                    all_news.append({"source": source["name"], "title": title, "time": pub_time})

            elif source["name"] == "华尔街日报":
                soup = BeautifulSoup(response.content, 'html.parser')
                # 华尔街日报的标题通常在 h3 标签下
                found = False
                for el in soup.select(source["selector"]):
                    title = el.text.strip()
                    # 过滤掉非新闻的短链接文本
                    if len(title) > 15:
                        all_news.append({"source": source["name"], "title": title, "time": "网页抓取"})
                        found = True
                    if len(all_news) >= 3 and found: break # 抓够3条即可
                if not found: print(f"[{source['name']}] 未抓取到内容，可能是反爬拦截。")

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