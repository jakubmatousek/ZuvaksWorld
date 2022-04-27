
from pos import Pos

def getPositionsOfWrapingPoints(sizeX,sizeY,point,radius=1):
    """tato funkce vrati indexy vsech okolnich bodu v 2d matrixu.
       pozice vrati jako objekty Pos.py
    """

    assert type(sizeX) == int, 'vstupni argument sizeX musi byt typu int'
    assert type(sizeY) == int, 'vstupni argument sizeY musi byt typu int'
    assert type(radius) == int, 'vstupni argument radius musi byt typu int'
    
    positions = []
    sqSideSize  = radius*2+1
    startX = point.x-radius
    startY = point.y-radius
    endX = startX+sqSideSize
    endY = startY+sqSideSize

    if startX < 0:
        startX = 0
    if endX > sizeX:
        endX = sizeX
    if startY < 0:
        startY = 0
    if endY > sizeY:
        endY = sizeY  
    for y in range (0,endY-startY):
        for x in range (0,endX-startX):
            nIndex = Pos(startX+x,+startY+y)
            if nIndex.x == point.x and nIndex.y == point.y:
                continue 
            positions.append(nIndex)
    return positions                   


def printPositions(posList):
    for pos in posList:
        print(pos)


def pos_of_wrapping_points_list_format(sizeX,sizeY,point,radius=1):
    """tato funkce vrati indexy vsech okolnich bodu v 2d matrixu v [x,y] formatu"""
    positions = []
    sqSideSize  = radius*2+1
    startX = point[0]-radius
    startY = point[1]-radius
    endX = startX+sqSideSize
    endY = startY+sqSideSize

    if startX < 0:
        startX = 0
    if endX > sizeX:
        endX = sizeX
    if startY < 0:
        startY = 0
    if endY > sizeY:
        endY = sizeY  
    for y in range (0,endY-startY):
        for x in range (0,endX-startX):
            nIndex = [startX+x,startY+y]
            if nIndex[0] == point[0] and nIndex[1] == point[1]:
                continue 
            positions.append(nIndex)
    return positions            

def most_balanced(elements):
    '''tato symetricky usporadane hodnoty radku v matrixu'''
    topN = 10**8
    winIndex = None
    for e in elements:
        rs = 0
        ls = 0
        row = list(e).copy()
        if len(row)%2==1:
            del row[int((len(row)-1)/2)]
        rowLen = len(row)    
        for colIn in range(rowLen):
            if colIn < int(rowLen/2):
                ls+=row[colIn]
            else:
                rs+=row[colIn]
        wDiff = abs(rs-ls)
        if wDiff < topN:
            topN = wDiff
            winIndex = elements.index(e)
    winEl = elements[winIndex]
    return [winEl,winEl[::-1]]        

def isNum(num):
    #validace cisla
    try:
        int(num)
    except ValueError:
        return False
    else:
        return True    