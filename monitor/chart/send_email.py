# from flask.ext.mail import Message,Attachment
# from config import ADMINS
# from monitor import app,mail
# from flask import render_template

# # def send_msg(subject, sender, recipients,text_body, html_body):
# def send_msg(subject, sender, recipients,attachments, text_body, html_body):
	
# 	# msg = Message(subject,sender=sender,recipients=recipients)
# 	msg = Message(subject,sender=sender,recipients=recipients,attachments=attachments)
# 	msg.body = text_body
# 	msg.html = html_body
# 	res = mail.send(msg)
# 	# print "--------------------send res---------------------", res

# def monitor_status_notification(img_info,rvaddress,subject):
# 	attachments = []
# 	index = 0
# 	attach_info = []
# 	for ii in img_info:
# 		path = 'static/report/' + ii['name']
# 		tmp = {}
# 		with app.open_resource(path) as fp:
# 			c_id = 'monitorreport' + str(index) + ''
# 			# Content_IDs.append(c_id)
# 			tmp['cid'] = c_id
# 			header = [('Content-ID','<' + c_id + '>')]
# 	 		attach1 = Attachment(filename= ii['name'],content_type='image/png',data=fp.read(),disposition='attachment',headers=header)
# 	 		attachments.append(attach1)
	 		
# 	 	tmp['title'] = ii['title']
# 	 	tmp['discription'] = ii['discription']
# 	 	attach_info.append(tmp)
# 	 	index += 1


	
# 	subject = subject
# 	sender = ADMINS[0]
# 	recipients = rvaddress
	
# 	text_body = render_template("chart/information.txt",server_name = 'Control',server_address = 'sg.control.tplinkcloud.com',running_status='Regular')
# 	html_body = render_template("chart/information.html",server_name = 'Control',attach_info=attach_info)

# 	# send_msg(subject,sender,recipients,text_body,html_body)
# 	send_msg(subject,sender,recipients,attachments,text_body,html_body)