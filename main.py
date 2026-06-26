# coding=utf-8
import os
import sys
import argparse

# 强制将当前目录加入路径，确保能找到 api 文件夹
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.ai_analyzer import analyze_and_rank
from api.email_sender import send_email

def get_news_data():
    """
    这里是你获取新闻数据的地方。
    目前我放了一个测试数据，保证程序能跑通。
    后续你可以把你真正的爬虫代码逻辑写在这里。
    """
    # 示例数据
    return [
        {"source": "测试源", "title": "这是一个测试新闻，请在此处替换为你的真实数据获取逻辑"}
    ]

def run_ai_workflow():
    print(">>> 调试：开始纯净版 AI 工作流")
    
    # 1. 获取数据
    raw_data = get_news_data()
    print(f">>> 调试：获取到 {len(raw_data)} 条新闻")
    
    # 2. AI 分析
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("!!! 错误：未配置 GEMINI_API_KEY")
        return
        
    print(">>> 调试：正在调用 AI 进行分析...")
    ranked_news = analyze_and_rank(raw_data, api_key)
    print(f">>> 调试：AI 分析完成，返回 {len(ranked_news)} 条精选新闻")
    
    # 3. 发送邮件
    if ranked_news:
        print(">>> 调试：正在发送邮件...")
        try:
            send_email({}, ranked_news)
            print(">>> 调试：邮件发送成功！")
        except Exception as e:
            print(f"!!! 邮件发送失败: {e}")
    else:
        print("警告：AI 返回为空，没有精选新闻。")

def main():
    # 只要运行 python main.py --run-ai，就会执行上面的工作流
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-ai', action='store_true')
    args = parser.parse_args()

    if args.run_ai:
        run_ai_workflow()
    else:
        print("请使用 python main.py --run-ai 来启动工作流")

if __name__ == "__main__":
    main()
