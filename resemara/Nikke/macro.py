import os
import time
import logging
from uuid import uuid4
import random
from statistics import mean
import math
import clipboard
import gc

from game import Screen, GameManager, Button
from gmail import Gmail
from config import gmailID, accountPW, macrologpath, nickname, useClipboard, serverpath
from imageprocessing import findenemy, findcrosshair

def macro(deviceidx, quit):
    logging.basicConfig(
        filename=os.path.join(macrologpath, str(deviceidx)+'.log'),
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(message)s'
    )
    logging.info('macro start')
    GM = GameManager(deviceidx)
    logging.info('game manager loaded')
    mail = Gmail()
    logging.info('gmail loaded')

    signup = False
    accountID = None
    mailaddr = None
    clearedStage = 0
    inputName = False
    simulationUnlock = False
    arkTutorial = False
    mailReceived = False
    pulled = False
    checked = False
    retrynum = 0
    good = False
    squadset = False
    profileset = False
    backedup = False
    while not quit.value:

        retrynum += 1
        if retrynum >= 5:
            # failed to detect image
            # app might be frozen
            GM.kill()
            retrynum = 0
        if not GM.alive():
            GM.launch()
            time.sleep(20)
            GM.wait(Screen.NOTICE, Screen.SELECTSERVER, Screen.SIGNIN, Screen.TOUCHTOCONTINUE, 60)
        try:
            if GM.check(Screen.NOTICE):
                GM.tap(598, 118) # close Notice
                time.sleep(20)
                GM.wait(Screen.SELECTSERVER, Screen.SIGNIN, Screen.TOUCHTOCONTINUE, 60)
            if GM.check(Screen.SELECTSERVER):
                GM.tap(480, 392) # OK with current server
                GM.wait(Screen.SIGNIN, Screen.TOUCHTOCONTINUE, 60)
            if GM.check(Screen.SIGNIN):
                time.sleep(1)
                if signup:
                    time.sleep(1)
                    GM.tap(400, 144) # type mailaddress
                    GM.wait(Screen.TEXTINPUT, 5)
                    GM.text(mailaddr)
                    time.sleep(1)
                    GM.tap(Button.TEXTCONFIRM)
                    time.sleep(1)
                    GM.text(accountPW)
                    GM.tap(Button.TEXTCONFIRM)
                    time.sleep(1)
                    GM.tap(480, 248) # Game Start
                    time.sleep(10)
                    GM.wait(Screen.TOUCHTOCONTINUE, 60)
                else:
                    GM.tap(395, 209) # Signup
                    time.sleep(1)
                    GM.wait(Screen.SIGNUP)
            if GM.check(Screen.SIGNUP):
                accountID = uuid4().hex[:8]
                mailaddr = '{}+{}@gmail.com'.format(gmailID, accountID)
                logging.info('new account: {}'.format(mailaddr))
                time.sleep(1)
                GM.tap(400, 172) # type mailaddress
                if not GM.wait(Screen.TEXTINPUT, 5):
                    GM.tap(400, 172)
                    GM.wait(Screen.TEXTINPUT, 5)
                GM.text(mailaddr)
                time.sleep(1)
                GM.tap(Button.TEXTCONFIRM)
                GM.text(accountPW)
                time.sleep(1)
                GM.tap(Button.TEXTCONFIRM)
                GM.text(accountPW)
                time.sleep(1)
                GM.tap(Button.TEXTCONFIRM)
                GM.tap(551, 337) # Auth code send
                code = None
                for _ in range(5):
                    time.sleep(5)
                    try:
                        code = mail.getCode(mailaddr)
                        if code:
                            break
                    except:
                        pass
                if code == None:
                    #raise Exception('Auth code receive failed')
                    GM.kill()
                    continue
                GM.tap(480, 350)
                GM.wait(Screen.SIGNUP)
                GM.tap(380, 338) # type authcode
                GM.wait(Screen.TEXTINPUT)
                GM.text(code)
                GM.tap(Button.TEXTCONFIRM)
                GM.tap(537, 389) # signup confirm
                time.sleep(10)
                if GM.wait(Screen.TOUCHTOCONTINUE, 60):
                    signup = True
            if GM.check(Screen.TOUCHTOCONTINUE):
                if not signup or accountID == None or mailaddr == None:
                    # logout, then start from creating new account
                    GM.tap(22, 78) # logout
                    time.sleep(5)
                    GM.tap(550, 340) # confirm
                    time.sleep(5)
                    GM.wait(Screen.NOTICE, Screen.SELECTSERVER, Screen.SIGNIN, 60)
                    retrynum -= 1 # this is not due to screen check error
                    continue
                GM.tap(Button.TAP)
                time.sleep(20)
                if clearedStage == 0:
                    GM.wait(Screen.OPERATION01PRESTORY, Screen.OPERATION01TUTORIAL1, 30)
                elif clearedStage == 1:
                    GM.wait(Screen.FIELD0TUTORIAL1, Screen.FIELD0, 30)
                elif clearedStage == 2:
                    GM.wait(Screen.FIELD0, 30)
                elif clearedStage == 3:
                    GM.wait(Screen.FIELD1TUTORIAL1, Screen.FIELD1, 30)
                elif 11 <= clearedStage <= 13:
                    GM.wait(Screen.FIELD1, 30)
                elif 14 <= clearedStage:
                    GM.wait(Screen.LOBBYTUTORIAL1, Screen.LOBBYTUTORIAL2, Screen.LOBBYNOTICE, Screen.LOBBY, 30)
            if GM.check(Screen.OPERATION01PRESTORY):
                GM.tap(Button.SKIP)
                time.sleep(10)
                GM.wait(Screen.OPERATION01TUTORIAL1, 30)
            if GM.check(Screen.OPERATION01TUTORIAL1):
                time.sleep(1)
                GM.swipe(-200, 0, 2000)
                time.sleep(5)
                GM.wait(Screen.OPERATION01TUTORIAL2, 30)
            if GM.check(Screen.OPERATION01TUTORIAL2):
                time.sleep(1)
                GM.tap(Button.SKIP)
                GM.wait(Screen.OPERATIONTUTORIALSKIPNOTICE, 5)
            if GM.check(Screen.OPERATIONTUTORIALSKIPNOTICE):
                GM.tap(Button.TUTORIALSKIPCONFIRM)
                time.sleep(1)
                GM.swipe(480, 270, 780, 270, 1000)
            if clearedStage == 0 and GM.check(Screen.OPERATION):
                lastshoot = 0
                while clearedStage == 0:
                    if not GM.alive():
                        break
                    res = GM.check(Screen.OPERATIONFAILED, Screen.LEVELUP2, Screen.OPERATION01CLEAR, Screen.FIELD0)
                    if res == Screen.OPERATIONFAILED:
                        GM.tap(Button.RETRY)
                        time.sleep(5)
                        continue
                    elif res == Screen.OPERATION01CLEAR or res == Screen.LEVELUP2:
                        clearedStage = 1
                        GM.wait(Screen.LEVELUP2, 10)
                        break
                    elif res == Screen.FIELD0:
                        break
                    scr = GM.screen()
                    crosshair = findcrosshair(scr)
                    if crosshair['found']:
                        crosshairY, crosshairX = crosshair['y'], crosshair['x']
                        enemies = findenemy(GM.screen())
                        if len(enemies) == 0:
                            logging.debug('no enemy found')
                            # no enemies found: probably error
                            # check if operation is already over
                            res = GM.check(Screen.OPERATIONFAILED, Screen.LEVELUP2, Screen.OPERATION01CLEAR, Screen.FIELD0)
                            if res == Screen.OPERATIONFAILED:
                                GM.tap(Button.RETRY)
                                time.sleep(5)
                                continue
                            elif res == Screen.OPERATION01CLEAR or res == Screen.LEVELUP2:
                                clearedStage = 1
                                GM.wait(Screen.LEVELUP2, 10)
                                break
                            elif res == Screen.FIELD0:
                                break
                            angle = random.random() * math.pi * 2
                            radius = 100
                            dy = math.cos(angle) * radius
                            dx = math.sin(angle) * radius
                            GM.swipe(dx, dy, 100)
                        elif len(enemies) < 5:
                            logging.debug('several enemies found')
                            # several enemies found: manually target them
                            enemyY, enemyX = enemies[0]
                            dy = enemyY - crosshairY
                            dx = enemyX - crosshairX
                            swipey = dy*2
                            swipex = dx*3
                            swipenum = max(math.ceil(abs(swipey)/270), math.ceil(abs(swipex)/480))
                            cmd = ''
                            for _ in range(swipenum):
                                randy = random.randint(-3, 4)
                                randx = random.randint(-3, 4)
                                cmd += 'input swipe {} {} {} {} {}; sleep 0.1;'.format(480+randx, 270+randy, 480+(swipex//swipenum)+randx, 270+(swipey//swipenum)+randy, 100)
                                # aim toward the enemy
                            randy = random.randint(-3, 4)
                            randx = random.randint(-3, 4)
                            # shoot for 3 seconds
                            cmd += 'input swipe {} {} {} {} {}'.format(480+randx, 270+randy, 480+randx, 270+randy, 3000)
                            #GM.swipe(0, 0, 3000)
                            res = GM.check(Screen.OPERATIONFAILED, Screen.LEVELUP2, Screen.OPERATION01CLEAR, Screen.FIELD0)
                            if res == Screen.OPERATIONFAILED:
                                GM.tap(Button.RETRY)
                                time.sleep(5)
                                continue
                            elif res == Screen.OPERATION01CLEAR or res == Screen.LEVELUP2:
                                clearedStage = 1
                                GM.wait(Screen.LEVELUP2, 10)
                                break
                            elif res == Screen.FIELD0:
                                break
                            GM.sh(cmd)
                        else:
                            # many enemies found: shoot everywhere
                            logging.debug('many enemies found')
                            dx, scanX = 0, 0
                            if crosshairX < 480:
                                # scan from left to right
                                dx = min(map(lambda c:c[1], enemies)) - crosshairX
                                scanX = 240
                            else:
                                dx = max(map(lambda c:c[1], enemies)) - crosshairX
                                scanX = -240
                            dy = mean(map(lambda c:c[0], enemies)) - crosshairY
                            swipex = dx*3
                            swipey = dy*2
                            swipenum = max(math.ceil(abs(swipey)/270), math.ceil(abs(swipex)/480))
                            cmd = ''
                            for _ in range(swipenum):
                                randy = random.randint(-3, 4)
                                randx = random.randint(-3, 4)
                                # aim toward the enemy
                                cmd += 'input swipe {} {} {} {} {}; sleep 0.1;'.format(480+randx, 270+randy, 480+(swipex//swipenum)+randx, 270+(swipey//swipenum)+randy, 100)
                            GM.sh(cmd)
                            for _ in range(3):
                                res = GM.check(Screen.OPERATIONFAILED, Screen.LEVELUP2, Screen.OPERATION01CLEAR, Screen.FIELD0)
                                if res == Screen.OPERATIONFAILED:
                                    GM.tap(Button.RETRY)
                                    time.sleep(5)
                                    continue
                                elif res == Screen.OPERATION01CLEAR or res == Screen.LEVELUP2:
                                    clearedStage = 1
                                    GM.wait(Screen.LEVELUP2, 10)
                                    break
                                elif res == Screen.FIELD0:
                                    break
                                randy = random.randint(-3, 4)
                                randx = random.randint(-3, 4)
                                # aim toward the enemy
                                GM.swipe(scanX, 0, 3000)
                    else:
                        # could not detect crosshair
                        # move random direction
                        angle = random.random() * math.pi * 2
                        radius = 300
                        dx = math.cos(angle) * radius
                        dy = math.sin(angle) * radius
                        GM.swipe(dx, dy, 1000)
            if not GM.alive():
                continue
            if GM.check(Screen.LEVELUP2):
                clearedStage = 1
                time.sleep(1)
                GM.tap(Button.TAP)
                GM.wait(Screen.OPERATION01CLEAR, 5)
            if GM.check(Screen.OPERATION01CLEAR):
                clearedStage = 1
                time.sleep(1)
                GM.tap(Button.TAP)
                time.sleep(5)
                GM.wait(Screen.OPERATION01POSTSTORY, 30)
            if GM.check(Screen.OPERATION01POSTSTORY):
                clearedStage = 1
                time.sleep(1)
                GM.tap(Button.SKIP)
                time.sleep(10)
                GM.wait(Screen.FIELD0TUTORIAL1, 30)
            if (clearedStage == 1 and GM.check(Screen.FIELD0)) or GM.check(Screen.FIELD0TUTORIAL1):
                clearedStage = 1
                time.sleep(5)
                GM.tap(740, 170) # 0-2
                time.sleep(5)
                if not GM.wait(Screen.FIELD0TUTORIAL2, Screen.OPERATION02ENTER, 10):
                    GM.tap(390, 180) # 0-3
                    time.sleep(5)
                    if GM.wait(Screen.OPERATION03ENTERDARK, Screen.OPERATION03ENTER, 10):
                        clearedStage = 2
            if GM.check(Screen.FIELD0TUTORIAL2, Screen.OPERATION02ENTER):
                time.sleep(1)
                GM.tap(Button.OPERATIONENTER)
                time.sleep(5)
                GM.wait(Screen.OPERATION02PRESTORY, Screen.OPERATION, 30)
            if GM.check(Screen.OPERATION02PRESTORY):
                GM.tap(Button.SKIP)
                time.sleep(10)
                GM.wait(Screen.OPERATION, 30)
            if (clearedStage == 1 and GM.check(Screen.OPERATION)) or GM.check(Screen.OPERATION02TUTORIAL):
                lastshoot = 0
                tutorialskip = False
                res = None
                while clearedStage == 1:
                    if not GM.alive():
                        break
                    if tutorialskip:
                        res = GM.check(Screen.OPERATION, Screen.OPERATIONFAILED, Screen.OPERATION02CLEAR, Screen.FIELD0, Screen.OPERATION03ENTER, Screen.OPERATION03ENTERDARK)
                    else:
                        res = GM.check(Screen.OPERATION, Screen.OPERATION02TUTORIAL, Screen.OPERATIONTUTORIALSKIPNOTICE, Screen.OPERATIONFAILED, Screen.OPERATION02CLEAR, Screen.FIELD0, Screen.OPERATION03ENTER, Screen.OPERATION03ENTERDARK)
                    if res == Screen.OPERATION02TUTORIAL:
                        GM.tap(Button.SKIP)
                        res = GM.wait(Screen.OPERATIONTUTORIALSKIPNOTICE, 10)
                    if res == Screen.OPERATIONTUTORIALSKIPNOTICE:
                        GM.tap(Button.TUTORIALSKIPCONFIRM)
                        tutorialskip = True
                    elif res == Screen.OPERATIONFAILED:
                        GM.tap(Button.RETRY)
                        time.sleep(5)
                        continue
                    elif res == Screen.OPERATION02CLEAR or res == Screen.FIELD0 or res == Screen.OPERATION03ENTER or res == Screen.OPERATION03ENTERDARK:
                        clearedStage = 2
                        break
                    else:
                        res = GM.wait(Screen.OPERATION, Screen.OPERATION02TUTORIAL, Screen.OPERATIONFAILED, 10)
                        if res == None:
                            break
                        elif res != Screen.OPERATION:
                            continue
                    GM.tap(920, 270) # Burst skill
                    crosshair = findcrosshair(GM.screen())
                    if crosshair['found']:
                        crosshairY, crosshairX = crosshair['y'], crosshair['x']
                        enemies = findenemy(GM.screen())
                        if len(enemies) == 0:
                            # no enemies found: probably error
                            # check if operation is already over
                            if tutorialskip:
                                res = GM.check(Screen.OPERATION, Screen.OPERATIONFAILED, Screen.OPERATION02CLEAR, Screen.FIELD0, Screen.OPERATION03ENTER, Screen.OPERATION03ENTERDARK)
                            else:
                                res = GM.check(Screen.OPERATION, Screen.OPERATION02TUTORIAL, Screen.OPERATIONTUTORIALSKIPNOTICE, Screen.OPERATIONFAILED, Screen.OPERATION02CLEAR, Screen.FIELD0, Screen.OPERATION03ENTER, Screen.OPERATION03ENTERDARK)
                            if res == Screen.OPERATION02TUTORIAL:
                                GM.tap(Button.SKIP)
                                res = GM.wait(Screen.OPERATIONTUTORIALSKIPNOTICE, 10)
                            if res == Screen.OPERATIONTUTORIALSKIPNOTICE:
                                GM.tap(Button.TUTORIALSKIPCONFIRM)
                                tutorialskip = True
                            elif res == Screen.OPERATIONFAILED:
                                GM.tap(Button.RETRY)
                                time.sleep(5)
                                continue
                            elif res == Screen.OPERATION02CLEAR or res == Screen.FIELD0 or res == Screen.OPERATION03ENTER or res == Screen.OPERATION03ENTERDARK:
                                clearedStage = 2
                                break
                            else:
                                res = GM.wait(Screen.OPERATION, Screen.OPERATION02TUTORIAL, Screen.OPERATIONFAILED, 10)
                                if res == None:
                                    break
                                elif res != Screen.OPERATION:
                                    continue
                            angle = random.random() * math.pi * 2
                            radius = 100
                            dy = math.cos(angle) * radius
                            dx = math.sin(angle) * radius
                            GM.swipe(dx, dy, 100)
                        elif len(enemies) < 5:
                            # several enemies found: manually target them
                            enemyY, enemyX = enemies[0]
                            dy = enemyY - crosshairY
                            dx = enemyX - crosshairX
                            swipey = dy*2
                            swipex = dx*3
                            swipenum = max(math.ceil(abs(swipey)/270), math.ceil(abs(swipex)/480))
                            cmd = ''
                            for _ in range(swipenum):
                                if tutorialskip:
                                    res = GM.check(Screen.OPERATION, Screen.OPERATIONFAILED, Screen.OPERATION02CLEAR, Screen.FIELD0, Screen.OPERATION03ENTER, Screen.OPERATION03ENTERDARK)
                                else:
                                    res = GM.check(Screen.OPERATION, Screen.OPERATION02TUTORIAL, Screen.OPERATIONTUTORIALSKIPNOTICE, Screen.OPERATIONFAILED, Screen.OPERATION02CLEAR, Screen.FIELD0, Screen.OPERATION03ENTER, Screen.OPERATION03ENTERDARK)
                                if res == Screen.OPERATION02TUTORIAL:
                                    GM.tap(Button.SKIP)
                                    res = GM.wait(Screen.OPERATIONTUTORIALSKIPNOTICE, 10)
                                if res == Screen.OPERATIONTUTORIALSKIPNOTICE:
                                    GM.tap(Button.TUTORIALSKIPCONFIRM)
                                    tutorialskip = True
                                elif res == Screen.OPERATIONFAILED:
                                    GM.tap(Button.RETRY)
                                    time.sleep(5)
                                    continue
                                elif res == Screen.OPERATION02CLEAR or res == Screen.FIELD0 or res == Screen.OPERATION03ENTER or res == Screen.OPERATION03ENTERDARK:
                                    clearedStage = 2
                                    break
                                else:
                                    res = GM.wait(Screen.OPERATION, Screen.OPERATION02TUTORIAL, Screen.OPERATIONFAILED, 10)
                                    if res == None:
                                        break
                                    elif res != Screen.OPERATION:
                                        continue
                                randy = random.randint(-3, 4)
                                randx = random.randint(-3, 4)
                                # aim toward the enemy
                                cmd += 'input swipe {} {} {} {} {}; sleep 0.1;'.format(480+randx, 270+randy, 480+(swipex//swipenum)+randx, 270+(swipey//swipenum)+randy, 300)
                            randy = random.randint(-3, 4)
                            randx = random.randint(-3, 4)
                            # shoot for 2.5 seconds
                            cmd += 'input swipe {} {} {} {} {}; sleep 0.1;'.format(480+randx, 270+randy, 480+randx, 270+randy, 2500)
                            if tutorialskip:
                                res = GM.check(Screen.OPERATION, Screen.OPERATIONFAILED, Screen.OPERATION02CLEAR, Screen.FIELD0, Screen.OPERATION03ENTER, Screen.OPERATION03ENTERDARK)
                            else:
                                res = GM.check(Screen.OPERATION, Screen.OPERATION02TUTORIAL, Screen.OPERATIONTUTORIALSKIPNOTICE, Screen.OPERATIONFAILED, Screen.OPERATION02CLEAR, Screen.FIELD0, Screen.OPERATION03ENTER, Screen.OPERATION03ENTERDARK)
                            if res == Screen.OPERATION02TUTORIAL:
                                GM.tap(Button.SKIP)
                                res = GM.wait(Screen.OPERATIONTUTORIALSKIPNOTICE, 10)
                            if res == Screen.OPERATIONTUTORIALSKIPNOTICE:
                                GM.tap(Button.TUTORIALSKIPCONFIRM)
                                tutorialskip = True
                            elif res == Screen.OPERATIONFAILED:
                                GM.tap(Button.RETRY)
                                time.sleep(5)
                                continue
                            elif res == Screen.OPERATION02CLEAR or res == Screen.FIELD0 or res == Screen.OPERATION03ENTER or res == Screen.OPERATION03ENTERDARK:
                                clearedStage = 2
                                break
                            else:
                                    res = GM.wait(Screen.OPERATION, Screen.OPERATION02TUTORIAL, Screen.OPERATIONFAILED, 10)
                                    if res == None:
                                        break
                                    elif res != Screen.OPERATION:
                                        continue
                            GM.sh(cmd)
                        else:
                            # many enemies found: shoot everywhere
                            dx, scanX = 0, 0
                            if crosshairX < 480:
                                # scan from left to right
                                dx = min(map(lambda c:c[1], enemies)) - crosshairX
                                scanX = 240
                            else:
                                dx = max(map(lambda c:c[1], enemies)) - crosshairX
                                scanX = -240
                            dy = mean(map(lambda c:c[0], enemies)) - crosshairY
                            swipex = dx*3
                            swipey = dy*2
                            swipenum = max(math.ceil(abs(swipey)/270), math.ceil(abs(swipex)/480))
                            cmd = ''
                            for _ in range(swipenum):
                                randy = random.randint(-3, 4)
                                randx = random.randint(-3, 4)
                                # aim toward the enemy
                                cmd += 'input swipe {} {} {} {} {}; sleep 0.1;'.format(480+randx, 270+randy, 480+(swipex//swipenum)+randx, 270+(swipey//swipenum)+randy, 100)
                            GM.sh(cmd)
                            for _ in range(3):
                                if tutorialskip:
                                    res = GM.check(Screen.OPERATION, Screen.OPERATIONFAILED, Screen.OPERATION02CLEAR, Screen.FIELD0, Screen.OPERATION03ENTER, Screen.OPERATION03ENTERDARK)
                                else:
                                    res = GM.check(Screen.OPERATION, Screen.OPERATION02TUTORIAL, Screen.OPERATIONTUTORIALSKIPNOTICE, Screen.OPERATIONFAILED, Screen.OPERATION02CLEAR, Screen.FIELD0, Screen.OPERATION03ENTER, Screen.OPERATION03ENTERDARK)
                                if res == Screen.OPERATION02TUTORIAL:
                                    GM.tap(Button.SKIP)
                                    res = GM.wait(Screen.OPERATIONTUTORIALSKIPNOTICE, 10)
                                if res == Screen.OPERATIONTUTORIALSKIPNOTICE:
                                    GM.tap(Button.TUTORIALSKIPCONFIRM)
                                    tutorialskip = True
                                elif res == Screen.OPERATIONFAILED:
                                    GM.tap(Button.RETRY)
                                    time.sleep(5)
                                    continue
                                elif res == Screen.OPERATION02CLEAR or res == Screen.FIELD0 or res == Screen.OPERATION03ENTER or res == Screen.OPERATION03ENTERDARK:
                                    clearedStage = 2
                                    break
                                else:
                                    res = GM.wait(Screen.OPERATION, Screen.OPERATION02TUTORIAL, Screen.OPERATIONFAILED, 10)
                                    if res == None:
                                        break
                                    elif res != Screen.OPERATION:
                                        continue
                                randy = random.randint(-3, 4)
                                randx = random.randint(-3, 4)
                                # aim toward the enemy
                                GM.swipe(scanX, 0, 3000)
                    else:
                        # could not detect crosshair
                        # move random direction
                        angle = random.random() * math.pi * 2
                        radius = 100
                        dx = math.cos(angle) * radius
                        dy = math.sin(angle) * radius
                        GM.swipe(int(dx), int(dy), 1000)
                        # possibly reload
                        time.sleep(2)
            if not GM.alive():
                continue
            if GM.check(Screen.OPERATION02CLEAR):
                clearedStage = 2
                time.sleep(1)
                GM.tap(480, 480)
                time.sleep(1)
                GM.wait(Screen.FIELD0, 30)
            if clearedStage == 2 and GM.check(Screen.FIELD0):
                time.sleep(1)
                GM.tap(390, 190) # 0-3
                time.sleep(5)
                GM.wait(Screen.OPERATION03ENTERDARK, Screen.OPERATION03ENTER, 5)
            if GM.check(Screen.OPERATION03ENTERDARK, Screen.OPERATION03ENTER):
                time.sleep(1)
                GM.tap(Button.OPERATIONENTER)
                GM.wait(Screen.OPERATION03PRESTORY, Screen.OPERATION, 30)
            if GM.check(Screen.OPERATION03PRESTORY):
                GM.tap(Button.SKIP)
                time.sleep(10)
                GM.wait(Screen.OPERATION, 30)
            if clearedStage == 2 and GM.check(Screen.OPERATION):
                while clearedStage == 2:
                    if not GM.alive():
                        break
                    time.sleep(5)
                    GM.swipe(-200, 0, 2000)
                    GM.wait(Screen.OPERATION03TUTORIAL1, 5)
                    GM.tap(360, 480) # Choose Nikke 1
                    if GM.wait(Screen.OPERATION03TUTORIAL2, 5):
                        GM.tap(Button.SKIP)
                        time.sleep(1)
                        GM.wait(Screen.OPERATIONTUTORIALSKIPNOTICE, 5)
                        GM.tap(Button.TUTORIALSKIPCONFIRM)
                        time.sleep(5)
                    GM.swipe(-250, -230, 1000)
                    GM.swipe(0, 0, 1000)
                    GM.swipe(0, 0, 1000)
                    time.sleep(10)
                    GM.swipe(180, -70, 1000)
                    GM.swipe(0, 0, 1000)
                    GM.swipe(0, 0, 1000)
                    time.sleep(60)
                    if GM.wait(Screen.LEVELUP3, 30):
                        clearedStage = 3
                        break
                    elif GM.check(Screen.OPERATIONFAILED):
                        GM.tap(Button.RETRY)
                        time.sleep(5)
                        GM.wait(Screen.OPERATION, 30)
                    else:
                        GM.tap(Button.PAUSE)
                        time.sleep(1)
                        GM.tap(Button.RESTART)
                        time.sleep(10)
                        GM.wait(Screen.OPERATION, 30)
            if GM.check(Screen.LEVELUP3):
                clearedStage = 3
                time.sleep(1)
                GM.tap(Button.TAP)
                time.sleep(1)
                GM.wait(Screen.OPERATION03CLEAR, 5)
            if GM.check(Screen.OPERATION03CLEAR):
                clearedStage = 3
                time.sleep(1)
                GM.tap(Button.TAP)
                time.sleep(5)
                GM.wait(Screen.OPERATION03POSTSTORY, 10)
            if GM.check(Screen.OPERATION03POSTSTORY):
                clearedStage = 3
                time.sleep(1)
                GM.tap(Button.SKIP)
                time.sleep(1)
                GM.wait(Screen.NAMEINPUT, 10)
            if GM.check(Screen.NAMEINPUT):
                clearedStage = 3
                time.sleep(1)
                GM.tap(480, 260) # Name input
                time.sleep(1)
                GM.wait(Screen.TEXTINPUT, 10)
            if clearedStage == 3 and GM.check(Screen.TEXTINPUT):
                time.sleep(1)
                if useClipboard:
                    clipboard.copy(nickname)
                    time.sleep(1)
                    GM.paste()
                else:
                    for chr in nickname:
                        GM.text(chr)
                time.sleep(1)
                GM.tap(Button.TEXTCONFIRM)
                time.sleep(1)
                GM.tap(480, 330) # Name Confirm
                inputName = True
                GM.wait(Screen.STORY, 5)
            if clearedStage == 3 and inputName and GM.check(Screen.STORY):
                GM.tap(Button.SKIP)
                time.sleep(10)
                GM.wait(Screen.CHAPTER0CLEAR)
            if GM.check(Screen.CHAPTER0CLEAR):
                clearedStage = 3
                time.sleep(5)
                GM.tap(Button.TAP)
                time.sleep(10)
                GM.wait(Screen.FIELD1TUTORIAL1, 30)
            if GM.check(Screen.FIELD1TUTORIAL1):
                clearedStage = 3
                time.sleep(1)
                GM.tap(Button.SKIP)
                time.sleep(1)
                GM.wait(Screen.TUTORIALSKIPNOTICE)
            if clearedStage == 3 and GM.check(Screen.TUTORIALSKIPNOTICE):
                time.sleep(1)
                GM.tap(Button.TUTORIALSKIPCONFIRM)
                time.sleep(1)
                GM.wait(Screen.FIELD1, 5)
            if clearedStage == 3 and GM.check(Screen.FIELD1):
                time.sleep(5)
                GM.tap(360, 320) # 1-1
                time.sleep(1)
                GM.wait(Screen.OPERATION11ENTER, 5)
            if GM.check(Screen.OPERATION11ENTER):
                clearedStage = 3
                GM.tap(Button.OPERATIONENTER)
                time.sleep(5)
                GM.wait(Screen.OPERATION11PRESTORY, 10)
            if GM.check(Screen.OPERATION11PRESTORY):
                clearedStage = 3
                GM.tap(Button.SKIP)
                time.sleep(20)
                GM.wait(Screen.OPERATION11TUTORIAL, 30)
            if GM.check(Screen.OPERATION11TUTORIAL):
                clearedStage = 3
                GM.tap(Button.SKIP)
                time.sleep(1)
                GM.wait(Screen.OPERATIONTUTORIALSKIPNOTICE, 5)
            if clearedStage == 3 and GM.check(Screen.OPERATIONTUTORIALSKIPNOTICE):
                GM.tap(Button.TUTORIALSKIPCONFIRM)
                time.sleep(40)
                GM.wait(Screen.OPERATION11CLEAR, 60)
            if GM.check(Screen.OPERATION11CLEAR):
                clearedStage = 11
                GM.tap(Button.TAP)
                time.sleep(5)
                GM.wait(Screen.OPERATION11POSTSTORY, 10)
            if GM.check(Screen.OPERATION11POSTSTORY):
                clearedStage = 11
                GM.tap(Button.SKIP)
                time.sleep(10)
                GM.wait(Screen.FIELD1, 30)
            if clearedStage == 11 and GM.check(Screen.FIELD1):
                time.sleep(0.5)
                GM.tap(280, 150) # 1-2
                time.sleep(2)
                GM.wait(Screen.FIELD1TUTORIAL2, 10)
            if GM.check(Screen.FIELD1TUTORIAL2):
                GM.tap(Button.SKIP)
                time.sleep(1)
                GM.wait(Screen.TUTORIALSKIPNOTICE, 5)
            if clearedStage == 11 and GM.check(Screen.TUTORIALSKIPNOTICE):
                GM.tap(Button.TUTORIALSKIPCONFIRM)
                time.sleep(1)
                GM.wait(Screen.FIELD1, 5)
            if clearedStage == 11 and GM.check(Screen.FIELD1):
                time.sleep(5)
                GM.tap(422, 184) # 1-2
                time.sleep(2)
                GM.wait(Screen.OPERATION12ENTER, 5)
            if GM.check(Screen.OPERATION12ENTER):
                clearedStage = 11
                GM.tap(Button.OPERATIONENTER)
                time.sleep(5)
                GM.wait(Screen.OPERATION12PRESTORY, 10)
            if GM.check(Screen.OPERATION12PRESTORY):
                clearedStage = 11
                GM.tap(Button.SKIP)
                time.sleep(10)
                GM.wait(Screen.OPERATION12TUTORIAL, 10)
            if GM.check(Screen.OPERATION12TUTORIAL):
                clearedStage = 11
                GM.tap(Button.SKIP)
                time.sleep(1)
                GM.wait(Screen.OPERATIONTUTORIALSKIPNOTICE)
            if clearedStage == 11 and GM.check(Screen.OPERATIONTUTORIALSKIPNOTICE):
                GM.tap(Button.TUTORIALSKIPCONFIRM)
                GM.wait(Screen.OPERATION, 5)
            if clearedStage == 11 and GM.check(Screen.OPERATION):
                trynum = 5
                while clearedStage == 11 and trynum > 0:
                    trynum -= 1
                    if GM.wait(Screen.OPERATION12TUTORIAL, 5):
                        GM.tap(Button.SKIP)
                        time.sleep(1)
                        GM.wait(Screen.OPERATIONTUTORIALSKIPNOTICE, 5)
                        GM.tap(Button.TUTORIALSKIPCONFIRM)
                        time.sleep(1)
                        GM.wait(Screen.OPERATION, 5)
                    # The first wave: 1 bot
                    GM.swipe(0, -360, 2000)
                    GM.swipe(0, 0, 2000)
                    GM.swipe(0, 0, 2000)
                    time.sleep(1)

                    # The second wave: 5 bots
                    GM.swipe(-90, -40, 2000)
                    GM.swipe(0, 0, 2000)
                    GM.swipe(0, 0, 2000)
                    time.sleep(5)

                    GM.swipe(-90, -90, 2000)
                    GM.swipe(0, 0, 2000)
                    GM.swipe(0, 0, 2000)

                    GM.swipe(170, 20, 2000)
                    GM.swipe(0, 0, 2000)
                    GM.swipe(0, 0, 2000)
                    time.sleep(5)

                    GM.swipe(90, 60, 2000)
                    GM.swipe(0, 0, 2000)
                    GM.swipe(0, 0, 2000)

                    GM.swipe(90, -90, 2000)
                    GM.swipe(0, 0, 2000)
                    GM.swipe(0, 0, 2000)
                    time.sleep(15)

                    # The third wave: 1 bot
                    GM.swipe(-260, 390, 2000)
                    GM.swipe(5, 5, 2000)
                    GM.swipe(0, -10, 2000)
                    GM.swipe(-10, 0, 2000)
                    GM.swipe(0, 10, 2000)
                    time.sleep(15)

                    if GM.wait(Screen.OPERATION12CLEAR, 30):
                        clearedStage = 12
                        break
                    elif GM.check(Screen.OPERATIONFAILED):
                        GM.tap(Button.RETRY)
                        time.sleep(10)
                        GM.wait(Screen.OPERATION, Screen.OPERATION12TUTORIAL, 10)
                    else:
                        GM.tap(Button.PAUSE)
                        GM.wait(Screen.PAUSE)
                        GM.tap(Button.RESTART)
                        time.sleep(10)
                        GM.wait(Screen.OPERATION, Screen.OPERATION12TUTORIAL, 10)
            if GM.check(Screen.OPERATION12CLEAR):
                clearedStage = 12
                time.sleep(1)
                GM.tap(Button.TAP)
                time.sleep(10)
                GM.wait(Screen.FIELD1, 30)
            if clearedStage == 12 and GM.check(Screen.FIELD1):
                time.sleep(0.5)
                GM.tap(597, 70) # 1-3
                time.sleep(5)
                GM.wait(Screen.OPERATION13ENTER, 5)
            if GM.check(Screen.OPERATION13ENTER):
                clearedStage = 12
                GM.tap(Button.OPERATIONENTER)
                time.sleep(5)
                GM.wait(Screen.OPERATION13PRESTORY)
            if GM.check(Screen.OPERATION13PRESTORY):
                clearedStage = 12
                GM.tap(Button.SKIP)
                time.sleep(10)
                GM.wait(Screen.OPERATION13TUTORIAL, 30)
            if GM.check(Screen.OPERATION13TUTORIAL):
                clearedStage = 12
                GM.tap(Button.SKIP)
                GM.wait(Screen.OPERATIONTUTORIALSKIPNOTICE, 5)
            if clearedStage == 12 and GM.check(Screen.OPERATIONTUTORIALSKIPNOTICE):
                GM.tap(Button.TUTORIALSKIPCONFIRM)
                time.sleep(2)
                GM.wait(Screen.OPERATION, 10)
            if clearedStage == 12 and GM.check(Screen.OPERATION):
                while clearedStage == 12:
                    time.sleep(5)
                    GM.swipe(0, -150, 1000)
                    GM.swipe(0, 0, 1000)
                    time.sleep(50)
                    if GM.wait(Screen.LEVELUP4, 30):
                        clearedStage = 13
                        break
                    elif GM.check(Screen.OPERATIONFAILED):
                        GM.tap(Button.RETRY)
                        time.sleep(15)
                    else:
                        GM.tap(Button.PAUSE)
                        time.sleep(2)
                        GM.tap(Button.RESTART)
                        time.sleep(20)
                        GM.wait(Screen.OPERATION, 30)
            if GM.check(Screen.LEVELUP4):
                clearedStage = 13
                GM.tap(Button.TAP)
                time.sleep(5)
                GM.wait(Screen.OPERATION13CLEAR, 5)
            if GM.check(Screen.OPERATION13CLEAR):
                clearedStage = 13
                GM.tap(Button.TAP)
                time.sleep(5)
                GM.wait(Screen.OPERATION13POSTSTORY, 10)
            if GM.check(Screen.OPERATION13POSTSTORY):
                clearedStage = 13
                GM.tap(Button.SKIP)
                time.sleep(10)
                GM.wait(Screen.FIELD1, 30)
            if clearedStage == 13 and GM.check(Screen.FIELD1):
                time.sleep(0.5)
                GM.tap(160, 290) # 1-4
                time.sleep(2)
                GM.wait(Screen.OPERATION14ENTER, 5)
            if GM.check(Screen.OPERATION14ENTER):
                clearedStage = 13
                GM.tap(Button.OPERATIONENTER)
                time.sleep(5)
                GM.wait(Screen.OPERATION14PRESTORY)
            if GM.check(Screen.OPERATION14PRESTORY):
                clearedStage = 13
                GM.tap(Button.SKIP)
                time.sleep(20)
                GM.wait(Screen.OPERATION14TUTORIAL, 20)
            if GM.check(Screen.OPERATION14TUTORIAL):
                clearedStage = 13
                GM.tap(Button.SKIP)
                time.sleep(2)
                GM.wait(Screen.OPERATIONTUTORIALSKIPNOTICE, 5)
            if clearedStage == 13 and GM.check(Screen.OPERATIONTUTORIALSKIPNOTICE):
                GM.tap(Button.TUTORIALSKIPCONFIRM)
                time.sleep(80)
                GM.wait(Screen.OPERATION14CLEAR, 60)
            if GM.check(Screen.OPERATION14CLEAR):
                clearedStage = 14
                time.sleep(1)
                GM.tap(Button.TAP)
                time.sleep(10)
                for _ in range(10):
                    GM.tap(Button.SKIP)
                    if GM.wait(Screen.ANIMATIONSKIPNOTICE, 3):
                        time.sleep(2)
                        GM.tap(550, 410) # Skip Confirm
                        time.sleep(20)
                        GM.wait(Screen.CHAPTER1CLEAR, 20)
                        break
            if GM.check(Screen.CHAPTER1CLEAR):
                clearedStage = 14
                GM.tap(Button.TAP)
                time.sleep(10)
                GM.wait(Screen.LOBBYTUTORIAL1, 10)
            if GM.check(Screen.LOBBYTUTORIAL1):
                clearedStage = 14
                GM.tap(Button.SKIP)
                GM.wait(Screen.TUTORIALSKIPNOTICE, 10)
            if clearedStage == 14 and GM.check(Screen.TUTORIALSKIPNOTICE):
                GM.tap(Button.TUTORIALSKIPCONFIRM)
                GM.wait(Screen.LOBBYTUTORIAL2, 10)
            if GM.check(Screen.LOBBYTUTORIAL2):
                GM.tap(Button.SKIP)
                GM.wait(Screen.TUTORIALSKIPNOTICE, 10)
            if clearedStage == 14 and GM.check(Screen.TUTORIALSKIPNOTICE):
                GM.tap(Button.TUTORIALSKIPCONFIRM)
                GM.wait(Screen.LOBBYNOTICE, 10)
            if GM.check(Screen.LOBBYNOTICE):
                GM.tap(600, 50) # close notice
                GM.wait(Screen.LOBBY, 10)
            if clearedStage == 14 and not arkTutorial and GM.check(Screen.LOBBY):
                GM.tap(675, 367) # Ark
                time.sleep(2)
                GM.wait(Screen.ARKSTORY1, 10)
            if GM.check(Screen.ARKSTORY1):
                GM.tap(Button.SKIP)
                time.sleep(5)
                GM.wait(Screen.ARK, 10)
            if not simulationUnlock and not arkTutorial and GM.check(Screen.ARK):
                GM.tap(473, 234) # commander's office
                time.sleep(2)
                GM.wait(Screen.ARKSTORY2, 10)
            if GM.check(Screen.ARKSTORY2):
                GM.tap(Button.SKIP)
                time.sleep(5)
                GM.wait(Screen.ARKUNLOCK, 15)
            if GM.check(Screen.ARKUNLOCK):
                simulationUnlock = True
                time.sleep(5)
                GM.tap(Button.TAP)
                time.sleep(5)
                GM.wait(Screen.ARK, 10)
            if simulationUnlock and not arkTutorial and GM.check(Screen.ARK):
                time.sleep(5)
                GM.tap(389, 274)
                time.sleep(2)
                GM.wait(Screen.ARKSTORY3, 10)
            if GM.check(Screen.ARKSTORY3):
                simulationUnlock = True
                GM.tap(Button.SKIP)
                time.sleep(1)
                GM.wait(Screen.SIMULATIONTUTORIAL, 10)
            if GM.check(Screen.SIMULATIONTUTORIAL):
                simulationUnlock = True
                GM.tap(Button.SKIP)
                time.sleep(1)
                GM.wait(Screen.TUTORIALSKIPNOTICE, 5)
            if simulationUnlock and not arkTutorial and GM.check(Screen.TUTORIALSKIPNOTICE):
                GM.tap(Button.TUTORIALSKIPCONFIRM)
                arkTutorial = True
                time.sleep(3)
                GM.wait(Screen.SIMULATIONROOM, 5)
            if simulationUnlock and arkTutorial and not pulled and GM.check(Screen.SIMULATIONROOM, Screen.LOBBY):
                GM.tap(82, 511) # home
                time.sleep(2)
                GM.wait(Screen.ARKSTORY4, 10)
            if GM.check(Screen.ARKSTORY4):
                simulationUnlock = True
                arkTutorial = True
                GM.tap(Button.SKIP)
                GM.wait(Screen.LOBBY, 10)
            if clearedStage == 14 and arkTutorial and GM.check(Screen.LOBBY):
                GM.tap(675, 414) # operation
                time.sleep(5)
                GM.wait(Screen.FIELD2STORY, 10)
            if GM.check(Screen.FIELD2STORY):
                arkTutorial = True
                GM.tap(Button.SKIP)
                time.sleep(10)
                GM.wait(Screen.FIELD2, 30)
            if clearedStage == 14 and GM.check(Screen.FIELD2):
                clearedStage = 14
                arkTutorial = True
                time.sleep(10)
                GM.tap(646, 279)
                time.sleep(2)
                if not GM.wait(Screen.OPERATION21ENTER, 10):
                    # maybe already done; check if mailbox is activated
                    GM.tap(920, 20) # Mailbox
                    if GM.wait(Screen.MAILBOXFULL, Screen.MAILBOXEMPTY, 5) != None:
                        # mailbox is opened
                        clearedStage = 21
                        GM.tap(600, 70) # close mailbox
                        GM.wait(Screen.FIELD2, 5)
            if GM.check(Screen.OPERATION21ENTER):
                clearedStage = 14
                arkTutorial = True
                GM.tap(Button.OPERATIONENTER)
                time.sleep(5)
                GM.wait(Screen.OPERATION21PRESTORY)
            if GM.check(Screen.OPERATION21PRESTORY):
                clearedStage = 14
                arkTutorial = True
                GM.tap(Button.SKIP)
                time.sleep(10)
                GM.wait(Screen.OPERATION21TUTORIAL, 30)
            if GM.check(Screen.OPERATION21TUTORIAL):
                clearedStage = 14
                arkTutorial = True
                GM.tap(Button.SKIP)
                time.sleep(1)
                GM.wait(Screen.OPERATIONTUTORIALSKIPNOTICE, 5)
            if clearedStage == 14 and GM.check(Screen.OPERATIONTUTORIALSKIPNOTICE):
                GM.tap(Button.TUTORIALSKIPCONFIRM)
                time.sleep(2)
                GM.wait(Screen.OPERATION, 5)
            if clearedStage == 14 and GM.check(Screen.OPERATION):
                time.sleep(40)
                GM.wait(Screen.OPERATION21CLEAR, 40)
            if GM.check(Screen.OPERATION21CLEAR):
                clearedStage = 21
                time.sleep(1)
                GM.tap(Button.TAP)
                time.sleep(10)
                GM.wait(Screen.FIELD2, 10)
            if clearedStage == 21 and GM.check(Screen.FIELD2):
                GM.tap(82, 511) # home
                time.sleep(5)
                GM.wait(Screen.DAILYLOGIN, 10)
            if GM.check(Screen.DAILYLOGIN):
                GM.tap(600, 75)
                time.sleep(5)
                GM.wait(Screen.LOBBY, 10)
            if clearedStage == 21 and not mailReceived and GM.check(Screen.LOBBY):
                GM.tap(920, 20) # Mailbox
                time.sleep(1)
                if not GM.wait(Screen.MAILBOXFULL, 10):
                    GM.wait(Screen.MAILBOXEMPTY, 10)
            if GM.check(Screen.MAILBOXFULL):
                clearedStage = 21
                time.sleep(5)
                GM.tap(550, 450) # Receive All
                for _ in range(60):
                    if GM.check(Screen.RECEIVERESULT):
                        break
                    GM.tap(Button.SKIP)
                    time.sleep(0.5)
            if not mailReceived and GM.check(Screen.RECEIVERESULT):
                GM.tap(Button.RECEIVECONFIRM)
                mailReceived = True
                GM.wait(Screen.SECTORTUTORIAL, 10)
            if GM.check(Screen.SECTORTUTORIAL):
                mailReceived = True
                GM.tap(Button.SKIP)
                GM.wait(Screen.TUTORIALSKIPNOTICE, 5)
            if mailReceived and GM.check(Screen.TUTORIALSKIPNOTICE):
                GM.tap(Button.TUTORIALSKIPCONFIRM)
                GM.wait(Screen.REWARD2, Screen.REWARD3, Screen.REWARD4, 10)
            if GM.check(Screen.REWARD2, Screen.REWARD3, Screen.REWARD4):
                mailReceived = True
                GM.tap(Button.TAP)
                time.sleep(1)
                GM.wait(Screen.MAILBOXEMPTY, 10)
            if GM.check(Screen.MAILBOXEMPTY):
                mailReceived = True
                GM.tap(600, 70) # close mailbox
                time.sleep(5)
                GM.wait(Screen.LOBBY, 10)
            if mailReceived and not pulled and GM.check(Screen.LOBBY):
                GM.tap(590, 500) # pull
                time.sleep(5)
                GM.wait(Screen.PULLTUTORIAL, 20)
            if GM.check(Screen.PULLTUTORIAL):
                GM.tap(480, 440) # pull tutorial
                time.sleep(5)
                for _ in range(60):
                    if GM.check(Screen.RECEIVERESULT):
                        break
                    GM.tap(Button.SKIP)
                    time.sleep(0.5)
            if mailReceived and GM.check(Screen.RECEIVERESULT):
                GM.tap(Button.RECEIVECONFIRM)
                time.sleep(5)
                GM.wait(Screen.PULL, 10)
            if not pulled and GM.check(Screen.PULL):
                while not GM.check(Screen.PULLNORMAL) and GM.alive():
                    GM.tap(940, 270) # >>
                    time.sleep(5)
            if not pulled and GM.check(Screen.PULLNORMAL):
                GM.tap(Button.PULL10)
                res = GM.wait(Screen.JEWELUSENOTICE, Screen.JEWELLACKNOTICE, Screen.TICKETLACKNOTICE, 5)
                if res == Screen.JEWELLACKNOTICE:
                    GM.tap(Button.JEWELUSEDECLINE) 
                else:
                    if res == Screen.JEWELUSENOTICE or res == Screen.TICKETLACKNOTICE:
                        GM.tap(Button.JEWELUSECONFIRM)
                        time.sleep(5)
                    else:
                        # used ticket: no popup
                        pass
                    for i in range(10):
                        for _ in range(60):
                            if GM.check(Screen.PULLRESULT):
                                break
                            GM.tap(Button.SKIP)
                            time.sleep(0.5)
                        GM.tap(Button.PULLAGAIN)
                        res = GM.wait(Screen.JEWELLACKNOTICE, Screen.JEWELUSENOTICE, 3)
                        if res == Screen.JEWELUSENOTICE:
                            GM.tap(Button.JEWELUSECONFIRM)
                        elif res == Screen.JEWELLACKNOTICE:
                            GM.tap(Button.JEWELUSEDECLINE)
                            time.sleep(1)
                            GM.tap(Button.PULLCONFIRM)
                            time.sleep(1)
                            break
                pulled = True
                time.sleep(5)
                GM.wait(Screen.PULLNORMAL, 10)
            if pulled and not checked:
                GM.tap(370, 500) # Nikke
                time.sleep(5)
                GM.wait(Screen.NIKKE, 10)
            if pulled and not checked and GM.check(Screen.NIKKE):
                time.sleep(5)
                scr = GM.screen()
                if GM.analyze(scr) >= 3: # FOR DEBUG: should be changed
                    logging.info('new backup: {}'.format(mailaddr))
                    imgname = '{}_nikke.jpg'.format(accountID)
                    imgpath = os.path.join(serverpath, 'images', imgname)
                    scr.crop((40, 147, 40 + 880, 147 + 248)).convert('RGB').save(imgpath)
                    # Do something more for macro detection bypass
                    good = True
                    GM.tap(425, 500) # Squad
                    time.sleep(1)
                    GM.wait(Screen.SQUAD, 10)
                else:
                    backedup = True
                checked = True
            if checked and good and GM.check(Screen.LOBBY):
                if not squadset:
                    GM.tap(425, 500) # Squad
                    time.sleep(1)
                    GM.wait(Screen.SQUAD, 10)
                elif not profileset:
                    GM.tap(20, 20) # profile
                    time.sleep(1)
                    GM.wait(Screen.INFO, 10)
            if checked and good and not squadset and GM.check(Screen.SQUAD):
                time.sleep(5)
                GM.tap(578, 439) # auto set
                time.sleep(5)
                squadset = True
                imgname = '{}_squad.jpg'.format(accountID)
                imgpath = os.path.join(serverpath, 'images', imgname)
                scr = GM.screen()
                scr.crop((364, 139, 364+233, 139+279)).convert('RGB').save(imgpath)
                GM.tap(480, 500) # Lobby
                GM.wait(Screen.LOBBY, 10)
            if good and squadset and not profileset and GM.check(Screen.LOBBY):
                GM.tap(20, 20) # account info
                time.sleep(1)
                GM.wait(Screen.INFO, 10)
            if good and squadset and not profileset and GM.check(Screen.INFO):
                time.sleep(3)
                GM.tap(387, 144) # profile
                time.sleep(2)
                GM.wait(Screen.PROFILE, 10)
            if good and squadset and not profileset and GM.check(Screen.PROFILE):
                time.sleep(3)
                GM.tap(384, 313) # first image
                time.sleep(2)
                imgname = '{}_profile.jpg'.format(accountID)
                imgpath = os.path.join(serverpath, 'images', imgname)
                scr = GM.screen()
                scr.crop((400, 145, 400+160, 145+62)).convert('RGB').save(imgpath)
                HTMLpath = os.path.join(serverpath, 'table.html')
                with open(HTMLpath, 'at') as html:
                    html.write('<div class="accordion-item">\n')
                    html.write('    <h2 class="accordion-header" id="{}_button">\n'.format(accountID))
                    html.write('        <button class="accordion-button collapsed" data-bs-toggle="collapse" href="#{}_content" role="button" aria-expanded="false" aria-controls="{}_content">\n'.format(accountID, accountID))
                    html.write('            {}\n'.format(accountID))
                    html.write('        </button>\n')
                    html.write('    </h2>\n')
                    html.write('    <div id="{}_content" class="accordion-collapse collapse" aria-labelledby="{}_button" data-bs-parent="#accordion" style="text-align:center;">\n'.format(accountID, accountID))
                    html.write('        <img src="images/{}_nikke.jpg" loading="lazy" /><br>\n'.format(accountID))
                    html.write('        <img src="images/{}_profile.jpg" loading="lazy" /><br>\n'.format(accountID))
                    html.write('        <img src="images/{}_squad.jpg" loading="lazy" />\n'.format(accountID))
                    html.write('    </div>\n')
                    html.write('</div>\n')
                
                GM.tap(528, 503) # apply
                backedup = True
                profileset = True
                time.sleep(2)
                GM.wait(Screen.INFO, 10)
            if good and squadset and profileset and GM.check(Screen.INFO):
                time.sleep(2)
                GM.tap(603, 49) # close
                time.sleep(2)
                GM.wait(Screen.LOBBY, 10)
            if backedup and (not good or good and squadset and profileset) and GM.check(Screen.NIKKE, Screen.LOBBY, Screen.PULL):
                GM.tap(950, 17) # submenu
                time.sleep(2)
                GM.wait(Screen.SUBMENU, 10)
            if backedup and (not good or good and squadset and profileset) and GM.check(Screen.SUBMENU):
                GM.tap(426, 292) # account
                time.sleep(2)
                GM.wait(Screen.ACCOUNT1, 10)
            if backedup and (not good or good and squadset and profileset) and GM.check(Screen.ACCOUNT1):
                GM.swipe(0, -260, 1000)
                time.sleep(5)
                GM.wait(Screen.ACCOUNT2, 10)
            if backedup and (not good or good and squadset and profileset) and GM.check(Screen.ACCOUNT2):
                GM.tap(540, 353) # logout
                time.sleep(2)
                GM.wait(Screen.LOGOUTNOTICE, 10)
            if backedup and (not good or good and squadset and profileset) and GM.check(Screen.LOGOUTNOTICE):
                GM.tap(530, 340)
                return 0
        except Exception as e:
            logging.warn(e)
            # ADB Exception: app player is frozen
            GM.reboot()
            GM.boot()
            time.sleep(30)
            # now app player is clean, app will not be frozen for a while
            retrynum = 0