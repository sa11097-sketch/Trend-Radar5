# api/crawler_engine.py (增强版)
import requests
from bs4 import BeautifulSoup
import json

def fetch_all_news():
    """从多个渠道获取财经新闻，返回列表"""
    all_news = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    # 1. 抓取华尔街见闻 (API接口)
    try:
        url = "https://api.wallstreetcn.com/v1/livenews?channel=global"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for item in data.get('data', {}).get('items', [])[:10]:
                all_news.append({
                    "source": "华尔街见闻",
                    "title": item.get('title') or item.get('content_text')
                })
    except Exception as e:
        print(f"华尔街见闻抓取失败: {e}")

    # 2. 抓取其他网站 (以 RSS 为例，这是最稳妥的)
    # 如果你还需要添加更多网站，可以在这里继续添加
    # 示例：路透社 RSS
    try:
        reuters_url = "https://www.reutersagency.com/feed/?post_type=best"
        resp = requests.get(reuters_url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.content, 'xml') # 使用 xml 解析器
        for item in soup.find_all('item')[:5]:
            all_news.append({
                "source": "路透社",
                "title": item.title.text
            })
    except Exception as e:
        print(f"路透社抓取失败: {e}")

    # 去重
    unique_news = {n['title']: n for n in all_news}.values()
    return list(unique_news)
