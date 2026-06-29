# api/email_sender.py (7分过滤版)
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(config, ranked_news):
    sender = os.getenv('GMAIL_USER')
    password = os.getenv('GMAIL_APP_PASSWORD')
    receiver = os.getenv('RECEIVER_EMAIL')
    
    if not all([sender, password, receiver]):
        return

    msg = MIMEMultipart()
    msg['Subject'] = '【今日财经情报简报】高管精选'
    msg['From'] = sender
    msg['To'] = receiver
    
    body = "今日精选财经情报（AI 辅助筛选，仅显示 7 分及以上）：\n\n"
    
    # 核心过滤逻辑：score >= 7
    filtered_news = [item for item in ranked_news if int(item.get('score', 0)) >= 7]
    
    if not filtered_news:
        body += "今日无高分情报 (7分以上) 更新。"
    else:
        for item in filtered_news:
            score = item.get('score', 0)
            title = item.get('title', '无标题')
            source = item.get('source', '未知')
            time_val = item.get('time', '未知')
            insight = item.get('insight', '暂无点评')
            
            body += f"【{score}分】{title} (来源: {source} | 时间: {time_val})\n"
            body += f"点评：{insight}\n\n"
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print("邮件推送成功")
    except Exception as e:
        print(f"邮件发送失败: {e}")
