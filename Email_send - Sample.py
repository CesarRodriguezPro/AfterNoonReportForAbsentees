import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime


############################ Settings ##############################
user_name = 'username'
user_password = 'userPassword'
today = datetime.datetime.today().strftime('%m/%d/%Y')
emailUser = "EmailUser"

to = 'test@test.com'
cc = 'test@test.com'
####################################################################


def email_send():

    print('Start process')
    with open('message.txt', "r") as m:
        message = m.read()

        msg = MIMEMultipart()
        msg['From'] = emailUser
        msg['To'] = to
        msg['Cc'] = cc
        msg['Subject'] = "subject for Email"

        body = message
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.ibkconstructiongroup.com')
        server.starttls()
        server.login(user_name, password=user_password)
        text = msg.as_string()
        server.sendmail(emailUser,to.split()+cc.split(), text)
        server.quit()
        print('message was send')


if __name__ == '__main__':

    print('This is only to be used from the EmployeesMissing.py')
    input('')