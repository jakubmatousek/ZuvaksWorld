import json
from customErrors import FileError

path = 'conf.json'

def update_conf_val(key,value, subkey = False):
    '''metoda pro zapisovani dat do configu'''
    try:
        file = open( path, "r")
        json_object = json.load(file)
        file.close()
        if not subkey:
            json_object[key] = value
        else:
            json_object[key][subkey] = value
        file = open(path, "w")
        json.dump(json_object, file)
        file.close()
    except:
        raise FileError('Ouch, nemohl jsem zapsat data do Confu')    