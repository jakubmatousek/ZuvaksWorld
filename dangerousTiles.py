from PIL import Image
from pos import Pos

class DangerousTile():
    '''trida smrticich policek'''
    def __init__(self,picturePath,tileSize,indexes=None):
        self.tileSize = tileSize
        self.img = Image.open(picturePath,'r')
        if indexes is not None:
            self.indexes = None
        else:
            self.selfIndex()  

    def selfIndex(self):
        '''tato metoda oindexuje obrazek a rozdeli ho na dlazdice'''
        self.indexes = list()
        width, height = self.img.size
        xTiles = int(width/self.tileSize)
        yTiles = int(height/self.tileSize)
        for x in range(xTiles):
            for y in range(yTiles):
                self.indexes.append(Pos(x,y))

    def  __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )              


           

