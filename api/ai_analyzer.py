# api/ai_analyzer.py (覆盖版)
import google.generativeai as genai
import json

def analyze_and_rank(news_list, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 将数据打包，并要求 AI 进行筛选
    summary_input = "\n".join([f"[{n.get('source')}] {n.get('title')}" for n in news_list])
    
    prompt = f"""
    你是高管情报助手。
    任务：从以下新闻中筛选最有价值的前6条。
    过滤原则：
    1. 必须是12小时内的重要动态。
    2. 关注领域：国资/国企改革/宏观政策/大宗商品/AI/生物医药。
    3. 严格按重要性(0-10分)排序，仅返回得分最高的前6条。
    
    输出要求：严格的 JSON 数组，格式为 [{"title": "...", "score": 9, "insight": "..."}]。不要Markdown标记。
    
    新闻：
    {summary_input}
    """
    
    response = model.generate_content(prompt)
    try:
        # 强制处理可能的 Markdown 包裹
        content = response.text.replace('```json', '').replace('```', '')
        return json.loads(content)
    except:
        return []
