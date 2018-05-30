import sys
import smtplib
import logging
from time import sleep
from daemon_email import Daemon
from models import Table


# initialize db_name "email" and collection "email"
db = Table("email", "email")


logging.basicConfig(level=logging.DEBUG, filename="test.log", format="%(message)s")


def sendmail(array):
    """function for read data in db and send mail
    """
    username = 'example@gmail.com'
    password = 'pass'
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
        # send mail
        server.sendmail(FROM, TO, message)
        server.quit()
        return "Success"
    except:
        return "Error"


class MyDaemon(Daemon):
    def run(self):
        # main program for demonizing
        while True:
            # get count new email
            count = db.count()
            # if count != 0
            if count:
                # get 100 last email
                array = db.pop_100el()
                for i in array:
                    request = sendmail(i)
                    logging.info(request)
            else:
                sleep(2)


if __name__ == "__main__":
    # initiation command for work from daemon
    daemon = MyDaemon('/tmp/daem_email.pid')
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
