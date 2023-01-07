from PIL import Image
import os
import time

from config import analyzelogpath

def analyze(img):
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
    if Error > 0:
        img.save(os.path.join(analyzelogpath, str(time.time())+'.png')) 
    
    # mark parse error as SSR
    return SSR + Error