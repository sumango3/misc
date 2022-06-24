'''
    Install
        pip install pure-python-adb
    
'''
from multiprocessing import Process, Manager
from ppadb.client import Client as AdbClient
import os
from PIL import Image, ImageChops
import numpy as np
import io
import time
import sys

name = 'sumango' # Change to your wanted name (only alphabet)
accountFiles = [
        '/data/data/com.bilibilikr.arterygear/shared_prefs/bili_key.xml',
        '/data/data/com.bilibilikr.arterygear/shared_prefs/login.xml',
        '/data/data/com.bilibilikr.arterygear/shared_prefs/com.bilibilikr.arterygear.v2.playerprefs.xml',
        '/data/data/com.bilibilikr.arterygear/shared_prefs/device_info.xml',
        '/data/data/com.bilibilikr.arterygear/shared_prefs/cache_data.xml',
]
screenIndicators = {
        # L, U, W, H
        'ToS': (480, 130, 20, 20),
        'Login': (574, 200, 20, 20),
        'LoginConfirm': (574, 200, 20, 20),
        'AccountLink': (444, 448, 20, 20),
        'TapToStart': (30, 660, 20, 20),
        'Animation': (1198, 38, 7, 6),
        'AnimationSkipConfirm': (630, 210, 20, 20),
        'BattleTutorial': (90, 100, 20, 20),
        'Event': (1198, 31, 20, 20),
        'CommanderInfo': (563, 347, 20, 20),
        'CommanderInfoConfirm': (690, 70, 20, 20),
        'LoginAward': (271, 429, 20, 20),
        'Notice': (530, 190, 20, 20),
        'MainTutorial': (97, 113, 20, 20),
        'Lobby': (1175, 115, 20, 20),
        'MainStory': (415, 356, 20, 20),
        'Episode1': (34, 665, 20, 20),
        'Episode1-1': (1117, 133, 20, 20),
        'Formation': (368, 335, 20, 20),
        'BattleTutorial2': (98, 116, 20, 20),
        'CoreTutorial': (270, 210, 20, 20),
        'BattleFinish': (1020, 640, 20, 20),
        'BattleStatistics': (630, 600, 20, 20),
        'MailList': (1226, 655, 20, 20),
        'MailReceiveConfirm': (630, 237, 20, 20),
        'MailListReceived': (1226, 655, 20, 20),
        'Recruit1': (90, 105, 20, 20),
        'Recruit2': (45, 215, 20, 20),
        'RecruitConfirm': (478, 379, 20, 20),
        'RecruitDone': (600, 635, 20, 20),
        'RecruitOver': (600, 635, 20, 20),
        'Disconnect': (630, 250, 20, 20)
}
buttonCoordinates = {
        # X Y
        'AgreeAndStart': (532, 524),
        'GuestLogin': (640, 440),
        'LoginConfirmOK': (745, 515),
        'Tap': (640, 680),
        'AnimationSkip': (1180, 40),
        'AnimationSkipNeverAsk': (566, 577),
        'AnimationSkipConfirmOK': (770, 460),
        'Skill1': (1045, 630),
        'Skill3': (1215, 630),
        'Enemy1': (926, 458),
        'Enemy2': (811, 405),
        'NameInput': (443, 651),
        'NameInputOK': (1190, 670),
        'CommanderInfoOK': (840, 650),
        'CommanderInfoConfirmOK': (640, 640),
        'AccountLinkSkip': (733, 552),
        'NoticeNeverShow': (857, 78),
        'NoticeClose': (1120, 78),
        'SkipTutorial': (1184, 61),
        'LobbyMainStory': (1080, 140),
        'MainStoryEpisode1': (420, 400),
        'Episode1-1': (700, 380),
        'StartOperation': (1150, 670),
        'CoreTutorialSkip': (210, 220),
        'BattleStatisticsClose': (640, 710),
        'BattleFinishNext': (1160, 650),
        'Mail': (1140, 40),
        'ReceiveMail': (280, 670),
        'ReceiveMailConfirmOK': (760, 500),
        'Recruit': (940, 670),
        'RecruitBanner2': (100, 250),
        'Recruit10': (1160, 650),
        'RecruitConfirmOK': (770, 500),
        'RecruitAgain': (540, 650),
        'DisconnectOK': (640, 520)
}
screens = {}

def loadData():
    global screenIndicators
    global screens
    
    for subdir, dirs, files in os.walk('screen'):
        for file in files:
            screenName = file.split('.')[0]
            L, U, W, H = screenIndicators[screenName]
            screens[screenName] = Image.open(os.path.join(subdir, file)).convert('RGB').crop((L, U, L+W, U+H))
            if screenName == 'Event':
                screens[screenName] = screens[screenName].convert('L').point(lambda x:0 if x<128 else 255, '1')





def macro(device,accountFiles,screenIndicators,buttonCoordinates,screens):
    def stopGame():
        device.shell('am force-stop com.bilibilikr.arterygear')
    def startGame():
        device.shell('monkey -p com.bilibilikr.arterygear -c android.intent.category.LAUNCHER 1')
    def removeAccount():
        global accountFiles
        for accountFile in accountFiles:
            device.shell('rm {}'.format(accountFile))
    def checkScreen(screenName):
        global screenIndicators
        print('{} check {}'.format(device.serial, screenName))
        img = Image.open(io.BytesIO(device.screencap()))
        L, U, W, H = screenIndicators[screenName]
        deviceimg = img.convert('RGB').crop((L, U, L+W, U+H))
        findimg = screens[screenName]
        if screenName == 'Event':
            deviceimg = deviceimg.convert('L').point(lambda x:0 if x<128 else 255, '1')
        return deviceimg.tobytes() == findimg.tobytes()
        devicearr = np.frombuffer(deviceimg.tobytes(), dtype=np.unit8)
        findarr = np.frombuffer(findimg.tobytes(), dtype=np.uint8)
        result = np.average(np.abs(devicearr - findarr)) < 20
    def waitScreen(screenName, waitTime):
        global screenIndicators
        print('{} waiting {}'.format(device.serial, screenName))
        screenFound = checkScreen(screenName)
        while waitTime >= 0 and screenFound == False:
            time.sleep(1)
            waitTime -= 1
            screenFound = checkScreen(screenName)
        if not screenFound:
            print('{} could not find {}'.format(device.serial, screenName))
        return screenFound

    def tapScreen(buttonName):
        global buttonCoordinates
        print('{} tap {}'.format(device.serial, buttonName))
        device.shell('input tap {} {}'.format(*buttonCoordinates[buttonName]))
        time.sleep(0.1)

    def doubleTapScreen(buttonName):
        global buttonCoordinates
        device.shell('input tap {} {} & sleep 0.1; input tap {} {}'.format(*buttonCoordinates[buttonName],*buttonCoordinates[buttonName]))
        time.sleep(0.1)

    def inputText(text):
        device.shell('input text \'{}\''.format(text))
    def analyzeResult():
        img = Image.open(io.BytesIO(device.screencap()))
        result = []
        for U in [100, 471]:
            for L in [233, 408, 582, 756, 930]:
                R = L + 116
                D = U + 20
                area = img.crop((L,U,R,D))
                area.thumbnail((1,1))
                #print(area.getpixel((0,0)))
                R, G, B, A = area.getpixel((0,0))
                if R+G+B < 200:
                    # Gray
                    result.append(3)
                elif R<B and G<B:
                    # Purple
                    result.append(4)
                elif B<R and B<G:
                    # Yellow
                    result.append(5)
                else:
                    # Unknown
                    result.append(0)
        return result
    resetAccount = False
    tutorialDone = False
    mainDone = False
    mailDone = False
    stars = []
    imgs = []
    failnum = 0
    while True:
        if not resetAccount:
            stopGame()
            removeAccount()
            resetAccount = True
            startGame()
            waitScreen('ToS', 20)
        if checkScreen('ToS'):
            tapScreen('AgreeAndStart')
            waitScreen('Login', 20)
        if checkScreen('Login'):
            tapScreen('GuestLogin')
            waitScreen('LoginConfirm', 20)
        if checkScreen('LoginConfirm'):
            tapScreen('LoginConfirmOK')
            waitScreen('TapToStart', 20)
        if not tutorialDone and checkScreen('TapToStart'):
            tapScreen('Tap')
            while not checkScreen('BattleTutorial'):
                if checkScreen('Disconnect'):
                    tapScreen('DisconnectOK')
                tapScreen('AnimationSkip') # Sometimes The first battle tutorial is skipped by this
                doubleTapScreen('Skill1') # If the battle tutorial is skipped, double tap skill 1
        if not tutorialDone and checkScreen('BattleTutorial'):    
            tapScreen('Enemy1')
            waitScreen('BattleTutorial', 10)
        if not tutorialDone and checkScreen('BattleTutorial'):
            tapScreen('Skill3')
            tapScreen('Enemy2')
            while not checkScreen('AnimationSkipConfirm'):
                if checkScreen('Disconnect'):
                    tapScreen('DisconnectOK')
                tapScreen('AnimationSkip')
        if not tutorialDone and checkScreen('AnimationSkipConfirm'):
            tapScreen('AnimationSkipNeverAsk')
            tapScreen('AnimationSkipConfirmOK')
            while not checkScreen('Event'):
                if checkScreen('Disconnect'):
                    tapScreen('DisconnectOK')
                doubleTapScreen('Skill1')
        if not tutorialDone and checkScreen('Event'):
            tapScreen('AnimationSkip')
            waitScreen('CommanderInfo', 20)
        if not tutorialDone and checkScreen('CommanderInfo'):
            tapScreen('NameInput')
            inputText(name)
            tapScreen('NameInputOK')
            tapScreen('CommanderInfoOK')
            waitScreen('CommanderInfoConfirm', 20)
        if not tutorialDone and checkScreen('CommanderInfoConfirm'):
            tapScreen('CommanderInfoConfirmOK')
            tutorialDone = True
            waitScreen('LoginAward', 20)
            stopGame()
            startGame()
            waitScreen('AccountLink', 20)
        if checkScreen('AccountLink'):
            tapScreen('AccountLinkSkip')
            waitScreen('TapToStart', 20)
        if tutorialDone and checkScreen('TapToStart'):
            tapScreen('Tap')
            waitScreen('Notice', 20)
        if checkScreen('Notice'):
            tapScreen('NoticeNeverShow')
            tapScreen('NoticeClose')
            waitScreen('MainTutorial', 20)
        while checkScreen('MainTutorial'):
            tapScreen('SkipTutorial')
            if checkScreen('Disconnect'):
                tapScreen('DisconnectOK')
        if not mainDone and checkScreen('Lobby'):
            tapScreen('LobbyMainStory')
            waitScreen('MainStory', 20)
        if not mainDone and checkScreen('MainStory'):
            tapScreen('MainStoryEpisode1')
            waitScreen('Episode1', 20)
        if not mainDone and checkScreen('Episode1'):
            tapScreen('Episode1-1')
            waitScreen('Episode1-1', 20)
        if not mainDone and checkScreen('Episode1-1'):
            tapScreen('StartOperation')
            waitScreen('Formation', 20)
        if not mainDone and checkScreen('Formation'):
            tapScreen('StartOperation')
            waitScreen('Event', 20)
        if not mainDone and checkScreen('Event'):
            tapScreen('AnimationSkip')
            while not checkScreen('CoreTutorial'):
                if checkScreen('Disconnect'):
                    tapScreen('DisconnectOK')
                doubleTapScreen('Skill1')
        if not mainDone and checkScreen('CoreTutorial'):
            tapScreen('CoreTutorialSkip')
            while not checkScreen('BattleFinish') and not checkScreen('BattleStatistics'):
                if checkScreen('Disconnect'):
                    tapScreen('DisconnectOK')
                doubleTapScreen('Skill1')
        if not mainDone and (checkScreen('BattleStatistics') or checkScreen('BattleFinish')):
            mainDone = True
            stopGame()
            startGame()
            waitScreen('TapToStart', 20)
        if mainDone and not mailDone and checkScreen('TapToStart'):
            tapScreen('Tap')
            waitScreen('Lobby', 20)
        if mainDone and not mailDone and checkScreen('Lobby'):
            tapScreen('Mail')
            waitScreen('MailList', 20)
        if mainDone and not mailDone and checkScreen('MailList'):
            tapScreen('ReceiveMail')
            if not waitScreen('MailReceiveConfirm', 10):
                mailDone = True
        if mainDone and not mailDone and checkScreen('MailReceiveConfirm'):
            tapScreen('ReceiveMailConfirmOK')
            mailDone = True
            time.sleep(3)
            stopGame()
            startGame()
            waitScreen('TapToStart', 20)
        if mailDone and checkScreen('TapToStart'):
            tapScreen('Tap')
            waitScreen('Lobby', 20)
        if mailDone and checkScreen('Lobby'):
            tapScreen('Recruit')
            waitScreen('Recruit1', 20)
        if mailDone and checkScreen('Recruit1'):
            tapScreen('RecruitBanner2')
            waitScreen('Recruit2', 20)
        if mailDone and checkScreen('Recruit2'):
            while not checkScreen('RecruitConfirm'):
                tapScreen('Recruit10')
        if mailDone and checkScreen('RecruitConfirm'):
            tapScreen('RecruitConfirmOK')
            while not checkScreen('RecruitDone') and not checkScreen('RecruitOver'):
                if checkScreen('Disconnect'):
                    tapScreen('DisconnectOK')
                tapScreen('AnimationSkip')
        if mailDone and checkScreen('RecruitDone'):
            stars = stars + analyzeResult()
            imgs.append(Image.open(io.BytesIO(device.screencap())))
            tapScreen('RecruitAgain')
            waitScreen('RecruitConfirm', 20)
        if mailDone and checkScreen('RecruitConfirm'):
            tapScreen('RecruitConfirmOK')
            while not checkScreen('RecruitDone') and not checkScreen('RecruitOver'):
                if checkScreen('Disconnect'):
                    tapScreen('DisconnectOK')
                tapScreen('AnimationSkip')
        if mailDone and checkScreen('RecruitOver'):
            stars = stars + analyzeResult()
            imgs.append(Image.open(io.BytesIO(device.screencap())))
            return {'stars': stars, 'imgs': imgs}
        if checkScreen('Disconnect'):
            tapScreen('DisconnectOK')
        failnum += 1
        if failnum > 2:
            failnum = 0
            stopGame()
            startGame()
            while not checkScreen('Login') and not checkScreen('AccountLink') and not checkScreen('TapToStart'):
                time.sleep(1)
                
def work(device):

    loadData()
    
    def backup(savepath):
        savepath = os.path.join(savepath, 'shared_prefs')
        os.makedirs(savepath, exist_ok=True)
        for accountFile in accountFiles:
            device.pull(accountFile, os.path.join(savepath, accountFile.rsplit('/',1)[1]))
    
    result = []
    while True:
        result = macro(device,accountFiles,screenIndicators,buttonCoordinates,screens)
        print('{} {}'.format(device.serial, result['stars']))
        if result['stars'].count(5) >= 2:
            #backup account files
            savepath = 'backup'
            os.makedirs(savepath, exist_ok=True)
            backupnum = len(os.listdir(savepath))
            while os.path.exists(os.path.join(savepath, str(backupnum))):
                backupnum += 1
            savepath = os.path.join(savepath, str(backupnum))
            os.makedirs(savepath, exist_ok=True)
            backup(savepath)
            for i in range(len(result['imgs'])):
                result['imgs'][i].save(os.path.join(savepath, 'screen{}.png'.format(i)))
            print('New Backup at {}'.format(savepath))
            

workers = []
manager = None

if __name__ == '__main__':
    manager = Manager()
    client = AdbClient(host='127.0.0.1', port=5037)

    print('H(Help) D(Show Devices) W(Show Workers) R(Restore Account) I(Initialize worker) M(Macro) K(Kill Worker) Q(Quit) ')
    
    while True:
        cmd = input().lower()
        cmds = cmd.strip().split()
        if cmds[0] == 'h':
            print('help me')
        elif cmds[0] == 'd':
            for device in client.devices():
                print('{}'.format(device.serial))
        elif cmds[0] == 'w':
            for worker in workers:
                print('{} [{}]'.format(worker['device'].serial,('WORKING' if worker['process'].is_alive() else 'KILLED')))
        elif cmds[0] == 'r':
            if len(cmds) < 3:
                print('Usage: R <device serial(127.0.0.1:xxxx)> <backup number>')
                continue
            backupPath = os.path.join('backup', cmds[2])
            if not os.path.exists(backupPath):
                print('Invalid Backup number')
                continue
            foundDevice = False
            for worker in workers:
                if worker['device'].serial == cmds[1]:
                    foundDevice = True
                    worker['process'].terminate()
                    worker['device'].shell('am force-stop com.bilibilikr.arterygear')
                    for accountFile in accountFiles:
                        worker['device'].push(os.path.join(backupPath, 'shared_prefs', accountFile.rsplit('/',1)[1]), accountFile)
                    worker['device'].shell('monkey -p com.bilibilikr.arterygear -c android.intent.category.LAUNCHER 1')
                    print('Successfully restored')
                    break
            if foundDevice == False:
                for device in client.devices():
                    if device.serial == cmds[1]:
                        foundDevice = True
                        device.shell('am force-stop com.bilibilikr.arterygear')
                        for accountFile in accountFiles:
                            device.push(os.path.join(backupPath, 'shared_prefs', accountFile.rsplit('/',1)[1]), accountFile)
                        device.shell('monkey -p com.bilibilikr.arterygear -c android.intent.category.LAUNCHER 1')
                        print('Successfully restored')
                        break
            if foundDevice == False:
                print('device not found')
        elif cmd[0] == 'i':
            if len(cmds) < 2:
                print('Usage: I <device serial(127.0.0.1:xxxx)>')
                continue
            foundDevice = False
            for worker in workers:
                if worker['device'].serial == cmds[1]:
                    foundDevice = True
                    worker['process'].terminate()
                    process = Process(target=work, args=(device,))
                    process.start()                   
                    worker['process'] = process
        elif cmds[0] == 'k':
            if len(cmds) < 2:
                print('Usage: K <device serail(127.0.0.1:xxxx)> or K all')
                continue
            if cmds[1] == 'all':
                for worker in workers:
                    worker['process'].terminate()
            else:
                foundDevice = False
                for worker in workers:
                    if worker['device'].serial == cmds[1]:
                        foundDevice = True
                        worker['process'].terminate()
        elif cmds[0] == 'm':
            if len(cmds) < 2:
                print('Usage: M <device serial> or M all')
                continue
            if cmds[1] == 'all':
                serials = set()
                for worker in workers:
                    serials.add(worker['device'].serial)
                for device in client.devices():
                    if device.serial not in serials:
                        worker = {
                            'device': device,
                            'process': Process(target=work, args=(device,))
                        }
                        workers.append(worker)
                        worker['process'].start()
            else:
                foundDevice = False
                serials = set()
                for worker in workers:
                    serials.add(worker['device'].serial)
                if cmds[1] in serials:
                    print('Already working device')
                    continue
                for device in client.devices():
                    if device.serial == cmds[1]:
                        foundDevice = True
                        worker = {
                            'device': device,
                            'process': Process(target=work, args=(device,))
                        }
                        workers.append(worker)
                        worker['process'].start()
                        break
                if foundDevice:
                    print('Device added')
                else:
                    print('Device not found')
        elif cmds[0] == 'q':
            for worker in workers:
                worker['process'].terminate()
            sys.exit(0)

