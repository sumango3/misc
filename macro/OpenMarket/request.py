# very simple requests wrapper for avoiding ban
import requests

class Session(requests.Session):
    def __init__(self):
        super().__init__()
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': '',
            'accept-language': 'ko-KR,ko;q=0.9',
            'sec-ch-ua': '"Chromium";v="112", "Brave";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        }
    def get(self, url):
        return super().get(url)

def get(url, headers={}):
    headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
    headers['Accept-Encoding'] = '' # avoid compression
    headers['Accept-Language'] = 'ko-KR,ko;q=0.9'
    headers['sec-ch-ua'] = '"Chromium";v="112", "Brave";v="112", "Not:A-Brand";v="99"'
    headers['sec-ch-ua-mobile'] = '?0'
    headers['sec-ch-ua-platform'] = '"Windows"'
    headers['sec-fetch-dest'] = 'document'
    headers['sec-fetch-mode'] = 'navigate'
    headers['sec-fetch-site'] = 'none'
    headers['sec-fetch-user'] = '?1'
    headers['sec-gpc'] = '1'
    headers['upgrade-insecure-requests'] = '1'
    headers['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'

    return requests.get(url, headers=headers)
    

if __name__ == '__main__':
    print(get('https://www.naver.com/').text)
