import json
from re import T
import os
from matplotlib.cbook import maxdict
from numpy import outer
from customErrors import BadFileFormatError
import xml.etree.ElementTree as ET
import datetime

def validate_and_load_conf(ev):
    try:
            with open('conf.json') as json_file:
                ev.conf = json.load(json_file)
    except:
        raise FileNotFoundError("Konfiguracni soubor nenalezen")
        
    try:
        ev.fertileFields = ev.conf["numberOfFertileFields"]
        ev.fertility = ev.conf["fertility"]
        ev.theme_folder = ev.conf['theme']['root']
        ev.fertileFieldRadius = ev.conf["fertileFieldRadius"]
        ev.deathTilesCount = ev.conf["numberOfDangerFields"]
        ev.startPopulation = ev.conf["startPopulation"]
        ev.fps = ev.conf['fps']
        ev.zuvaksSexEnergyReq = ev.conf['zuvak']["sexEnergyReq"]
        ev.zuvaksAdultAge = ev.conf['zuvak']["adultAge"]
        ev.zuvaks_fight_duration = ev.conf['zuvak']['fightDuration']
        ev.iqKoef = ev.conf['iqKoef']
        ev.agresivityKoef = ev.conf['agresivityKoef']
        ev.theme = ev.conf['theme']
        dt = ev.conf["event_banner_disp_t"]# cas zobrazeni event banneru v sekundach  
        ev.eventBannerDispTime = dt
        attack_round_seconds = ev.conf['attack_round_seconds']
        attack_rounds  = ev.conf['attack_rounds']
        ev.frames_per_fight  = attack_round_seconds * ev.fps * attack_rounds
        print( ev.frames_per_fight)
        ev.bDispTCycles = dt * ev.fps
        ev.arrow_len = ev.theme["arrow_len"]
        ev.storm_prob = ev.conf['storm_prob']
        #ev.storm_lne = ev.conf
    except Exception  as e:
        m = "Konfiguracni soubor je poskozen"
        raise BadFileFormatError(m)

    tS = ev.conf['tileSize']
    tX = ev.conf['resX'] / tS
    tY = ev.conf['resX'] / tS
    tile_count = tX*tY
    assert type(ev.arrow_len) in [int,float], 'arrow_len musi byt cislo nebo None!'
    assert type(ev.fertileFields) == int, 'fertile fields musi byt typu int'
    assert ev.fertileFields >= 0, 'fertileFields  nesmi byt zaporne'    
    assert in_range(ev.fertileFields, 0 , tile_count), f'prilis mnoho urodnych poli (max={tile_count})'
    assert type(ev.conf['numberOfDangerFields']) == int
    assert in_range(ev.conf['numberOfDangerFields'], 0, tile_count), f'prilis mnoho smrticich poli (max={tile_count})'
    assert type(ev.fertileFields) == int, 'fertility musi byt typu int'
    assert type(ev.fertileFieldRadius) in [float,int], 'fertileFieldRadius musi byt cislo'   
    assert type(ev.fertility) == int, 'fertility musi byt cele cislo' 
    assert in_range(ev.fertility,1,None), 'fertility musi byt >= 1'
    assert type(ev.fps) == int, 'fps musi byt int'
    assert type(ev.startPopulation) == int, 'startPopulation musi byt cele cislo'
    assert in_range(ev.startPopulation,0,10**4), 'startPopulation musi byt v rozsahu 0-10000'
    assert ev.fps > 0 and ev.fps <= 240, 'fps musi byt v rozsahu 1-240'
    assert type(ev.zuvaksAdultAge) == int, 'zuvaksAdultAge musi byt typu int'
    assert type(ev.zuvaks_fight_duration) == int, 'zuvaks_fight_duration musi byt typu int'
    assert ev.zuvaks_fight_duration > 0, 'atribut zuvaks_fight_duration musi byt vetsi nez 0'
    assert type(ev.iqKoef) in [float, int] and type(ev.agresivityKoef) in [float, int], 'nespravne koeficienty' 
    assert type(ev.agresivityKoef) in [int, float], 'agresivityKoef musi byt cislo!'
    assert type(ev.iqKoef) in [int, float], 'iqKoef musi byt cislo!'
    assert type(ev.conf["attack_round_seconds"]) in [int, float], 'attack_round_seconds musi byt cislo!'
    assert type(ev.conf["attack_rounds"]) in [int], 'attack_rounds musi byt cele cislo!'
    assert in_range(ev.conf["attack_rounds"],0,None), 'attack_rounds nesmi byt zaporne cislo'
    #validate zuvaks stuff
    zuv = ev.conf['zuvak']
    assert valid_position(zuv['colorStartPoint']), f"{zuv['colorStartPoint']} neni vhodna pozice !"
    assert valid_position(zuv['colorEndPoint']), f"{zuv['colorEndPoint']} neni vhodna pozice !"
    try:
        eps = zuv['eyePoints']
        ep1 = eps[0]
        ep2 = eps[1]
    except:
        raise ValueError('eye_points ve spatnem formatu')
    assert valid_position(ep1), f"nehodna pozice !"
    assert valid_position(ep2), f"nehodna pozice !"
    assert type(zuv['startingFatStorageForDays']) in [int, float], 'startingFatStorageForDays musi byt cislo!'
    assert type(zuv['sexEnergyReq']) in [int, float], 'sexEnergyReq musi byt cislo!'
    assert type(zuv['adultAge']) ==  int, 'sexEnergyReq musi byt cislo!'
    assert in_range(zuv['adultAge'],0,None),'adultAge nesmi byt zaporne cislo'
    assert in_range(zuv['sexEnergyReq'],0,None),'sexEnergyReq nesmi byt zaporne cislo' 
    assert type(zuv['fightDuration']) ==  int, 'fightDuration musi byt cislo!'
    assert in_range(zuv['fightDuration'],0,None),'fightDuration nesmi byt zaporne cislo'
    assert valid_position(ev.conf['food']['energyRange']), 'neplatny zapis valid_position'
    return ev
#  assert type(zuv['startingFatStorageForDays']) in [int, float], 'startingFatStorageForDays musi byt cislo!'


def get_conf():
    try:
            with open('conf.json') as json_file:
                conf = json.load(json_file)
    except:
        raise FileNotFoundError("Konfiguracni soubor nenalezen")
    return conf

def valid_position(pos):
    try:
        x = pos[0]
        assert in_range(x,
                        0,
                        None)
        y = pos[1]
        assert in_range(y,
                        0,
                        None)
        return True
    except:
        return False    

def is_on_map(mapX,mapY,point):
    x = point[0]
    y = point[1]
    x_on_map = in_range(x,
     mapX,
      max_inc=False)
    y_on_map = in_range(y,
                        mapY,
                        max_inc=False)
    res = x_on_map and y_on_map
    return res

def valid_fd(path,dir):
    if dir:
        os.path.isdir(path) 
    else:    
        return os.path.isfile(path) 

def in_range(num, min, max, min_inc = True, max_inc = True):
    try:
        if min != None:
            if min_inc:
                if num < min:
                    return False
            else:
                if num <= min:
                    return False   
        if max != None:            
            if max_inc:
                if num > max:
                    return False
            else:
                if num >= max:
                    return False   
        return True
    except:
        raise ValueError('Neplatny vstup funkce')


def logError(erType,message=""):
    doc = ET.parse("error.log")
    root = doc.getroot()
    errorEl = ET.Element("Error")
    timeEl = ET.SubElement(errorEl,"time")
    timeEl.text = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    erTypeEl = ET.SubElement(errorEl,"type")
    erTypeEl.text = erType
    messEl = ET.SubElement(errorEl,"message")
    messEl.text = message
    root.append(errorEl)
    tree =  ET.ElementTree(root)
    with open("error.log","wb") as f:
        tree.write(f)

def cleanLog():
    root  = ET.Element("ERROR_LOG")
    tree = ET.ElementTree(root)
    with open ("error.log", "wb") as files :
        tree.write(files)

def logAndRaiseError(error):
    eType = type(error).__name__ 
    mess = error.__str__()
    logError(eType,mess)
    raise error 
