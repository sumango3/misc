import requests

access_token = '<YOUR_ACCESS_TOKEN_HERE>'

def sendNote(title, body):
    requests.post('https://api.pushbullet.com/v2/pushes',
                  headers = {
                      'Access-Token': access_token,
                      'Content-Type': 'application/json'
                  },
                  json={
                      'title': title,
                      'body': body,
                      'type': 'note'
                  })
def sendLink(title, body, URL):
    requests.post('https://api.pushbullet.com/v2/pushes',
                  headers = {
                      'Access-Token': access_token,
                      'Content-Type': 'application/json'
                  },
                  json={
                      'title': title,
                      'body': body,
                      'url': URL,
                      'type': 'note'
                  })

if __name__ == '__main__':
    sendLink('Github', 'Touch to go Github', 'https://github.com/')
