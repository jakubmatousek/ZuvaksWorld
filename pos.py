import random

class Pos:
    #Trida 2d pozice
    def __init__(self,pos_x,pos_y):
        self.x = pos_x
        self.y = pos_y

    def __str__(self):
        return str(self.x) + "X  " + str(self.y) + "Y"

class RandomPos(Pos):
    #Trida nahodne 2d pozice
    def __init__(self,rangeX,rangeY):
        xF,xT = rangeX
        yF,yT = rangeY
        x = random.randint(xF,xT)
        y = random.randint(yF,yT)
        super().__init__(x,y)






            