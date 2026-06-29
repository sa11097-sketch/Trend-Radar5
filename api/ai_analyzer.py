# api/ai_analyzer.py (强制中文与元数据版)
import google.generativeai as genai
import json

def analyze_and_rank(news_list, api_key):
    if not api_key:
        return []
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 包含时间信息
    summary_input = "\n".join([f"[{n.get('source', '未知')}] [{n.get('time', '未知时间')}] {n.get('title', '')}" for n in news_list])
    
    prompt = f"""
    你是一名专业财经情报分析师。请阅读以下新闻列表，挑选最有价值的6条。
    
    【核心要求】：
    1. 必须将所有内容翻译为中文，点评也必须使用中文。
    2. 输出的 JSON 格式必须包含：source（来源）、time（时间）、title（中文标题）、score（0-10）、insight（精华点评，70汉字以内，对国内宏观面影响）。
    3. 输出要求：严格返回 JSON 数组，不包含任何 Markdown 标记。
    
    新闻列表：
    {summary_input}
    """
    
    try:
        response = model.generate_content(prompt)
        content = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(content)
    except Exception as e:
        print(f"AI 分析出错: {e}")
        return []
