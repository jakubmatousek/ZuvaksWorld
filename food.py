import pygame

class Food(pygame.sprite.Sprite):
    '''Trida v ktere se uklada jidlo a data o nem'''
    def __init__(self,imgPath,tileSize,energy):
        pygame.sprite.Sprite.__init__(self)
        self.surf = pygame.Surface((tileSize, tileSize))
        img = pygame.image.load(imgPath)
        self.surf.blit(img,(0,0))
        self.surf.set_colorkey((0, 0, 0))
        self.rect = self.surf.get_rect()
        self.energy = energy

    def  __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )  
