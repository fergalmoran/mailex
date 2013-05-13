#!/usr/bin/env python
import smtplib, os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import argparse, getpass, socket, sys


def send_mail(send_from, send_to, subject, text, files=[], server="localhost"):
    assert type(send_to) == list
    assert type(files) == list

    try:
        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach(MIMEText(text))

        for f in files:
            try:
                part = MIMEBase('application', "octet-stream")
                part.set_payload(open(f, "rb").read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
                msg.attach(part)
            except TypeError:
                print "Failed to attach file: %s" % f

        smtp = smtplib.SMTP(server)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()
    except smtplib.SMTPRecipientsRefused, smtpE:
        print smtpE.message

def _get_default_from():
    return "%s@%s" % (getpass.getuser(), socket.gethostname())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sends email, inclucing attachments, from the command line')
    #commands
    parser.add_argument("-v", "--version", action="version", version="0.1")

    #required
    parser.add_argument("-t", "--to-address", metavar="TO", help="To address", required=True)

    #optional
    parser.add_argument("-f", "--from-address", metavar="FROM",  default=_get_default_from(), help="From address")
    parser.add_argument("-a", "--attachments", nargs="?", help="File(s) to attach")
    parser.add_argument("-s", "--subject", metavar="SUBJ", help="Mail subject", default="")
    parser.add_argument("-b", "--mail-body", metavar="BODY", help="Mail body", default="")
    args = parser.parse_args()

    #read any piped text
    if sys.stdin.isatty():
        if args.mail_body:
            body = args.mail_body
        else:
            body = raw_input('Enter message\n')
    else:
        body = sys.stdin.read()

    files = []
    if args.attachments:
        files = [args.attachments]

    send_mail(
        send_from=args.from_address,
        send_to=[args.to_address],
        subject=args.subject,
        text=body,
        files=files)
