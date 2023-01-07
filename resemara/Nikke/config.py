import os
from string import ascii_letters, digits

cwd = os.path.dirname(__file__)

### macro setting ###

gmailID = 'YourGMailID'
accountPW = 'PassWord1!' # 8~13 characters, including letter, number and special character
macrologpath = os.path.join(cwd, 'log', 'macro')
nickname = '수망고'
# If you want to use non-ascii nickname, you should use clipboard (ADB cannot input non-ascii letters)
useClipboard = any(map(lambda c:c not in ascii_letters+digits, nickname))
## LD player clipboard is buggy; check if copy-paste is working before running 

serverpath = os.path.join(cwd, 'server')
os.makedirs(os.path.join(serverpath, 'images'), exist_ok=True)


### nikke list analyze configuration ###

analyzelogpath = os.path.join(cwd, 'log', 'analyze')
os.makedirs(analyzelogpath, exist_ok=True)

### screen manager configuration ###

screenpath = os.path.join(cwd, 'screen')

### ADB configuration ### 

LDPlayerPath = 'C:\\LDPlayer\\LDPlayer9'
packagename = 'com.proximabeta.nikke'

### GMail API configuration ###

# where to save your oAuth authorization information created with GMail API (default: same folder)
tokenpath = os.path.join(cwd, 'token.json')

# where to place your downloaded credentials.json (default: same folder)
credentialpath = os.path.join(cwd, 'credentials.json')