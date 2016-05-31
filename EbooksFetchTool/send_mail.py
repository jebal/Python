# -*- coding: utf-8 -*-

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr


def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr.encode('utf-8') if isinstance(addr, unicode) else addr))


def send_mail():

        sender = 'jebal@126.com'
        receivers = ['529074441@qq.com']

        message = MIMEMultipart()
        
        message['From'] = _format_addr(u'jebal<%s>' % sender)
        message['To'] = _format_addr(u'kindle<%s>' % receivers[0])
        message['Subject'] = Header('', 'utf-8')

        # 构建正文
        message.attach(MIMEText('Thanks', 'plain', 'utf-8'))
        
        # 构建附件
        attach_file = open('G:\\code\\python\\EbooksFetchTool\\fetch_ebooks.py', 'rb')
        attachment = MIMEText(attach_file.read(), 'base64', 'utf-8')
        attachment['Content-Type'] = 'application/octet-stream'
        attachment["Content-Disposition"] = 'attachment; filename="fetch_ebooks.py"'
        message.attach(attachment)
       
        try:                
                smtpObj = smtplib.SMTP()        
                smtpObj.connect('smtp.126.com')
                smtpObj.login(sender, 'jebal*_*100912')                
                smtpObj.sendmail(sender, receivers, message.as_string())
                smtpObj.quit()
                attach_file.close()
                
                print "邮件发送成功"
        except smtplib.SMTPException:
                print "Error: send mail failed! "        

if __name__ == '__main__':

        '''
        sender = 'jebal@126.com'
        receivers = ['529074441@qq.com']
        message = MIMEText('Python 邮件发送测试...', 'plain', 'utf-8')
        message['From'] = Header("菜鸟教程", 'utf-8')
        message['To'] = Header("测试", 'utf-8')
        message['Subject'] = Header('python smtp 邮件测试', 'utf-8')

        try:
                smtpObj = smtplib.SMTP()
                smtpObj.set_debuglevel(1)
                smtpObj.connect('smtp.126.com') 
                smtpObj.login(sender, u'jebal*_*100912')
                smtpObj.sendmail(sender, receivers, message.as_string())
                print "邮件发送成功"
        except smtplib.SMTPException:
                print "Error: send mail failed! "
        '''
        send_mail()
