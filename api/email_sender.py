import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(config, ranked_news):
    """发送邮件推送"""
    sender = config['sender_email']
    password = config['password']
    receiver = config['receiver_email']
    
    msg = MIMEMultipart()
    msg['Subject'] = '【今日财经情报简报】高管精选'
    msg['From'] = sender
    msg['To'] = receiver
    
    # 构建邮件正文
    body = "今日精选财经情报（AI 辅助筛选）：\n\n"
    for item in ranked_news:
        body += f"【{item['score']}分】{item['title']}\n点评：{item['insight']}\n\n"
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print("邮件推送成功")
    except Exception as e:
        print(f"邮件发送失败: {e}")
