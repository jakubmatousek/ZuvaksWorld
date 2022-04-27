import os
import customErrors 

def checkFile(path):
    '''nastoj pro validaci'''
    if os.path.isfile('filename.txt'):
        return True
    else:
        m = f'demanded file ({path}) does not exsist'
        raise FileExistsError(m)


