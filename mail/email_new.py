from daemon_email import Daemon
import sys
import smtplib
from models import Table
import logging
from time import sleep


# initialize db_name "email" and collection "email"
db = Table("email", "email")
#logging.basicConfig(level=logging.DEBUG, filename="test.log", format="%(message)s")


def sendmail(array):
    # function for read data in db and send mail
    # unzip data
    username = 'eastern.server.engine@gmail.com'
    password = '9018540z'
    FROM = username
    TO = [array["to"]]
    SUBJECT = array["subject"]
    # check on correct data in optional
    if type(array["optional"]) == str and array["optional"]:
        TEXT = array["optional"]
    else:
        return "Error: missed argument"
    # make template

    message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        logging.info(server)
        server.ehlo()
        server.starttls()
        # authorizing user, must setup your account
        server.login(username, password)
        server.sendmail(FROM, TO, message)
        server.quit()
        return "Success"
    except:
        return "Error"



class MyDaemon(Daemon):
    def run(self):
        # main program for demonizing
        while True:
            count = db.count()
            #loging.critical(count)
            if count:
                array = db.pop_100el()
                for i in array:
                    sendmail(i)
            else:
                sleep(2)


if __name__ == "__main__":
    # initiation command for work from daemon
    daemon = MyDaemon('/tmp/daem.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
