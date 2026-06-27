# api/crawler_engine.py
import requests
from bs4 import BeautifulSoup
import time

SOURCES = [
    {"id": "wallstreetcn-hot", "name": "华尔街见闻", "url": "https://api.wallstreetcn.com/v1/livenews?channel=global"}, # 建议使用API接口
    # 注意：大型网站建议优先使用其 RSS 或 API 接口，直接爬网页容易触发风控
]

def fetch_all_news():
    """获取所有新闻来源，汇总并去重"""
    all_news = []
    
    # 模拟浏览器头部，防止直接被阻断
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    # 这里以华尔街见闻的API为例（实际操作中建议配置各站点的获取逻辑）
    try:
        # 示例：抓取逻辑，后续可扩充其他网站
        response = requests.get(SOURCES[0]["url"], headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # 解析华尔街见闻的直播流格式
            for item in data.get('data', {}).get('items', [])[:15]:
                all_news.append({
                    "source": "华尔街见闻",
                    "title": item.get('title') or item.get('content_text'),
                    "timestamp": item.get('display_time')
                })
    except Exception as e:
        print(f"!!! 爬取华尔街见闻失败: {e}")

    # TODO: 可以在这里继续添加其他网站的爬取逻辑
    # 建议策略：对 Reuters, FT, CNBC 等，优先寻找其官方 RSS 链接进行解析，最稳定
    
    return all_news
