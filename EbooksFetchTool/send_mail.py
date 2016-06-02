# -*- coding: utf-8 -*-

import os
import ConfigParser

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr


def _format_addr(s):
	name, addr = parseaddr(s)
	return formataddr((Header(name, 'utf-8').encode(), addr.encode('utf-8') if isinstance(addr, unicode) else addr))

def send_mail(mail_conf, subject='', main_body=''):

	sender = raw_input("From: ")
	sender_psw = raw_input("Password: ")
	receivers = mail_conf.get('mail', 'receivers').split(',')

	sender_name = sender.split('@')[0]
	receivers_name = receivers[0].split('@')[0]

	smtp_server = mail_conf.get('mail', 'smtp_server')

	#
	message = MIMEMultipart()

	# 构建头，这几个东西一定要设正确，否则很容易发不成功
	message['From'] = _format_addr(u'%s<%s>' % (sender_name, sender))
	message['To'] = _format_addr(u'%s<%s>' % (receivers_name, receivers[0]))
	message['Subject'] = Header('', 'utf-8')

	# 构建正文
	message.attach(MIMEText(main_body, 'plain', 'utf-8'))

	# 构建附件
	attach_file_path = mail_conf.get('file', 'path')
	file_type_list = mail_conf.get('file', 'file_type').split(',')

	# 遍历目录下所有mobi文件
	for dirpath, dirnames, filenames in os.walk(attach_file_path):
		for filename in filenames:
			file_surfix = os.path.splitext(filename)[1][1:]
			if file_surfix in file_type_list:
				#print filename, "size:", os.path.getsize(filename)
				attach_file = open(os.path.join(dirpath, filename), 'rb')
				if attach_file:
					attachment = MIMEText(attach_file.read(), 'base64', 'utf-8')
					attachment['Content-Type'] = 'application/octet-stream'
					attachment["Content-Disposition"] = 'attachment; filename="%s"' % filename
					message.attach(attachment)
					attach_file.close()
				else:
					print "Error open file! " + os.path.join(dirpath, filename)

	try:
		smtpObj = smtplib.SMTP()
		smtpObj.connect(smtp_server)
		smtpObj.login(sender, sender_psw)
		smtpObj.sendmail(sender, receivers, message.as_string())
		smtpObj.quit()

		print "OK: send mail succeed!"

	except smtplib.SMTPException:
		print "Error: send mail failed! "



if __name__ == '__main__':

	# 加载配置
	app_config = ConfigParser.ConfigParser()
	app_config.read("app.conf")

	# 发邮件
	send_mail(app_config, u'test', u'thanks')
