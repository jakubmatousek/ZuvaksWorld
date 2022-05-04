from enum import unique
from PIL import Image
import random as r


for i in range(1,6):
    '''generovani dlazdic mapy, dlazdice se ukladaji jako .png do slozky'''
    
    imgPath = f"../ground{i+1}.png"
    for ii in range(1,101):
        img = Image.open(imgPath)
        alreadyGreenX = []
        alreadyGreenY = []
        alreadyGreen = list()
        isUnique = False
        greenPixelCount = int((25*25)*(ii/100))
        print(greenPixelCount," ", ii)
        for iii in range(greenPixelCount):
            while 1:
                rndX = r.randint(0,24)
                rndY = r.randint(0,24)
                #print(f"rndX:{rndX} rndY:{rndY}; '{alreadyGreenX}; {alreadyGreenY} ;")
                found = False
                for e in alreadyGreen:
                    if e[0]==rndX and e[1]==rndY:
                        found = True
                if not found:
                    break
            alreadyGreen.append([rndX,rndY])
            img.putpixel((rndY,rndX), (0,255,0))
        iName = f'g{i+1}_f{ii}.png'        
        img.save(iName)
