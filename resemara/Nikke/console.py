
import time
from io import BytesIO
from subprocess import check_output, STDOUT, CalledProcessError
import os
from PIL import Image
import logging

# config.py
from config import LDPlayerPath, packagename

adbpath = os.path.join(LDPlayerPath, 'adb.exe')
consolepath = os.path.join(LDPlayerPath, 'dnconsole.exe')


class Console:
    def devices(self):
        res = []
        output = ''
        bin = check_output([consolepath, 'list2'], shell=True)
        try:
            output = bin.decode('euc-kr')
        except:
            try:
                output = bin.decode('cp949')
            except:
                try:
                    output = bin.decode('utf-8')
                except:
                    try:
                        output = bin.decode('utf-16-le')
                    except:
                        try:
                            output = bin.decode('utf-16-be')
                        except:
                            raise Exception('decode failed')
        for line in output.splitlines():
            index, name, _, _, booted, pid, vboxpid, width, height, dpi = line.strip().split(',')
            index = int(index)
            booted = bool(int(booted))
            if index < 10000:
                res.append({
                    'index': index,
                    'name': name,
                    'boot': booted,
                    'width': width,
                    'height': height,
                    'dpi': dpi
                })
        return res
    def boot(self, device):
        if type(device) == int:
            return check_output([consolepath, 'launch', '--index', str(device)], shell=True)
        else:
            return check_output([consolepath, 'launch', '--name', device], shell=True)
    def reboot(self, device):
        if type(device) == int:
            return check_output([consolepath, 'reboot', '--index', str(device)], shell=True)
        else:
            return check_output([consolepath, 'reboot', '--name', device], shell=True)
    def _cmd(self, device, *cmds):
        if type(device) == int:
            deviceaddr = '127.0.0.1:{}'.format(5555 + device * 2)
            return check_output([adbpath, '-s', deviceaddr, *cmds], shell=True, stderr=STDOUT)
            #return check_output([consolepath, 'adb', '--index', str(device), '--command', ' '.join(cmds)], shell=True, stderr=STDOUT)
        else:
            return check_output([consolepath, 'adb', '--name', device, '--command', *cmds], shell=True, stderr=STDOUT)
    def cmd(self, device, *cmds):
        for _ in range(3):
            try:
                res = self._cmd(device, *cmds).decode('utf-8')
                if 'error:' in res:
                    logging.warn('({})[{}]\t{}'.format(device, ' '.join(cmds), e))
                    time.sleep(5)
                else:
                    return res
            except CalledProcessError as e:
                logging.warn('[{}]{}'.format(e.returncode, e.output))
                time.sleep(5)

        raise Exception('ADB Command Failed')
    def sh(self, device, shcmd):
        return self.cmd(device, 'shell', shcmd)
    def su(self, device, shcmd):
        try:
            return self.cmd(device, 'shell', "su -c '{}'".format(shcmd))
        except Exception as e:
            pass
        raise Exception('ADB Command Failed')
    def pull(self, device, target, location):
        return self.cmd(device, 'pull', target, location)
    def screen(self, deviceidx):
        assert type(deviceidx) == int
        deviceaddr = '127.0.0.1:{}'.format(5555 + deviceidx * 2)
        for _ in range(3):
            try:
                # This might fail, if original image binary contains '\r\n'
                # LDplayer console does not work properly for screen capture; we should use adb instead
                return Image.open(BytesIO(check_output([adbpath, '-s', deviceaddr, 'shell', 'screencap -p'], shell=True).replace(b'\r\n', b'\n')))
            except:
                pass
        # The app player is frozen
        raise Exception ('ADB Command Failed')

    def tap(self, device, x, y):
        return self.sh(device, 'input tap {} {}'.format(x, y))
    def tap2(self, device, x, y):
        return self.sh(device, 'input tap {} {} & sleep 0.1; input tap {} {}'.format(x, y, x, y))
    def swipe(self, device, x1, y1, x2, y2, t):        
        cmd = 'input swipe {} {} {} {} {}'.format(x1, y1, x2, y2, t)
        return self.sh(device, cmd)
    def text(self, device, txt):
        return self.sh(device, 'input text {}'.format(txt))
    def backspace(self, device):
        return self.sh(device, 'input keyevent 67')
    def back(self, device):
        return self.sh(device, 'input keyevent 4')
    def paste(self, device):
        return self.sh(device, 'input keyevent 279')
    def launch(self, device):
        return self.sh(device, 'monkey -p {} -c android.intent.category.LAUNCHER 1 2> /dev/null'.format(packagename))
    def kill(self, device):
        return self.sh(device, 'am force-stop {} 2> /dev/null'.format(packagename))
    def alive(self, device):
        try:
            res = self.sh(device, 'pidof {} 2> /dev/null'.format(packagename))
            return res and len(res.strip()) > 1
        except Exception as e:
            return False