#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import os
import smtplib
import email.mime.application
from smtplib import SMTPException


class SMTPClient(smtplib.SMTP):
    def transmit(self, sender, receivers, subject, body=None, attachment=None):
        """
        @param body: body used as params of email.mime.Text.MIMEText, it should be a str or tuple
                         if it is a str, the subtype is 'plain', and charset is None
                         if it is a tuple (_text, _subtype='plain', _charset=None), you can specify the subtype and charset
                         for example: if we send body is a html, we need to set body as (htmlcontent, "html")
                        
        """
        logger.debug("Send mail: sender=%s, receivers=%s, subject=%s", sender, receivers, subject)
        msg = email.MIMEMultipart.MIMEMultipart()
        msg.add_header("From", sender)
        msg.add_header("To", ", ".join(receivers))
        msg.add_header("Subject", subject)
        
        if body is not None:
            if isinstance(body, tuple):
                msg.attach(email.mime.Text.MIMEText(*body))
            elif isinstance(body, str):
                msg.attach(email.mime.Text.MIMEText(body))
            else:
                raise TypeError()
        
        if attachment is not None:
            fb = open(attachment, "rb")
            att = email.mime.application.MIMEApplication(fb.read())
            fb.close()
            att.add_header("Content-Disposition", "attachment;filename=%s" % os.path.basename(attachment))
            msg.attach(att)

        try:
            self.sendmail(sender, receivers, msg.as_string())
        except SMTPException:
            logger.exception("Send mail failed")
            raise

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )

    report = r"D:\testreport.html"
    f = open(report, "rb")
    smtp = SMTPClient("172.25.0.3")
    smtp.transmit("sqagroup@siliconimage.com", ["yale.yang@siliconimage.com", "yale.yang@siliconimage.com"], "test subject", (f.read(), "html"))
    f.close()
#     smtp.quit()
#     message = email.message.Message()
#     message.add_header("From", "From %s" % "yale.yang@siliconimage.com")
#     message.add_header("To", "To %s" % ", ".join(["yale.yang@siliconimage.com"]))
#     message.add_header("Subject", "test")
#     message.set_payload("test content")
#     print(message.as_string())