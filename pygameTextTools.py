import pygame

def drawText(x, y, string, col, size, window):
    '''metoda pro vyreslovani textu'''
    font = pygame.font.SysFont("Impact", size )
    text = font.render(string, True, col)
    textbox = text.get_rect()
    textbox.center = (x, y)
    window.blit(text, textbox)

def drawOutlinedText(x,y,string,fgCol,bgCol,size,radius,window):
    '''metoda pro vykresleni outline textu'''
    drawText(x +  radius, y - radius , string, bgCol, size, window)
    drawText(x + radius, y + radius , string, bgCol, size, window)
    drawText(x - radius, y + radius , string, bgCol, size, window)
    drawText(x - radius, y - radius , string, bgCol, size, window) 
    drawText(x, y, string, fgCol, size, window) 



