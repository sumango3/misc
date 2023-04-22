# Korean Open Market Sold out detection

## What does this script do?

It continuously visits open market page to check if the product is sold out,

and if not, sends notification to user's phone via [Pushbullet](https://www.pushbullet.com)

## Requirements

Python 3
- requests

Pushbullet Account
- Access Token for API access

## How to use

1. Add product page to check
    1. Open `main.py`
    2. Edit  `checklist`, setting `URL`, `selling` (if currently selling), `soldoutText` (text to check if sold out), `lastcheck` (None as default)
    3. Run `main.py`, check if it correctly parses product state
2. Edit `pushbullet` configuration
    1. If you have not, sign up at [Pushbullet](https://www.pushbullet.com)
    2. Go to [Settings - Account](https://www.pushbullet.com/#settings/account)
    3. At `Access Tokens` tab, click `Create Access Token` button
    4. Open `pushbullet.py`, copy-paste your access token to `access_token`
    5. Install pushbullet application on your phone, then sign in with same account
    6. Ruin `pushbullet.py`, check if the push is correctly sent
3. Run `main.py`
