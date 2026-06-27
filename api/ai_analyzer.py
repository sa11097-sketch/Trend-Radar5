import google.generativeai as genai
import json
import os

def analyze_and_rank(news_list, api_key):
    """使用 Gemini 分析并筛选出最有价值的财经新闻"""
    if not api_key:
        print("API Key 未配置，跳过 AI 分析")
        return []
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash') # 建议使用最新版本模型

    # 简化新闻列表，仅取标题和来源
    summary_input = "\n".join([f"[{i}] [{n.get('source', '未知')}] {n.get('title', '')}" for i, n in enumerate(news_list[:30])])
    
    # 使用 .format() 填充变量，而不是直接使用 f-string，可以避免 {} 冲突
    template = """
    你是一名专业财经情报分析师，负责为高管提供决策支持。
    关注核心领域：国资动态、国企改革、汇率、大宗商品、半导体、AI、生物医药、跨境贸易、国际宏观。
    
    请从以下新闻列表中，挑选出最具价值、前瞻性且对上述领域影响最大的前6条。
    请按重要性打分(0-10分)，并给出简短的专业点评。
    
    输出要求：严格返回 JSON 数组格式，不要 Markdown，不要解释。
    格式如下：
    [
      {"title": "新闻标题", "score": 9, "insight": "简洁点评"}
    ]
    
    新闻列表：
    {news_content}
    """
    
    prompt = template.format(news_content=summary_input)
    
    try:
        response = model.generate_content(prompt)
        content = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(content)
    except Exception as e:
        print(f"AI 分析出错: {e}")
        return []
