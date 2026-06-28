# api/crawler_engine.py (终极整合版)
import requests
from bs4 import BeautifulSoup

def fetch_all_news():
    """全量财经媒体采集：含深度伪装与防御性容错解析"""
    all_news = []
    
    # 深度伪装 Header
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/"
    }

    # 完整来源列表
    sources = [
        {"name": "华尔街见闻", "url": "https://api.wallstreetcn.com/v1/livenews?channel=global", "type": "json"},
        {"name": "路透社", "url": "https://www.reuters.com/arc/outboundfeeds/rss/?outputType=xml", "type": "rss"},
        {"name": "雅虎财经", "url": "https://finance.yahoo.com/rss/headline", "type": "rss"},
        {"name": "CNBC", "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000311", "type": "rss"},
        {"name": "金融时报", "url": "https://www.ft.com/?format=rss", "type": "rss"}
    ]

    for source in sources:
        try:
            response = requests.get(source["url"], headers=headers, timeout=12)
            if response.status_code != 200:
                print(f"!!! {source['name']} 响应错误: {response.status_code}")
                continue

            if source["type"] == "json":
                data = response.json()
                for item in data.get('data', {}).get('items', [])[:5]:
                    all_news.append({"source": source["name"], "title": item.get('title') or item.get('content_text')})
            else:
                # 【核心防御逻辑】：优先 XML，失败自动回退 html.parser
                try:
                    soup = BeautifulSoup(response.content, features="xml")
                    # 检查是否成功解析（如果没找到 item，可能是解析错误）
                    if not soup.find_all('item'):
                        raise Exception("XML解析未发现item")
                except:
                    soup = BeautifulSoup(response.content, features="html.parser")
                
                for item in soup.find_all('item')[:5]:
                    title = item.find('title').text if item.find('title') else "无标题"
                    all_news.append({"source": source["name"], "title": title})
                    
        except Exception as e:
            print(f"!!! {source['name']} 采集异常: {e}")

    # 兜底机制：Google 财经数据
    if len(all_news) < 3:
        print(">>> 采集数量不足，启动 Google 财经数据补充...")
        try:
            resp = requests.get("https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=zh-CN", headers=headers, timeout=10)
            soup = BeautifulSoup(resp.content, features="xml")
            for item in soup.find_all('item')[:5]:
                all_news.append({"source": "Google财经", "title": item.find('title').text})
        except:
            pass

    print(f">>> 最终汇总采集到 {len(all_news)} 条新闻")
    return all_news
