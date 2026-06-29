# api/crawler_engine.py (均衡采集版)
import requests
from bs4 import BeautifulSoup

def fetch_all_news():
    """多源均衡采集：限制单源条数，并输出详细日志"""
    all_news = []
    
    # 深度伪装 Header
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    # 来源列表
    sources = [
        {"name": "华尔街见闻", "url": "https://api.wallstreetcn.com/v1/livenews?channel=global", "type": "json"},
        {"name": "路透社", "url": "https://www.reuters.com/business/feed", "type": "rss"},
        {"name": "雅虎财经", "url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=yahoofinance&region=US&lang=en-US", "type": "rss"},
        {"name": "CNBC", "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000311", "type": "rss"},
        {"name": "金融时报", "url": "https://www.ft.com/?format=rss", "type": "rss"}
    ]

    print(">>> 开始执行数据采集...")

    for source in sources:
        try:
            print(f"正在抓取 {source['name']} ...")
            response = requests.get(source["url"], headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"  -> {source['name']} 失败 (状态码: {response.status_code})")
                continue

            count = 0
            if source["type"] == "json":
                data = response.json()
                items = data.get('data', {}).get('items', [])
                for item in items[:2]: # 限制单源只取2条
                    all_news.append({"source": source["name"], "title": item.get('title'), "time": "近期"})
                    count += 1
            else:
                soup = BeautifulSoup(response.content, features="xml")
                items = soup.find_all('item')
                for item in items[:2]: # 限制单源只取2条
                    title = item.find('title').text if item.find('title') else "无标题"
                    pub_date = item.find('pubDate').text if item.find('pubDate') else "未知时间"
                    all_news.append({"source": source["name"], "title": title, "time": pub_date})
                    count += 1
            
            print(f"  -> {source['name']} 成功获取 {count} 条")

        except Exception as e:
            print(f"  -> {source['name']} 异常: {e}")

    # 如果抓取总量过少，进行补全
    if len(all_news) < 3:
        print(">>> 采集数量不足，尝试 Google 财经兜底...")
        # ... (此处保持原有兜底逻辑)

    print(f">>> 最终采集汇总: {len(all_news)} 条")
    return all_news
