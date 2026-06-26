import google.generativeai as genai
import json

def analyze_and_rank(news_list, api_key):
    """使用 Gemini 分析并筛选出最有价值的财经新闻"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 将 news_list 简化为纯文本列表，节省Token
    summary_input = "\n".join([f"[{n['source']}] {n['title']}" for n in news_list[:30]])
    
    prompt = f"""
    你是一名专业财经情报分析师，负责为高管提供决策支持。
    请根据以下新闻标题，筛选出最重要、最具前瞻性且对长三角/浙江地区国资改革、硬科技、生物医药、国际贸易影响最大的前6条。
    请打分（0-10分），并给出简短的专业点评。
    
    输出要求：严格返回 JSON 格式，如下所示：
    [
      {{"title": "新闻标题", "score": 9, "insight": "简洁点评"}},
      ...
    ]
    
    新闻列表：
    {summary_input}
    """
    
    try:
        response = model.generate_content(prompt)
        # 清理响应中的 Markdown 标记
        content = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(content)
    except Exception as e:
        print(f"AI 分析出错: {e}")
        return []
