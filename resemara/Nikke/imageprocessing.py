import numpy as np
import os 
import cv2
import time
from PIL import Image
images = []
cwd = os.path.dirname(os.path.realpath(__file__))
mask = cv2.imread(os.path.join(cwd, 'mask.png'))
pattern_skyblue = cv2.imread(os.path.join(cwd, 'pattern_skyblue.png'))
pattern_white = cv2.imread(os.path.join(cwd, 'pattern_white.png'))

    
def findenemy(img):
    img = np.asarray(img.convert('RGB')).astype(np.uint8)
    y,x,d = img.shape
    mask = (img[:,:,0] > 230) & (img[:,:,1] < 100) & (img[:,:,2] < 100)
    mask[:220, :] = False
    mask[380:, :] = False
    mask[220:380,:150] = False
    mask[220:380,810:] = False
    mask[302:380, 418:480] = False
    mask[333:380, 480:535] = False
    reds = np.where(mask)
    reds = np.stack(reds, axis=1)
    if reds.shape[0] == 0:
        return []
    elif reds.shape[0] == 1:
        return [(reds[0][0], reds[0][1])]
    N = reds.shape[0]
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 2.0)
    flags = cv2.KMEANS_RANDOM_CENTERS
    for k in range(2,20):
        ret, label, center = cv2.kmeans(np.float32(reds), k, None, criteria, 10, flags)
        if ret / reds.shape[0] < 200:
            break
    unique, counts = np.unique(label, return_counts=True)
    try:
        assert sum(counts) == N
    except Exception as e:
        print(e)
        print(unique, counts)
        return []
    labelcnt = dict(zip(unique, counts))
    center = list(zip(center, [labelcnt[i] for i in range(k)]))
    center.sort(key=lambda t:t[1], reverse=True)
    '''
    for coord,cnt in center:
        i,j = coord
        i,j = int(i), int(j)
        img[i-1,j-1,:] = [0,0,0]
        img[i-1,j,:] = [0,0,0]
        img[i-1,j+1,:] = [0,0,0]
        img[i,j-1,:] = [0,0,0]
        img[i,j,:] = [255,255,255]
        img[i,j+1,:] = [0,0,0]
        img[i+1,j-1,:] = [0,0,0]
        img[i+1,j,:] = [0,0,0]
        img[i+1,j+1,:] = [0,0,0]
    cv2.imwrite(os.path.join(cwd, '{}.png'.format(time.time())), img[:,:,::-1])
    '''
    res = list(map(lambda x:x[0].astype(np.int32), center))
    try:
        screenY, screenX = res[0]
    except Exception as e:
        print(unique)
        print(counts)
        print(labelcnt)
        print(center)
        print(res)
    return res

    
def findcrosshair(img):
    img = np.asarray(img.convert('RGB')).astype(np.uint8)
    #print(img.shape)
    res = cv2.matchTemplate(img, pattern_skyblue, cv2.TM_CCOEFF, mask=mask)
    _, skyblue_maxv, _, skyblue_maxloc = cv2.minMaxLoc(res)
    res = cv2.matchTemplate(img, pattern_white, cv2.TM_CCOEFF, mask=mask)
    _, white_maxv, _, white_maxloc = cv2.minMaxLoc(res)
    goal_diff = 3500000
    saveimg = False
    if white_maxv > skyblue_maxv and white_maxv > goal_diff:
        x, y = white_maxloc
        if saveimg:
            i = y + 13
            j = x + 51
            
            img[i-1,j-1,:] = [0,0,0]
            img[i-1,j,:] = [0,0,0]
            img[i-1,j+1,:] = [0,0,0]
            img[i,j-1,:] = [0,0,0]
            img[i,j,:] = [255,255,255]
            img[i,j+1,:] = [0,0,0]
            img[i+1,j-1,:] = [0,0,0]
            img[i+1,j,:] = [0,0,0]
            img[i+1,j+1,:] = [0,0,0]
            cv2.imwrite(os.path.join(cwd, '{}.png'.format(time.time())), img[:,:,::-1])
        
        return {
            'found': True,
            'lockon': False,
            'y': y + 13,
            'x': x + 51,
        }
    elif skyblue_maxv > goal_diff:
        x, y = skyblue_maxloc
        if saveimg:
            i = y + 13
            j = x + 51
            img[i-1,j-1,:] = [255,0,0]
            img[i-1,j,:] = [255,0,0]
            img[i-1,j+1,:] = [255,0,0]
            img[i,j-1,:] = [255,0,0]
            img[i,j,:] = [255,0,0]
            img[i,j+1,:] = [255,0,0]
            img[i+1,j-1,:] = [255,0,0]
            img[i+1,j,:] = [255,0,0]
            img[i+1,j+1,:] = [255,0,0]
            cv2.imwrite(os.path.join(cwd, '{}.png'.format(time.time())), img[:,:,::-1])
        return {
            'found': True,
            'lockon': True,
            'y': y + 13,
            'x': x + 51,
        }
    else:
        #print('crosshair not found: v = {},{}'.format(skyblue_maxv, white_maxv))
        #cv2.imwrite(os.path.join(cwd, '{}.png'.format(time.time())), img[:,:,::-1])
        return {
            'found': False
        }

if __name__ == '__main__':
    print('run')
    img = Image.open(os.path.join(cwd, 'x.png'))
    enemies = findenemy(img)
    y, x = enemies[0]
    print(y,x)