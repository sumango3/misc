from macro import macro
from console import Console
from multiprocessing import Process, Value
import time
import sys
import time
import os
import logging
from config import macrologpath

def worker(deviceidx, quit):
    logging.basicConfig(
        filename=os.path.join(macrologpath, str(deviceidx)+'.log'),
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(message)s'
    )
    sys.stdout = open(os.devnull, 'w') # do not print
    sys.stderr = open(os.devnull, 'w')
    console = Console()
    logging.info('Console loaded')
    while not quit.value:
        logging.info('process create')
        p = Process(target=macro, args=(deviceidx, quit))
        p.start()
        logging.info('process started')
        p.join(5400) # wait for 90 min
        if p.is_alive() or p.exitcode != 0:
            # app player or macro function is frozen
            if p.is_alive():
                logging.warn('terminating macro')
                p.terminate()
            else:
                logging.warn('exit code: {}'.format(p.exitcode))
            logging.warn('Reboot required')
            console.reboot(deviceidx)
            console.boot(deviceidx)
            time.sleep(30)
            

class Manager:
    workers = {}
    devices = {}
    # devices = {
    #   x: {
    #       name: "asdf",
    #       boot: False,
    #       worker: Process(...),
    #       quit: Value(),
    #   },
    # }
    console = Console()
    lastLaunch = 0
    def updateDevice(self):
        visited = set()
        devices = self.console.devices()
        for device in devices:
            idx = device['index']
            visited.add(idx)
            if idx in self.devices:
                self.devices[idx]['name'] = device['name']
                self.devices[idx]['boot'] = device['boot']
                if self.devices[idx]['worker'] and not self.devices[idx]['worker'].is_alive():
                    self.devices[idx]['worker'] = None
                    self.devices[idx]['quit'] = None
            else:
                self.devices[idx] = {
                    'index': device['index'],
                    'name': device['name'],
                    'boot': device['boot'],
                    'worker': None,
                    'quit': None
                }
        removed = set(self.devices.keys()) - set(map(lambda d:d['index'], devices))
        for idx in removed:
            if self.devices[idx]['worker']:
                self.devices[idx]['worker'].terminate()
            self.devices[idx]['worker'] = None
            del self.devices[idx]
    def bootDevice(self, deviceidx):
        device = self.devices[deviceidx]
        if not device['boot']:
            self.console.boot(deviceidx)
    def startWorker(self, deviceidx):
        device = self.devices[deviceidx]
        if device['worker'] == None:
            v = Value('b', 0)
            p = Process(target=worker, args=(deviceidx,v))
            print('new worker: idx={}'.format(deviceidx))
            delay = self.lastLaunch + 120 - time.time()
            if delay > 0:
                print('waiting for 2 min delay ...', end = '')
                sys.stdout.flush()
                time.sleep(delay)
                print(' Done!')
            print('worker start')
            p.start()
            self.lastLaunch = time.time()
            device['worker'] = p
            device['quit'] = v
    def endWorker(self, deviceidx):
        device = self.devices[deviceidx]
        if device['quit'] != None:
            device['quit'].value = 1
    def terminateWorker(self, deviceidx):
        device = self.devices[deviceidx]
        if device['worker'] != None:
            device['worker'].terminate()
            device['worker'] = None
            device['quit'] = None
    
    def run(self):
        print('press H to see help')
        while True:
            cmd = None
            try:
                cmd = input('>> ')
            except Exception:
                continue
            cmds = cmd.strip().split()
            if len(cmds) == 0:
                continue
            if cmds[0] == 'h':
                # help
                print('H(Help) D(Devices) B(Boot device) S(Start worker) R (Restart worker) T(Terminate worker) E(End worker) Q(Quit)')
                print('B [all | <device name | device index>]\tboot device')
                print('S [all | <device name | device index>]\tstart worker (do not affect running workers)')
                print('R [all | <device name | device index>]\trestart worker (for running workers, terminate and restart)')
                print('T [all | <device name | device index>]\tterminate worker; stop worker immediately, macro process will end at this loop')
            elif cmds[0].lower() == 'd':
                # print current devices
                self.updateDevice()
                for idx in self.devices.keys():
                    device = self.devices[idx]
                    name = device['name']
                    boot = 'On' if device['boot'] else 'Off'
                    state = ''
                    if device['worker'] == None:
                        state = 'Not running'
                    elif device['quit'].value:
                        state = 'Waiting for end'
                    else:
                        state = 'Running'
                    print('[{}]\t{}\t{}\t{}'.format(idx, name, boot, state))
            elif cmds[0].lower() == 'b':
                # boot device
                self.updateDevice()
                firstProcess = True
                if len(cmds) == 2 and cmds[1] == 'all':
                    print('boot all')
                    for idx in self.devices.keys():
                        self.bootDevice(idx)
                else:
                    for devicestr in cmds[1:]:
                        print(devicestr)
                        try:
                            # assume that given str is id
                            idx = int(devicestr)
                            self.bootDevice(idx)
                        except Exception:
                            # given str is device name
                            for device in self.devices.values():
                                if device['name'] == devicestr:
                                    self.bootDevice(device['index'])
                                    break
            elif cmds[0].lower() == 's':
                # start worker
                self.updateDevice()
                if len(cmds) == 2 and cmds[1] == 'all':
                    for idx in self.devices.keys():
                        if self.devices[idx]['boot']:
                            self.startWorker(idx)
                else:
                    for devicestr in cmds[1:]:
                        try:
                            # assume that given str is id
                            idx = int(devicestr)
                            self.startWorker(idx)
                        except:
                            # given str is device name
                            for device in self.devices.values():
                                if device['name'] == devicestr:
                                    self.startWorker(device['index'])
                                    break
            elif cmds[0].lower() == 'r':
                # restart worker
                self.updateDevice()
                if len(cmds) == 2 and cmds[1] == 'all':
                    for device in self.devices.values():
                        if device['worker'] != None:
                            self.terminateWorker(device['index'])
                        self.startWorker(device['index'])
                else:
                    for devicestr in cmds[1:]:
                        device = None
                        try:
                            idx = int(devicestr)
                            device = self.devices[idx]
                            if device['worker'] != None:
                                self.terminateWorker(idx)
                            self.startWorker(idx)
                        except:
                            for device in self.devices.values():
                                if devicestr == device['name']:
                                    if device['worker'] != None:
                                        self.terminateWorker(device['index'])
                                    self.startWorker(device['index'])

            elif cmds[0].lower() == 't':
                # terminate worker
                self.updateDevice()
                if len(cmds) == 2 and cmds[1] == 'all':
                    for device in self.devices.values():
                        if device['worker'] != None:
                            self.terminateWorker(device['index'])
                else:
                    for devicestr in cmds[1:]:
                        device = None
                        try:
                            idx = int(devicestr)
                            device = self.devices[idx]
                            if device['worker'] != None:
                                self.terminateWorker(idx)
                        except:
                            for device in self.devices.values():
                                if devicestr == device['name']:
                                    if device['worker'] != None:
                                        self.terminateWorker(device['index'])
            elif cmds[0].lower() == 'q':
                for device in self.devices.values():
                    if device['worker'] != None:
                        device['worker'].terminate()
                return