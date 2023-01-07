from manager import Manager
import ctypes
import sys

if __name__ == '__main__':
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        manager = Manager()
        manager.run()