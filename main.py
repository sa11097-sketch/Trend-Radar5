# coding=utf-8
import os
import sys
import argparse
import yaml
import traceback

# 强制路径：确保能找到 api 文件夹
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.ai_analyzer import analyze_and_rank
from api.email_sender import send_email

# --- 调试导入逻辑 ---
print(">>> DEBUG: 当前目录下的文件列表:")
print(os.listdir('.'))

HAS_ANALYZER = False
try:
    # 这里可能会报错，如果报错，我们会打印出详细信息
    from news_analyzer import NewsAnalyzer, generate_static_api_files
    HAS_ANALYZER = True
    print(">>> DEBUG: 成功导入 NewsAnalyzer")
except Exception as e:
    print("!!! 严重错误：无法导入 NewsAnalyzer")
    traceback.print_exc() # 这会打印详细的报错原因
    HAS_ANALYZER = False

def run_ai_workflow():
    print(">>> 调试：开始 AI 智能分析工作流")
    
    if not HAS_ANALYZER:
        print("!!! 严重错误：由于导入失败，无法获取新闻数据。请检查文件名。")
        return
    
    try:
        analyzer = NewsAnalyzer()
        print(">>> 调试：正在获取新闻数据...")
        raw_data = analyzer.get_all_news()
        print(f">>> 调试：获取到 {len(raw_data)} 条新闻")
        
        if not raw_data:
            print("警告：没有获取到任何新闻数据。")
            return
            
        # 2. AI 分析
        api_key = os.getenv('GEMINI_API_KEY')
        ranked_news = analyze_and_rank(raw_data, api_key)
        
        # 3. 发送邮件
        if ranked_news:
            send_email({}, ranked_news)
        else:
            print("警告：AI 返回为空")
            
    except Exception as e:
        print(f"!!! 流程出错 -> {e}")
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-ai', action='store_true')
    args = parser.parse_args()

    if args.run_ai:
        run_ai_workflow()
    else:
        # 原有逻辑
        if HAS_ANALYZER:
            analyzer = NewsAnalyzer()
            analyzer.run()

if __name__ == "__main__":
    main()
