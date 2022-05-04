import random
from PIL import Image
import numpy as np
from probabilityTools import decideBasedOnProbability
from multiprocessing import Process
import math
import glob
import matplotlib.pyplot as plt
from perlin_noise import PerlinNoise
from customErrors import *
from tools import *


fg_checked = False
bg_checked = False
fg_range_checked = False

def generateRandomBackgroundTile(tileSize,bg, fg, fg_range):
    '''generovani dlazdic pozadi mapy'''
    global fg_checked
    global bg_checked
    global fg_range_checked
    
    img = Image.new(mode="RGB", size=(tileSize, tileSize),color = bg) 

    fg = color_list_to_tuple(fg)
    bg = color_list_to_tuple(bg)

    if not fg_checked:
        if not is_color(fg):
            raise ValueError(f'{fg} neni validni barva')
        else:
            fg_checked = True

    if not bg_checked:
        if not is_color(bg):
            raise ValueError(f'{bg} neni validni barva')
        else:
            bg_checked = True       

    if not fg_range_checked:
        try:
            assert fg_range[0] >= 0 and fg_range[0] <= 100
            assert fg_range[1] >= 0 and fg_range[1] <= 100
            fg_range_checked = True
        except:
            raise ValueError('fg_range neni mezi 0 a 100')    


    fgPercent = random.randint(fg_range[0], fg_range[1]) 
    fgPixelCount = int((tileSize**2)*(fgPercent/100))
    alreadyFg = list()
    for i in range(fgPixelCount):
        while 1:
            rndX = random.randint(0,
                                  tileSize-1)
            rndY = random.randint(0,
                                  tileSize-1)
            found = False
            for e in alreadyFg:
                if e[0]==rndX and e[1]==rndY:
                    found = True
            if not found:
                break
        alreadyFg.append([rndX,rndY])
        img.putpixel((rndY,rndX), fg)
    return img    

def is_color(c):
    '''validace barvy'''
    try:
        c = list(c)
        if len(c) != 3:
            return False
        for v in c:
            if v not in range(0,256):
                return False
        return 1  
    except:
        return 0        

def color_list_to_tuple(c):
    if type(c)==tuple:
        return c
    try:    
        red = c[0]
        green = c[1]
        blue = c[2]
        tple = (red,
                green,
                blue)
        return tple
    except:
        pass     


def generateFertileTile(tileSize,percent,fertile_color,bg, fg, fg_percent_range):
    '''generovani urodnych dlazdic'''
    assert percent >= 0
    assert percent <= 1
    if type(fertile_color) == list:
        assert len(fertile_color) == 3
        fertile_color = tuple(fertile_color)
    img = generateRandomBackgroundTile(tileSize,
                                       bg,
                                       fg,
                                       fg_percent_range)
    fgPixelCount = int((tileSize**2)*(percent))
    alreadyFg = list()
    for i in range(fgPixelCount):
        while 1:
            rndX = random.randint(0,tileSize-1)
            rndY = random.randint(0,tileSize-1)
            found = False
            for e in alreadyFg:
                if e[0]==rndX and e[1]==rndY:
                    found = True
            if not found:
                break
        alreadyFg.append([rndX,rndY])
        img.putpixel((rndY,rndX), fertile_color)
    return img    


def generateCloud(noisePx,imgSize,fg,save,img=None,rndMp=False,):
    '''generovani mraku 1. metodou'''
    width,height = imgSize
    if not rndMp:
        midPoint = np.array([width//2,height//2])
    else:
        rndX = random.randint(0,
                              width-1)
        rndY = random.randint(0,
                              height-1)
        midPoint = np.array([rndX,rndY])
    if img != None:
        img = img
    else:        
        img = Image.new(mode="RGB",
                        size=(width, height)) 

    if noisePx > width * height:    
        for i in range(noisePx):
            rndX = random.randint(0,width-1)
            rndY = random.randint(0,height-1)
            rndPoint = np.array([rndX,rndY])
            disFromMid = np.linalg.norm(midPoint-rndPoint)
            revDis = 1/disFromMid
            drawPixel = decideBasedOnProbability(revDis**4)
            if drawPixel:
                img.putpixel((rndX,rndY),fg)
    else:
        for x in range(width):
            for y in range(height):
                cP = np.array([x,y])
                disFromMid = np.linalg.norm(midPoint-cP)
                revDis = 1/disFromMid
                drawPixel = decideBasedOnProbability(revDis)
                if drawPixel:
                    cP_tuple = (x,y)
                    img.putpixel(cP_tuple,fg)

    if save:
        al = string.ascii_lowercase
        used = list()
        pixelNumberFormated = format(noisePx, "10.2e")
        rndName = 'textures/clouds/' + pixelNumberFormated
        for i in range(0,5):
            while 1:
                letter = random.choice(al)
                if letter not in used:
                    used.append(letter)
                    rndName = rndName + letter
                    break
        imgPath = rndName + '.png'
        img.save(imgPath)         
    else:            
        return img        


def makeClouds(size,n):
    '''tato metoda vola vicekrat metodu pro generovani mraku. Generovani probiha paralalne'''
    grey = (169,169,169)
    for i in range(n):
        p = Process(target=generateCloud, args=(10**5,size,grey,True))
        p.start()

def brightness(color):
    # vrati svetelnost pixelu
    r,g,b = color
    rBr = r ** 2 * 0.241
    gBr = g ** 2 * 0.691
    bBr = b ** 2 * 0.068
    finalBr = math.sqrt(rBr+gBr+bBr)
    return finalBr

def darknessPer(color):
    d = 255 - brightness(color)
    dPercent = d/255
    return dPercent

def perlinCloud(size,gradient_img=None,t=None):
    '''
       tato metoda generuje mraky pomoci perlin noise,
       tento zpusob generovani se mi nakonec osvedcil vice
    '''
    sX,sY = size
    noise1 = PerlinNoise(octaves=9)
    pic = []
    if gradient_img != None:
        try:
            gImg = Image.open('textures/perlin_resources/gradient.jpeg')
        except:
            checkFile('textures/perlin_resources/gradient.jpeg')    
    else:
        gImg = gradient_img        
    gImg = gImg.convert('RGB')
    gImg = gImg.resize(size)
    t = 0
    for r in range(sX):
        row = []
        for c in range(sY):
            if t != None:
                noise_val = noise1([r/sX, c/sY,t])
            else:
                noise_val = noise1([r/sX, c/sY])    
            colOfGradPix = gImg.getpixel((c, r))
            dOfGradPix = darknessPer(colOfGradPix)
            noise_mapped = (noise_val+1) / 2
            row.append(noise_mapped * dOfGradPix)
            #print(f'x{r} y{c}, noise: {noise_val}, dOfGrad: {dOfGradPix}, comb: {noise_val * dOfGradPix}')
        pic.append(row)
    plt.imshow(pic, cmap='gray')
    return plt

def makeBlackDisapear(path,size):
    '''metoda odstranuje z obrazku cernou barvu'''
    if not type(size):
        raise not_valid_RGB()
    low_black = 0
    high_black = 130 # threshold
    grayScale = list()
    for i in range(low_black,high_black):
        grayScale.append(i)
    img = Image.open(path)
    rgba = img.convert("RGBA")
    datas = rgba.getdata()
  
    newData = []
    for item in datas:
        cAvg =  item[0] + item[1] + item[2]
        cAvg = cAvg / 3
        if cAvg in grayScale:
            newData.append((255,
                            255,
                            255,
                            0))
        else:
            newData.append(item)
  
    rgba.putdata(newData)
    rgba = rgba.resize(size)
    rgba.save(path, "PNG")

def perlinSlideshow(size,count):
    '''tato metoda pousti generaci mraku a uklada ji do slozky pro pozdejsi pouziti'''
    sX,sY = size
    for x in range(0,count):
        img = perlinCloud(size,x*0.0001)
        path = f'textures/clouds/{x+1}.png'
        img.savefig(path,
                    bbox_inches='tight',
                    pad_inches=0,transparent=True)
        makeBlackDisapear(path,size)

def oneToCenter(n):
    if n == 0:
        return n + 1
    else:
        return n - 2

def pickCornerOfMatrix(matrX,matrY):
    '''vybere roh matice'''
    x = matrX*random.randint(0,1)
    y = matrY*random.randint(0,1)
    return [x,y]

def pickEdgeOfMatrix(matrX,matrY):
    '''vybere stranu matrixu'''
    x = random.randint(0, matrX-1)
    y = random.randint(0, matrY-1)
    return [x,y]

def joined_clouds_from_folder():
    '''metoda zkompiluje mraky ulozene ve slozce v jeden maxi mrak'''
    size = 500
    clouds_to_join = 50

    cloud_folder = 'textures\clouds\*.png'
    cloud_paths = glob.glob(cloud_folder)
    cloud_count = len(cloud_paths)
    img = Image.new(mode="RGBA",
                    size=(size, size),
                    color = (0,0,0)) 
    h_size = int(size/2)
    center = [h_size,h_size]                
    for x in range(clouds_to_join):
        r_ind = random.randint(0,cloud_count-1)
        cloud_path = cloud_paths[r_ind]
        cloud = Image.open(cloud_path)
        cloud = cloud.convert("RGBA")
  
        cloud_pos = list()
        for xx in range(2):
            distance = random.uniform(0.001,0.8) ** 2
            distance = int(distance * h_size)
            distance = rnd_invert(distance)
            pos = h_size+distance
            cloud_pos.append(pos)
        sX, sY = cloud.size
        off_x = int(sX/2)
        off_y = int(sY/2)
        cloud_pos_adjusted = [cloud_pos[0]-off_x,
                              cloud_pos[1]-off_y]
        img = trans_paste(cloud,img,1,cloud_pos_adjusted)

    clouds_in_f =  len(glob.glob('textures/clouds/big_ones/*.png'))
    number = clouds_in_f + 1
    img.save(f'textures/clouds/big_ones/{number}.png', 'png') 


def trans_paste(fg_img,bg_img,alpha=1.0,box=(0,0)):
    fg_img_trans = Image.new("RGBA",
                             fg_img.size)
    fg_img_trans = Image.blend(fg_img_trans,
                               fg_img,alpha)
    bg_img.paste(fg_img_trans,
                 box,
                 fg_img_trans)
    return bg_img

def rnd_invert(n):
    invert = random.randint(0,1)
    if invert:
        return n*-1
    return n    

    
if __name__ == '__main__':
    for x in range(200):
        joined_clouds_from_folder()