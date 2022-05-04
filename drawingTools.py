from cv2 import sqrt
import pygame as p
import json
import math
import numpy as np



class AttackAnimator():
    '''tato trida se stara o animovani boje mezi zuvaky'''
    def __init__(self,display_surface, tile_size, arrow_len = None):
        self.load_config()
        fpr = self.round_sec*self.fps
        fpr = int(fpr)
        self.frames_per_round = fpr
        self.display_surface = display_surface
        self.ts = tile_size
        self.arrow_len = arrow_len

    def draw_frame(self, frame_number, start_point,  vector):
        '''vykresleni obrazku animace'''
        dir_a_to_b = frame_number //  self.frames_per_round
        dir_a_to_b = not (dir_a_to_b % 2 )

        start_point = [start_point[0]*self.ts, start_point[1]*self.ts]
        if dir_a_to_b:
            fn =   frame_number % self.frames_per_round
            start_progress = self.get_progress(fn)
            end_progress = self.get_progress(fn+1)
        else:
            fn = self.frames_per_round - frame_number % self.frames_per_round
            start_progress = self.get_progress(fn)
            end_progress = self.get_progress(fn-1)

        lsr_start_p = [vector[0]*start_progress, vector[1]*start_progress]
        lsr_end_p = [vector[0]*end_progress, vector[1]*end_progress]
        
        laser_start = [int(start_point[0]+lsr_start_p[0]+self.center_offset),
                       int(start_point[1]+lsr_start_p[1])+self.center_offset] 
        laser_end = [int(start_point[0]+lsr_end_p[0])+self.center_offset,
                     int(start_point[1]+lsr_end_p[1])+self.center_offset]

        p.draw.line(self.display_surface,
                    self.fight_visualisation_color,
                    tuple(laser_start),
                    tuple(laser_end),
                    self.laser_thickness)
        
        if self.arrow_len != None:
            self.draw_arrow(laser_end)


    def draw_arrow(self,laser_end):
        '''tato metoda kresli na koncich laseru sipky'''
        half_d = int(self.arrow_len/2)
        lp = [laser_end[0] - half_d,
              laser_end[1] + self.arrow_len]
        rp = [laser_end[0] + half_d,
              laser_end[1] + self.arrow_len]
        points = [lp,
                  rp,
                  laser_end]
        p.draw.polygon(self.display_surface,
                       self.fight_visualisation_color,
                       points)                         

    def calc_time(self,frame_number):
        return (frame_number / self.frames_per_round * self.round_sec / self.frames_per_round)

    def get_progress(self,frame_number):
        '''tato metoda vraci v progress animace (output=0.5 -> 50%, 0.7 -> 70%, atd...)'''
        try:
            prog = frame_number / self.frames_per_round 
        except:
            prog = 0    
        return prog    

    def load_config(self):
        '''nacteni konfigurace'''
        try:
            with open('conf.json') as json_file:
                conf = json.load(json_file)
        except:
            raise FileNotFoundError("connection config file not found")
        assert type(conf["attack_round_seconds"]) in [int,float], 'attack_round_seconds must be a number'
        assert type(conf["attack_rounds"]) in [int], 'attack_rounds must be a whole number'
        assert type(conf['fps']) in [int, float] and conf['fps'] > 0, 'FPS must be a number and larger than 0' 
        assert len(conf['theme']['fight_visualisation_color']) == 3 , 'fight_visualisation_color must not be empty'
        assert type(conf['theme']["laser_thickness"]) in [int,float], 'laser_thickness must not be empty'
        self.round_sec = conf["attack_round_seconds"]
        self.attack_rounds = conf["attack_rounds"]
        self.fps = conf["fps"]
        self.fight_visualisation_color = tuple(conf['theme']["fight_visualisation_color"])
        self.laser_thickness = conf['theme']['laser_thickness']
        self.center_offset = int(conf['tileSize']/2)

    def grid_to_pix(self,pos):
        '''prevod pozice dlazdice na pixels'''
        return [pos[0]*self.ts,
               pos[1]*self.ts] 

    def draw_frame_of_linear_attack(self,frame_number, distance,pos_a):
        '''vykresleni obrazku animace'''
        velocity = distance / self.round_sec 
        laser_start_distance = self.calc_time(frame_number) * velocity
        laser_end_distance = self.calc_time(frame_number+1) * velocity
        laser_start = [pos_a[0]+laser_start_distance,pos_a[1]+laser_start_distance]
        laser_end = [pos_a[0]+laser_end_distance,pos_a[1]+laser_end_distance]
        laser_start = f_pos_to_int(laser_start)
        laser_end = f_pos_to_int(laser_end)
             

def f_pos_to_int(pos):
    return [int(pos[0]),
            int(pos[1])] 

        
 

