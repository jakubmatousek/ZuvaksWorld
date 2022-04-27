import random


def decideBasedOnProbability(pOfYes):
    '''metoda vrati Pravda/Nepravda na zakladne pravdepodobnosti pravdy'''
    r = random.random()
    if r < pOfYes:
        return True
    else:
        return False

