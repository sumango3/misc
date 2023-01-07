import os
import re
import time

# GMail API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from bs4 import BeautifulSoup

# config.py
from config import tokenpath, credentialpath

# Original code from https://www.geeksforgeeks.org/how-to-read-emails-from-gmail-using-gmail-api-in-python/

class Gmail:
    def __init__(self):
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        creds = None
        if os.path.exists(tokenpath):
            creds = Credentials.from_authorized_user_file(tokenpath, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentialpath, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(tokenpath, 'w') as token:
                token.write(creds.to_json())
        self.service = build('gmail', 'v1', credentials=creds)
    def getMail(self):
        result = self.service.users().messages().list(maxResults=10, userId='me').execute()
        messages = result.get('messages')
        res = []
        for msg in messages:
            # Get the message from its id
            txt = self.service.users().messages().get(userId='me', id=msg['id']).execute()
            # Get value of 'payload' from dictionary 'txt'
            #print('txt: {}'.format(txt))
            payload = txt['payload']
            #print('payload: {}'.format(payload))
            headers = payload['headers']
            #print('headers: {}'.format(headers))
            # Look for Subject and Sender Email in the headers
            for d in headers:
                #print('header: {}'.format(d))
                if d['name'] == 'Subject':
                    subject = d['value']
                if d['name'] == 'From':
                    sender = d['value']
                if d['name'] == 'Delivered-To':
                    receiver = d['value']
            # The Body of the message is in Encrypted format. So, we have to decode it.
            # Get the data and decode it with base 64 decoder.
            parts = payload.get('parts')[0]
            #print('parts: {}'.format(parts))
            data = None
            try:
                try:
                    data = parts['body']['data']
                except Exception as e:
                    data = parts['parts'][0]['body']['data']
            except:
                #print(parts)
                continue
            data = data.replace("-","+").replace("_","/")
            decoded_data = base64.b64decode(data)

            # Now, the data obtained is in lxml. So, we will parse 
            # it with BeautifulSoup library
            soup = BeautifulSoup(decoded_data , "lxml")
            body = soup.body()

            # Printing the subject, sender's email and message
            res.append({
                "subject": subject,
                "from": sender,
                "to": receiver,
                "body": str(body[0])
            })
        return res
    def getCode(self, mailaddr):
        while True:
            try:
                for mail in self.getMail():
                    #print(mail)
                    if mail['to'] == mailaddr:
                        o = re.search(r'<font color=\"#FFFFFF\" size=\"6\">\s*(\d{6})\s*<\/font>', mail['body'])
                        if o != None:
                            return o.group(1)
                return None
            except Exception:
                time.sleep(3)
        return None
