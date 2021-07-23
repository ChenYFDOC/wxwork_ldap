import smtplib
from email.mime.text import MIMEText
from email.header import Header
from config import settings
from utils.log import logger


class Sender():
    def __init__(self):
        self.sender = settings['email_sender']

    def send(self, text, to):
        message = MIMEText(text, 'plain', 'utf-8')
        message['Subject'] = Header('您的通用账号', 'utf-8')
        message['From'] = Header(self.sender, 'utf-8')  # 发送者
        message['To'] = Header(to, 'utf-8')  # 接收者
        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(settings['email_host'], 25)
            smtpObj.login(settings['email_user'], settings['email_password'])
            smtpObj.sendmail(settings['email_sender'], to, message.as_string())
            smtpObj.quit()
        except smtplib.SMTPException:
            logger.error(to + '发送邮件失败')
