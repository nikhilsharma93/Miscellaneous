#!/usr/bin/python
'''
This script can be used to send messages via your way2sms account.
A major benefit of this to send a common message to several mobile numbers at once.
Note that you are allowed to send a maximum of 140 characters per message.
Please refer to requirements.txt, to see the packages used/necessary.
'''

import urllib2
import cookielib
from getpass import getpass
import sys

while True:
    list_of_numbers = [] ###Enter the mobile numbers
    username = raw_input('Enter Your Registered Mobile Number: ')
    password = getpass()
    message_to_send = raw_input('Enter the message: ')
    if len(message_to_send) > 140:
        print '\nYou typed a message that has more than the permissible number of characters (140). Please try again\n'
    else:
        break

for loopNumber in range(len(list_of_numbers)):
    number = list_of_numbers[loopNumber]
    message_to_send = '+'.join(message_to_send.split(' '))

    #Logging into way2sms
    url = 'http://site24.way2sms.com/Login1.action?'
    data = 'username='+username+'&password='+password+'&Submit=Sign+in'

    #For Cookies:
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    #Header details:
    opener.addheaders = [('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36')]

    try:
        usock = opener.open(url, data)
    except IOError:
        print '\nError while logging in. Check your internet connection.\n'
        sys.exit(1)

    jession_id = str(cj).split('~')[1].split(' ')[0]
    send_sms_url = 'http://site24.way2sms.com/smstoss.action?'
    send_sms_data = 'ssaction=ss&Token='+jession_id+'&mobile='+number+'&message='+message_to_send+'&msgLen='+str(len(message_to_send))
    opener.addheaders = [('Referer', 'http://site25.way2sms.com/sendSMS?Token='+jession_id)]

    try:
        sms_sent_page = opener.open(send_sms_url,send_sms_data)
        print 'SMS has been sent to ',list_of_numbers[loopNumber]
    except IOError:
        print 'Error while sending message to ',list_of_numbers[loopNumber]
        sys.exit(1)
