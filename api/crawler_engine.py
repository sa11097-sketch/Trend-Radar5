# api/crawler_engine.py (网页源抓取进阶版)
import requests
from bs4 import BeautifulSoup

def fetch_all_news():
    """多源混合采集：RSS + 精准网页HTML分析"""
    all_news = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.google.com/"
    }

    # 混合采集配置
    # RSS源：WSJ、FT
    # 网页源：Reuters、Yahoo、CNBC
    sources = [
        {"name": "华尔街见闻", "url": "https://api.wallstreetcn.com/v1/livenews?channel=global", "type": "json"},
        {"name": "金融时报", "url": "https://www.ft.com/?format=rss", "type": "rss"},
        {"name": "路透社", "url": "https://www.reuters.com/business/", "type": "html", "selector": 'a[data-testid="Heading"]'},
        {"name": "雅虎财经", "url": "https://finance.yahoo.com/news/", "type": "html", "selector": 'h3 > a'},
        {"name": "CNBC", "url": "https://www.cnbc.com/finance/", "type": "html", "selector": '.Card-title'}
    ]

    print(">>> 开始执行数据采集（RSS + HTML混合模式）...")

    for source in sources:
        try:
            print(f"正在抓取 {source['name']} ({source['type']})...")
            response = requests.get(source["url"], headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"  -> {source['name']} 失败 (状态码: {response.status_code})")
                continue

            count = 0
            if source["type"] == "json":
                data = response.json()
                for item in data.get('data', {}).get('items', [])[:3]:
                    all_news.append({"source": source["name"], "title": item.get('title'), "time": "近期"})
                    count += 1
            
            elif source["type"] == "rss":
                soup = BeautifulSoup(response.content, features="xml")
                for item in soup.find_all('item')[:3]:
                    title = item.find('title').text if item.find('title') else "无标题"
                    all_news.append({"source": source["name"], "title": title, "time": "RSS"})
                    count += 1
            
            elif source["type"] == "html":
                soup = BeautifulSoup(response.content, 'html.parser')
                elements = soup.select(source["selector"])
                for el in elements[:3]:
                    title = el.text.strip()
                    if len(title) > 5: # 过滤掉无效链接
                        all_news.append({"source": source["name"], "title": title, "time": "网页抓取"})
                        count += 1

            print(f"  -> {source['name']} 成功获取 {count} 条")

        except Exception as e:
            print(f"  -> {source['name']} 异常: {e}")

    return all_news
