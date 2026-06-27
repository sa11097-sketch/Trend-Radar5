# main.py (覆盖版)
import os
import sys
import argparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.ai_analyzer import analyze_and_rank
from api.email_sender import send_email
from api.crawler_engine import fetch_all_news  # 导入爬虫引擎

def get_news_data():
    """通过引擎获取新闻"""
    print(">>> 正在启动数据采集引擎...")
    news_data = fetch_all_news()
    print(f">>> 成功采集到 {len(news_data)} 条新闻")
    return news_data

def run_ai_workflow():
    raw_data = get_news_data()
    api_key = os.getenv('GEMINI_API_KEY')
    
    # 核心：分析并筛选
    ranked_news = analyze_and_rank(raw_data, api_key)
    
    if ranked_news:
        send_email({}, ranked_news)
    else:
        print("无高分新闻或分析失败")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-ai', action='store_true')
    args = parser.parse_args()
    if args.run_ai: run_ai_workflow()
