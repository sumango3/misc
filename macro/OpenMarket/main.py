import time
import datetime

import request
import pushbullet

checklist = {
    # Examples below are Roborock S8 Ultra product pages
    'coupang': {
        'URL': 'https://www.coupang.com/vp/products/7245496424',
        'selling': False,
        'soldoutText': '일시품절',
        'lastcheck': None
    },
    'Gmarket': {
        'URL': 'http://item.gmarket.co.kr/Item?goodscode=2884284059',
        'selling': False,
        'soldoutText': 'SOLD OUT',
        'lastcheck': None
    },
    'auction': {
        'URL': 'http://itempage3.auction.co.kr/DetailView.aspx?ItemNo=D285836236&frm3=V2',
        'selling': False,
        'soldoutText': '현재 구매가 불가능한 상품입니다.',
        'lastcheck': None
    },
    'Naver': {
        'URL': 'https://brand.naver.com/roborock/products/8252030653',
        'selling': False,
        'soldoutText': '이 상품은 현재 구매하실 수 없는 상품입니다.',
        'lastcheck': None
    },
    '11st': {
        'URL': 'https://www.11st.co.kr/products/5673574228',
        'selling': False,
        'soldoutText': '현재 판매중인 상품이 아닙니다.',
        'lastcheck': None
    }
}
while True:
    for product, productinfo in checklist.items():
        try:
            res = request.get(productinfo['URL'])
            resp = res.text
            sellingnow = productinfo['soldoutText'] not in resp
            productinfo['lastcheck'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if productinfo['selling'] != sellingnow:
                productinfo['selling'] = sellingnow
                if sellingnow:
                    pushbullet.sendLink(product, '{} is now selling'.format(product), URL)
                else:
                    pushbullet.sendNote(product, '{} sold out'.format(product))
        except Exception as e:
            pass
        print('[{}]\t{}\t{}'.format(productinfo['lastcheck'], product, 'Selling ' if productinfo['selling'] else 'Sold out'))
    
    for _ in range(len(checklist.keys())-1):
        print('\033[F', end='')
    print('\033[A', end='')
    time.sleep(5)
