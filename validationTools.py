import json
import os
from customErrors import BadFileFormatError

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
    assert type(ev.conf['numberOfDangerFields']) == int
    assert type(ev.fertileFields) == int, 'fertility musi byt typu int'
    assert type(ev.fertileFieldRadius) in [float,int], 'fertileFieldRadius musi byt cislo'   
    assert type(ev.fertility) == int, 'fertility musi byt cele cislo' 
    assert type(ev.fps) == int, 'fps musi byt int'
    assert type(ev.startPopulation) == int, 'startPopulation musi byt cele cislo'
    assert ev.fps > 0 and ev.fps <= 240, 'fps musi byt v rozsahu 1-240'
    assert type(ev.zuvaksAdultAge) == int, 'zuvaksAdultAge musi byt typu int'
    assert type(ev.zuvaks_fight_duration) == int, 'zuvaks_fight_duration musi byt typu int'
    assert ev.zuvaks_fight_duration > 0, 'atribut zuvaks_fight_duration musi byt vetsi nez 0'
    assert type(ev.iqKoef) in [float, int] and type(ev.agresivityKoef) in [float, int], 'nespravne koeficienty' 
    assert type(ev.agresivityKoef) in [int, float], 'agresivityKoef musi byt cislo!'
    assert type(ev.iqKoef) in [int, float], 'iqKoef musi byt cislo!'
    assert type(ev.conf["attack_round_seconds"]) in [int, float], 'attack_round_seconds musi byt cislo!'
    assert type(ev.conf["attack_rounds"]) in [int], 'attack_rounds musi byt cele cislo!'
    #validate zuvaks stuff
    zuv = ev.conf['zuvak']
    try:
        eps = zuv['eyePoints']
        ep1 = eps[0]
        ep2 = eps[1]
    except:
        raise ValueError('eye_points ve spatnem formatu')
    assert type(zuv['startingFatStorageForDays']) in [int, float], 'startingFatStorageForDays musi byt cislo!'
    assert type(zuv['sexEnergyReq']) in [int, float], 'sexEnergyReq musi byt cislo!'
    assert type(zuv['adultAge']) ==  int, 'sexEnergyReq musi byt cislo!'
    assert type(zuv['fightDuration']) ==  int, 'fightDuration musi byt cislo!'
    return ev


def get_conf():
    try:
            with open('conf.json') as json_file:
                conf = json.load(json_file)
    except:
        raise FileNotFoundError("Konfiguracni soubor nenalezen")
    return conf


def is_on_map(mapX,mapY,point):
    x = point[0]
    y = point[1]
    x_on_map = x < mapX and x >=0
    y_on_map = y < mapY and y >=0
    res = x_on_map and y_on_map
    return res

def valid_fd(path,dir):
    if dir:
        os.path.isdir(path) 
    else:    
        return os.path.isfile(path) 





