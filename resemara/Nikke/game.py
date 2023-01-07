
import os
from enum import Enum, auto
import logging
import time
from collections import deque
import random

from PIL import Image
import numpy as np


# adb.py
from console import Console

# config.py
from config import screenpath


class Screen(Enum):
    NOTICE = auto()
    SELECTSERVER = auto()
    SIGNIN = auto()
    SIGNUP = auto()
    TEXTINPUT = auto()
    AUTHCODESENT = auto()
    TOUCHTOCONTINUE = auto()
    OPERATION01PRESTORY = auto()
    OPERATION = auto()
    PAUSE = auto()
    OPERATION01TUTORIAL1 = auto()
    OPERATION01TUTORIAL2 = auto()
    OPERATIONTUTORIALSKIPNOTICE = auto()
    OPERATIONFAILED = auto()
    LEVELUP2 = auto()
    OPERATION01CLEAR = auto()
    OPERATION01POSTSTORY = auto()
    FIELD0 = auto()
    FIELD0TUTORIAL1 = auto()
    FIELD0TUTORIAL2 = auto()
    OPERATION02ENTER = auto()
    OPERATION02PRESTORY = auto()
    OPERATION02TUTORIAL = auto()
    OPERATION02CLEAR = auto()
    OPERATION03ENTERDARK = auto()
    OPERATION03ENTER = auto()
    OPERATION03PRESTORY = auto()
    OPERATION03TUTORIAL1 = auto()
    OPERATION03TUTORIAL2 = auto()
    LEVELUP3 = auto()
    OPERATION03CLEAR = auto()
    OPERATION03POSTSTORY = auto()
    NAMEINPUT = auto()
    STORY = auto()
    CHAPTER0CLEAR = auto()
    FIELD1TUTORIAL1 = auto()
    TUTORIALSKIPNOTICE = auto()
    FIELD1 = auto()
    OPERATION11ENTER = auto()
    OPERATION11PRESTORY = auto()
    OPERATION11TUTORIAL = auto()
    OPERATION11CLEAR = auto()
    OPERATION11POSTSTORY = auto()
    FIELD1TUTORIAL2 = auto()
    OPERATION12ENTER = auto()
    OPERATION12PRESTORY = auto()
    OPERATION12TUTORIAL = auto()
    OPERATION12CLEAR = auto()
    OPERATION13ENTER = auto()
    OPERATION13PRESTORY = auto()
    OPERATION13TUTORIAL = auto()
    LEVELUP4 = auto()
    OPERATION13CLEAR = auto()
    OPERATION13POSTSTORY = auto()
    OPERATION14ENTER = auto()
    OPERATION14PRESTORY = auto()
    OPERATION14TUTORIAL = auto()
    OPERATION14CLEAR = auto()
    ANIMATIONSKIPNOTICE = auto()
    CHAPTER1CLEAR = auto()
    LOBBYTUTORIAL1 = auto()
    LOBBYTUTORIAL2 = auto()
    LOBBYNOTICE = auto()
    DAILYLOGIN = auto()
    LOBBY = auto()
    ARKSTORY1 = auto()
    ARK = auto()
    ARKSTORY2 = auto()
    ARKUNLOCK = auto()
    ARKSTORY3 = auto()
    SIMULATIONTUTORIAL = auto()
    SIMULATIONROOM = auto()
    ARKSTORY4 = auto()
    FIELD2STORY = auto()
    FIELD2 = auto()
    OPERATION21ENTER = auto()
    OPERATION21PRESTORY = auto()
    OPERATION21TUTORIAL = auto()
    OPERATION21CLEAR = auto()
    MAILBOXFULL = auto()
    RECEIVERESULT = auto()
    SECTORTUTORIAL = auto()
    REWARD2 = auto()
    REWARD3 = auto()
    REWARD4 = auto()
    MAILBOXEMPTY = auto()
    PULLTUTORIAL = auto()
    PULL = auto()
    JEWELUSENOTICE = auto()
    TICKETLACKNOTICE = auto()
    PULLRESULT = auto()
    JEWELLACKNOTICE = auto()
    PULLNORMAL = auto()
    NIKKE = auto()
    SQUAD = auto()
    INFO = auto()
    PROFILE = auto()
    SUBMENU = auto()
    ACCOUNT1 = auto()
    ACCOUNT2 = auto()
    LOGOUTNOTICE = auto()

LEVELAREA = (446, 218, 68, 44)
SCRIPTAREA = (271, 439, 38, 42)
FIELDAREA = (872, 497, 24, 17)
OPERATIONCLEARAREA = (352, 341, 86, 28)
OPERATIONENTERAREA = (342, 304, 55, 20)
CHAPTERAREA = (391, 137, 42, 12)
MAILBOXAREA = (512, 449, 66, 17)
screenIndicators = {
    # L, U, W, H
    Screen.NOTICE: (350, 109, 260, 18),
    Screen.SELECTSERVER: (376, 200, 38, 17),
    Screen.SIGNIN: (427, 88, 107, 23),
    Screen.SIGNUP: (459, 129, 42, 14),
    Screen.TEXTINPUT: (859, 478, 38, 22),
    Screen.AUTHCODESENT: (463, 195, 36, 13),
    Screen.TOUCHTOCONTINUE: (2, 6, 40, 195),
    Screen.OPERATION01PRESTORY: SCRIPTAREA,
    Screen.OPERATION: (939, 11, 14, 14),
    Screen.PAUSE: (462, 39, 35, 11),
    Screen.OPERATION01TUTORIAL1: (396, 69, 153, 55),
    Screen.OPERATION01TUTORIAL2: (397, 70, 77, 28),
    Screen.OPERATIONTUTORIALSKIPNOTICE: (400, 232, 159, 22),
    Screen.LEVELUP2: LEVELAREA,
    Screen.OPERATIONFAILED: (838, 484, 118, 33),
    Screen.OPERATION01CLEAR: OPERATIONCLEARAREA,
    Screen.OPERATION01POSTSTORY: SCRIPTAREA,
    Screen.FIELD0: FIELDAREA,
    Screen.FIELD0TUTORIAL1: (396, 52, 36, 12),
    Screen.FIELD0TUTORIAL2: (396, 52, 36, 12),
    Screen.OPERATION02ENTER: OPERATIONENTERAREA,
    Screen.OPERATION02PRESTORY: SCRIPTAREA,
    Screen.OPERATION02TUTORIAL: (396, 354, 43, 12),
    Screen.OPERATION02CLEAR: OPERATIONCLEARAREA,
    Screen.OPERATION03ENTERDARK: OPERATIONENTERAREA,
    Screen.OPERATION03ENTER: OPERATIONENTERAREA,
    Screen.OPERATION03PRESTORY: SCRIPTAREA,
    Screen.OPERATION03TUTORIAL1: (396, 355, 53, 10),
    Screen.OPERATION03TUTORIAL2: (396, 70, 76, 11),
    Screen.LEVELUP3: LEVELAREA,
    Screen.OPERATION03CLEAR: OPERATIONCLEARAREA,
    Screen.OPERATION03POSTSTORY: SCRIPTAREA,
    Screen.NAMEINPUT: (438, 197, 83, 20),
    Screen.STORY: (807, 8, 134, 12),
    Screen.CHAPTER0CLEAR: CHAPTERAREA,
    Screen.FIELD1TUTORIAL1: (396, 377, 17, 11),
    Screen.TUTORIALSKIPNOTICE: (414, 238, 131, 9),
    Screen.FIELD1: FIELDAREA,
    Screen.OPERATION11ENTER: OPERATIONENTERAREA,
    Screen.OPERATION11PRESTORY: SCRIPTAREA,
    Screen.OPERATION11TUTORIAL: (396, 71, 30, 9),
    Screen.OPERATION11CLEAR: OPERATIONCLEARAREA,
    Screen.OPERATION11POSTSTORY: SCRIPTAREA,
    Screen.FIELD1TUTORIAL2: (397, 377, 25, 11),
    Screen.OPERATION12ENTER: OPERATIONENTERAREA,
    Screen.OPERATION12PRESTORY: SCRIPTAREA,
    Screen.OPERATION12TUTORIAL: (396, 354, 17, 11),
    Screen.OPERATION12CLEAR: OPERATIONCLEARAREA,
    Screen.OPERATION13ENTER: OPERATIONENTERAREA,
    Screen.OPERATION13PRESTORY: SCRIPTAREA,
    Screen.OPERATION13TUTORIAL: (397, 368, 16, 10),
    Screen.LEVELUP4: LEVELAREA,
    Screen.OPERATION13CLEAR: OPERATIONCLEARAREA,
    Screen.OPERATION13POSTSTORY: SCRIPTAREA,
    Screen.OPERATION14ENTER: OPERATIONENTERAREA,
    Screen.OPERATION14PRESTORY: SCRIPTAREA,
    Screen.OPERATION14TUTORIAL: (396, 342, 35, 10),
    Screen.OPERATION14CLEAR: OPERATIONCLEARAREA,
    Screen.ANIMATIONSKIPNOTICE: (396, 2565, 167, 16),
    Screen.CHAPTER1CLEAR: CHAPTERAREA,
    Screen.LOBBYTUTORIAL1: (396, 53, 35, 10),
    Screen.LOBBYTUTORIAL2: (396, 53, 18, 10),
    Screen.LOBBYNOTICE: (453, 48, 57, 17),
    Screen.DAILYLOGIN: (513, 237, 84, 22),
    Screen.LOBBY: (914, 110, 39, 41),
    Screen.ARKSTORY1: SCRIPTAREA,
    Screen.ARK: (914, 72, 39, 40),
    Screen.ARKSTORY2: SCRIPTAREA,
    Screen.ARKUNLOCK: (457, 214, 50, 72),
    Screen.ARKSTORY3: SCRIPTAREA,
    Screen.SIMULATIONTUTORIAL: (397, 144, 51, 11),
    Screen.SIMULATIONROOM: (438, 253, 87, 38),
    Screen.ARKSTORY4: SCRIPTAREA,
    Screen.FIELD2STORY: SCRIPTAREA,
    Screen.FIELD2: FIELDAREA,
    Screen.OPERATION21ENTER: OPERATIONENTERAREA,
    Screen.OPERATION21PRESTORY: SCRIPTAREA,
    Screen.OPERATION21TUTORIAL: (396, 137, 35, 10),
    Screen.OPERATION21CLEAR: OPERATIONCLEARAREA,
    Screen.MAILBOXFULL: MAILBOXAREA,
    Screen.RECEIVERESULT: (464, 480, 32, 16),
    Screen.SECTORTUTORIAL: (396, 376, 43, 12),
    Screen.REWARD2: (453, 146, 53, 20),
    Screen.REWARD3: (453, 121, 53, 20),
    Screen.REWARD4: (453, 95, 53, 20),
    Screen.MAILBOXEMPTY: MAILBOXAREA,
    Screen.PULLTUTORIAL: (432, 439, 42, 11),
    Screen.PULL: (563, 473, 47, 39),
    Screen.PULLNORMAL: (500, 439, 41, 11),
    Screen.JEWELUSENOTICE: (395, 219, 169, 11),
    Screen.JEWELLACKNOTICE: (450, 232, 59, 9),
    Screen.TICKETLACKNOTICE: (392, 221, 174, 21),
    Screen.PULLRESULT: (525, 480, 33, 14),
    Screen.NIKKE: (340, 96, 172, 27),
    Screen.SQUAD: (404, 476, 45, 37),
    Screen.INFO: (386, 489, 54, 17),
    Screen.PROFILE: (457, 57, 46, 9),
    Screen.SUBMENU: (439, 191, 85, 12),
    Screen.ACCOUNT1: (462, 59, 39, 14),
    Screen.ACCOUNT2: (362, 349, 36, 12),
    Screen.LOGOUTNOTICE: (433, 237, 92, 11)
}  

# by default, search for white text
# for images in here, search for dark text (or small text) at black background
DARKTEXT = set([
    Screen.OPERATION01PRESTORY,
    Screen.OPERATION,
    Screen.OPERATION01TUTORIAL1,
    Screen.OPERATION01TUTORIAL2,
    Screen.LEVELUP2,
    Screen.OPERATION01POSTSTORY,
    Screen.OPERATION02PRESTORY,
    Screen.OPERATION02TUTORIAL,
    Screen.OPERATION03ENTERDARK,
    Screen.OPERATION03PRESTORY,
    Screen.OPERATION03TUTORIAL1,
    Screen.OPERATION03TUTORIAL2,
    Screen.LEVELUP3,
    Screen.OPERATION03POSTSTORY,
    Screen.OPERATION11PRESTORY,
    Screen.OPERATION11TUTORIAL,
    Screen.OPERATION11POSTSTORY,
    Screen.OPERATION12PRESTORY,
    Screen.OPERATION12TUTORIAL,
    Screen.OPERATION13PRESTORY,
    Screen.OPERATION13TUTORIAL,
    Screen.LEVELUP4,
    Screen.OPERATION13POSTSTORY,
    Screen.OPERATION14PRESTORY,
    Screen.OPERATION14TUTORIAL,
    Screen.ARKSTORY1,
    Screen.ARKSTORY2,
    Screen.ARKSTORY3,
    Screen.SIMULATIONTUTORIAL,
    Screen.ARKSTORY4,
    Screen.FIELD2STORY,
    Screen.OPERATION21PRESTORY,
    Screen.SECTORTUTORIAL,
])

class Button(Enum):
    TEXTCONFIRM = auto()
    TAP = auto()
    SKIP = auto()
    TUTORIALSKIPCONFIRM = auto()
    RETRY = auto()
    PAUSE = auto()
    RESTART = auto()
    CONTINUE = auto()
    OPERATIONENTER = auto()
    RECEIVECONFIRM = auto()
    PULL10 = auto()
    JEWELUSECONFIRM = auto()
    JEWELUSEDECLINE = auto()
    PULLAGAIN = auto()
    PULLCONFIRM = auto()

buttonCoordinates = {
    # X Y
    Button.TEXTCONFIRM: (878, 489),
    Button.TAP: (480, 480),
    Button.SKIP: (920, 10),
    Button.TUTORIALSKIPCONFIRM: (530, 340),
    Button.RETRY: (915, 500),
    Button.PAUSE: (945, 16),
    Button.RESTART: (480, 500),
    Button.CONTINUE: (603, 41),
    Button.OPERATIONENTER: (560, 500),
    Button.RECEIVECONFIRM: (480, 485),
    Button.PULL10: (550, 440),
    Button.JEWELUSECONFIRM: (530, 340),
    Button.JEWELUSEDECLINE: (420, 340),
    Button.PULLAGAIN: (540, 488),
    Button.PULLCONFIRM: (420, 488)
}

class GameManager():
    def __init__(self, deviceidx):
        self.deviceidx = deviceidx
        self.console = Console()
        self.record = deque()
        self.screenflags = {}
        for f in os.listdir(screenpath):
            fname = os.path.splitext(f)[0]
            scr = Screen[fname]
            L, U, W, H = screenIndicators[scr]
            self.screenflags[scr] = Image.open(os.path.join(screenpath, f)).convert('RGB').crop((L, U, L+W, U+H))
    def boot(self):
        return self.console.boot(self.deviceidx)
    def reboot(self):
        return self.console.reboot(self.deviceidx)
    def cmd(self, *cmds):
        return self.console.cmd(self.deviceidx, *cmds)
    def shraw(self, shcmd):
        return self.console.shraw(self.deviceidx, shcmd)
    def sh(self, shcmd):
        return self.console.sh(self.deviceidx, shcmd)
    def su(self, shcmd):
        return self.console.su(self.deviceidx, shcmd)
    def pull(self, target, location):
        return self.console.pull(self.deviceidx, target, location)
    def screen(self):
        return self.console.screen(self.deviceidx)
    def tap(self, *args):
        x = None
        y = None
        try:
            if len(args) == 1:
                    x, y = buttonCoordinates[args[0]]
            elif len(args) == 2 and type(args[0]) == type(args[1]) == int:
                x, y = args[0], args[1]
        except:
            raise Exception('invalid tap argument: {}'.format(args))
        dx = random.randint(-3, 4)
        dy = random.randint(-3, 4)
        return self.console.swipe(self.deviceidx, x+dx, y+dy, x+dx, y+dy, 100)
    def tap2(self, *args):
        x = None
        y = None
        try:
            if len(args) == 1 and type(args[0]) == Button:
                x, y = buttonCoordinates[args[0]]
            elif len(args) == 2 and type(args[0]) == type(args[1]) == int:
                x, y = args[0], args[1]
        except:
            raise Exception('invalid tap2 argument: {}'.format(args))
        dx = random.randint(-3, 4)
        dy = random.randint(-3, 4)
        return self.console.tap2(self.deviceidx, x+dx, y+dy)
    def swipe(self, *args):
        x1, y1, x2, y2, t = None, None, None, None, None
        if len(args) == 5:
            # input: x1 y1 x2 y2 tadb
            x1, y1, x2, y2, t = args[0], args[1], args[2], args[3], args[4]
        elif len(args) == 3:
            # input: dx dy t
            x1, y1, x2, y2, t = 480, 270, 480+args[0], 270+args[1], args[2]
        dx = random.randint(-3, 4)
        dy = random.randint(-3, 4)
        return self.console.swipe(self.deviceidx, x1+dx, y1+dy, x2+dx, y2+dy, t)
    def text(self, txt):
        res = self.console.text(self.deviceidx, txt)
        time.sleep(0.5)
        return res
    def backspace(self):
        return self.console.backspace(self.deviceidx)
    def back(self):
        return self.console.back(self.deviceidx)
    def paste(self):
        return self.console.paste(self.deviceidx)
    def launch(self):
        logging.info('launch app')
        #print('launch app')
        return self.console.launch(self.deviceidx)
    def kill(self):
        logging.info('kill app')
        #print('kill app')
        return self.console.kill(self.deviceidx)
    def alive(self):
        return self.console.alive(self.deviceidx)
    def screen(self):
        return self.console.screen(self.deviceidx)
    def check(self, *screenNames):
        logging.debug('check {}'.format(screenNames))
        # if screen found in last 2 seconds, return
        while len(self.record) > 0:
            checkTime, screenName = self.record[0]
            if checkTime + 2 < time.time():
                self.record.popleft()
            else:
                break
        for checkTime, screenName in self.record:
            if screenName in screenNames:
                return screenName
        
        img = self.console.screen(self.deviceidx)
        for screenName in screenNames:
            res = None
            L, U, W, H = screenIndicators[screenName]
            #if screenName in RGB:
            pivot = 50 if screenName in DARKTEXT else 160
            deviceimg = img.convert('L').crop((L, U, L+W, U+H))
            findimg = self.screenflags[screenName].convert('L')
            
            devicearr = np.asarray(deviceimg).copy()
            findarr = np.asarray(findimg).copy()
            devicearr[devicearr<=pivot] = 0
            devicearr[devicearr>pivot] = 255
            findarr[findarr<=pivot] = 0
            findarr[findarr>pivot] = 255
            deviceimg = Image.fromarray(devicearr)
            findimg = Image.fromarray(findarr)
            #deviceimg.save(os.path.join(os.path.dirname(__file__), 'check', '{}_device.png'.format(screenName)))
            #findimg.save(os.path.join(os.path.dirname(__file__), 'check', '{}_find.png'.format(screenName)))
            res = np.count_nonzero(devicearr - findarr) < W*H/40
            if res:
                logging.info('found {}'.format(screenName))
                self.record.append((time.time(), screenName))
                return screenName
        return None
    def wait(self, *args):
        waitTime = 5
        screenNames = None
        if type(args[-1]) == int:
            waitTime = args[-1]
            screenNames = args[:-1]
        else:
            screenNames = args
        logging.debug('wait {}'.format(screenNames))
        res = self.check(*screenNames)
        if res != None:
            return res
        if not self.console.alive(self.deviceidx):
            return None
        for _ in range(waitTime):
            time.sleep(1)
            res = self.check(*screenNames)
            if res != None:
                return res
        logging.warn('cound not find {}'.format(screenNames))
        return None
    def analyze(self, img):
        img = img.convert('RGB')
        W = 58
        H = 1
        SSR = 0
        SR = 0
        R = 0
        Error = 0
        for U in (266, 393):
            for L in range(41, 41 + 75 * 12, 75):
                area = img.crop((L, U, L+W, U+H))
                area.thumbnail((1,1))
                R,G,B = area.getpixel((0,0))
                if R > 200 and G > 200 and B < 100:
                    SSR += 1
                elif R > 200 and G < 100 and B > 200:
                    SR += 1
                elif R < 100 and G > 200 and B > 200:
                    R += 1
                elif R > 200 and G > 200 and B > 200:
                    pass
                else:
                    Error += 1
        #if Error > 0:
        #    img.save(os.path.join(analyzelogpath, str(time.time())+'.png')) 
        
        # mark parse error as SSR
        return SSR + Error