class fertileTile():
    '''Dlazdice s urodnymi policky'''

    def __init__(self,pos,fertility,greenPixels):
        if not betweenZeroAndOne(fertility) or not betweenZeroAndOne(greenPixels):
            raise ValueError()
        self.pos = pos
        self.fertility = fertility # od 0 do 1
        self.greenPixels = greenPixels

    def __str__(self):
        return str(self.x) + "X  " + str(self.y) + "Y," + f"{self.fertility*100}% fertile"    

def betweenZeroAndOne(num):
    '''validaci metoda'''
    
    if num >= 0 and num <= 1:
        return True
    else:
        return False    
