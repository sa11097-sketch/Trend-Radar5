# coding=utf-8
import os
import sys
import argparse
import yaml

# --- 路径修复代码 (确保能找到 api 文件夹) ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# ----------------------------------------

from api.ai_analyzer import analyze_and_rank
from api.email_sender import send_email

# 尝试导入原项目依赖
try:
    from news_analyzer import NewsAnalyzer, generate_static_api_files
    HAS_ANALYZER = True
except ImportError:
    HAS_ANALYZER = False

def run_ai_workflow():
    """执行 AI 筛选与邮件推送逻辑"""
    print("开始 AI 智能分析工作流...")
    # 1. 实例化原项目分析器以获取数据
    if HAS_ANALYZER:
        analyzer = NewsAnalyzer()
        raw_data = analyzer.get_all_news() # 假设这是获取新闻的方法
    else:
        print("警告: 未找到 NewsAnalyzer，无法获取数据")
        return
    
    # 2. AI 分析
    api_key = os.getenv('GEMINI_API_KEY')
    ranked_news = analyze_and_rank(raw_data, api_key)
    
    # 3. 发送邮件
    if ranked_news:
        send_email({}, ranked_news)
    else:
        print("无高分新闻，未发送邮件")

def main():
    parser = argparse.ArgumentParser(description="TrendRadar: 新闻热点分析工具。")
    parser.add_argument('--serve-api', action='store_true')
    parser.add_argument('--generate-json', action='store_true')
    parser.add_argument('--run-ai', action='store_true', help='执行 AI 分析并发送邮件')
    args = parser.parse_args()

    if args.run_ai:
        run_ai_workflow()
    elif args.serve_api:
        # 尝试导入 Flask 以确保服务器模式可用
        try:
            from flask import Flask
            app = Flask(__name__)
            print("以API服务器模式启动...")
            app.run(host='0.0.0.0', port=5001, debug=False)
        except ImportError:
            print("错误：无法启动API服务器，因为 Flask 模块未安装。")
    elif args.generate_json:
        if HAS_ANALYZER:
            print("仅生成静态API文件...")
            analyzer = NewsAnalyzer()
            generate_static_api_files(analyzer)
            print("文件生成完毕。")
    else:
        # 原有的默认运行逻辑
        if HAS_ANALYZER:
            analyzer = NewsAnalyzer()
            analyzer.run()

if __name__ == "__main__":
    main()
