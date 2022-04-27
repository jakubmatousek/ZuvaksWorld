from menuTools import NumberPicker, ResolutionPicker
import pygame as p
from pygame.locals import *
from pygame import mixer
from validationTools import get_conf
from fileTools import *
from manager import Manager

class MainMenu():
    '''Hlavni menu'''
    def __init__(self):
        p.init()
        p.display.set_caption('Zuvak\'s world')
        self.conf = get_conf()
        self.FONT_COLOR = (255,255,255)
        self.ACTIVE_FONT_COLOR = (0,0,0)
        self.ACTIVE_ROW_COLOR = (255,255,255)
        self.HELP_BAR_ROW_COLOR = (210,210,210)
        self.HELP_BAR_FONT_COLOR = (0,0,0)
        self.logo_width_ratio = 0.9 # logo zabira 90% sirky obrazovky
        self.logo_top_off_ratio = 0.1 #odrazeni od shora
        self.first_banner_off = 0.35
        self.banner_off = 0.09
        self.HEIGHT = self.conf['resY']
        self.WIDTH = self.conf['resX']
        self.fps = self.conf['fps']
        self.choices = list()
        self.active_index = 0
        self.font_size = 35
        self.instr_font_size = 15
        self.clock = p.time.Clock()
        self.set_font_size(self.font_size)
        self.instr_font = p.font.Font('textures/fonts/DOS.TTF', self.instr_font_size)
        self.disp_surf = p.display.set_mode((self.WIDTH,self.HEIGHT))
        self.bck_img = p.image.load('textures/menu/bg_pix.png')
        self.logo_img = p.image.load('textures/menu/logo_pix.png')
        self.instruction_bar_heigth = 0.05 #v procentech
        self.instructions_txt = "ESC=ukoncit ENTER=potvrdit"
        self.init_choices()
        self.init_bug_pointer()
        self.init_dos_border()
        self.init_mixer()
        self.init_banners()
        self.update_pointer(0)
        self.update()
        self.start_loopin()
        

    def init_choices(self):
        ch = [['SPUSTIT', self.configure_and_play],['NASTAVENI', self.settings_loop]]
        self.set_choices(ch) 

    def set_choices(self,choices):
        self.choices = choices

    def init_dos_border(self):
        # nacteni ramecku do pameti
        pth = 'textures/menu/dos_border.png'
        self.border_img = p.image.load(pth)
        self.border_img.set_colorkey((0,0,0))
        self.border_img = p.transform.scale(self.border_img, (self.WIDTH,self.HEIGHT))

    def draw_border(self):
        self.disp_surf.blit(self.border_img, (0,0))    

    def init_bug_pointer(self):
        #nacteni ukazatele aktivniho radku 
        theme_root = self.conf['theme']['root']
        pth = theme_root + '/zuvak.png'
        img_coef = 0.6
        self.bug_offset = 10
        self.bug_img = p.image.load(pth)
        self.bug_img = p.transform.scale(self.bug_img, (int(self.letter_heigth * img_coef), int(self.letter_heigth * img_coef)))
        self.bug_img.set_colorkey((0, 0, 0))
        self.bug_center = ( int(self.bug_img.get_width() / 2), int(self.bug_img.get_height() / 2))

    def init_banners(self):
        #nacteni banneru
        self.logo_offset_x = int((self.WIDTH -  (self.logo_width_ratio * self.WIDTH )) / 2)
        self.logo_offset_y = self.HEIGHT * self.logo_top_off_ratio
        org_logo_width =  self.logo_img.get_width() 
        org_logo_heigth = self.logo_img.get_height()
        logo_aspect_ratio = org_logo_width / org_logo_heigth
        logo_width = int(self.WIDTH * self.logo_width_ratio)
        logo_heigth = int(logo_width / logo_aspect_ratio)
        scale = (logo_width, logo_heigth)
        self.logo_img = p.transform.scale(self.logo_img, scale)
        self.logo_img.set_colorkey((0,0,0))
        self.bck_img = p.transform.scale(self.bck_img, (self.WIDTH, self.WIDTH))
                             
    def init_mixer(self):
        #inicializace mixeru zvukovych efektu
        mixer.init()
        mixer.music.load("music/menu_sound.wav")
        mixer.music.set_volume(0.5)
       
       

    def update_pointer(self,direction): 
        #tato metoda se vola pri stisknuti sipky nahoru/dolu
        #pri zavolani posune index aktivniho radku podle smeru stisknute sipky
        if direction == -1:
            if self.active_index > 0:
                self.active_index = self.active_index - 1
        elif direction == 1:
            if self.active_index < len(self.choices) - 1 :
                self.active_index = self.active_index + 1   

    def draw_choice_banners(self):
        # vykreslovani radku s moznostmi
        c = 0
        for choice in self.choices:
            y_offset =  self.first_banner_off + (c*self.banner_off)
            ch_txt = choice[0]
            if len(choice)>2:
                if choice[2] != None or choice[2] != False:
                    ch_txt = ch_txt + choice[2].__str__()
            banner_pos = self.center_banner(ch_txt, y_offset)
            rendered = None
            if c==self.active_index:
                self.draw_rect_behind_banner(banner_pos)    
                rendered = self.font.render(ch_txt, False, self.ACTIVE_FONT_COLOR)
            else:
                rendered = self.font.render(ch_txt, False, self.FONT_COLOR)  
            self.disp_surf.blit(rendered, banner_pos) 
            c+=1


    def pick_choice(self):
        index = self.active_index
        choice = self.choices[index]
        func = choice[1]
        func()          

    def update(self):
        #tato metoda se vola kdyz je potreba vykreslit nejakou zmenu
        self.disp_surf.blit(self.bck_img, (0,0))
        self.disp_surf.blit(self.logo_img, (self.logo_offset_x, self.logo_offset_y))
        self.draw_choice_banners()
        self.draw_instructions()
        self.draw_border()
        mixer.music.play()

    def draw_instructions(self):
        # tato metoda vykresluje banner s informacemi o ovladani hlavniho menu
        H = int(self.instruction_bar_heigth * self.HEIGHT)
        top_x = 0
        top_y = self.HEIGHT - H
        rect = p.Rect(top_x, top_y, self.WIDTH, H)
        p.draw.rect(self.disp_surf, self.HELP_BAR_ROW_COLOR, rect)
        txt = self.instructions_txt    
        txt_h = self.get_size_of_txt(txt,0,1,self.instr_font)
        txt_h_center = int(txt_h / 2)
        half_banner = (H / 2)
        txt_x = int(self.WIDTH*0.02)
        txt_y = top_y+half_banner-txt_h_center
        rendered_txt = self.instr_font.render(txt, False, self.HELP_BAR_FONT_COLOR)   
        self.disp_surf.blit(rendered_txt, (txt_x,txt_y)) 


    def center_banner(self, txt, offset_y):
        # vycentrovani radku
        width = self.get_size_of_txt(txt,True)
        center = self.WIDTH / 2
        txt_center = width / 2
        x = int(center - txt_center)
        y = int(self.HEIGHT * offset_y)
        return (x,y)

    def draw_rect_behind_banner(self, banner_pos, color = None):
        #vykreslovani obdelniku za textem aktivniho radku
        b_x, b_y = banner_pos
        rect = p.Rect(0, b_y-1, self.WIDTH, int(self.letter_heigth))
        if color == None:
            p.draw.rect(self.disp_surf, self.ACTIVE_ROW_COLOR, rect)
        else:
            p.draw.rect(self.disp_surf, color, rect)

        row_c_off = self.letter_heigth / 2
        bug_x,bug_y  = self.bug_center
        self.disp_surf.blit(
            self.bug_img,
            (
                b_x - bug_x * 2 - self.bug_offset,
                b_y + row_c_off - bug_y 
            )
        )


    def get_size_of_txt(self, txt, w = False, h = False, font = False):
        #vrati valikost textu v pixelech
        if not font:
            width, heigth = self.font.size(txt)
        else:
            width, heigth = font.size(txt)
        if w:
            return width
        if h:
            return heigth
        return (width,heigth)
        
           
    def start_loopin(self):      
        #uvodni stranka menu
        notQuit = True
        while notQuit:
            for event in p.event.get():
                if event.type == QUIT:
                    notQuit = False
                if event.type == p.KEYDOWN:
                    if event.key == p.K_ESCAPE:
                        notQuit = False
                        quit()
                    if event.key == p.K_UP:
                        self.update_pointer(-1)
                    if event.key == p.K_DOWN:
                        self.update_pointer(1)  
                    if event.key == 13: #enter
                        self.pick_choice()
                        self.init_choices()
                    self.update()
            self.clock.tick(self.fps)  
            p.display.update() 


    def set_font_size(self,fs):
        #nastaveni velikosti fontu
        self.font_size = fs
        self.font = p.font.Font('textures/fonts/press-start.regular.TTF', fs) 
        self.letter_heigth = self.get_size_of_txt("I",False, True)
        self.init_bug_pointer()

    def settings_loop(self):
        #Stranka s nastavenim programu
        running = True
        rp =  ResolutionPicker()
        np = NumberPicker(15,1,30,1)
        choices = [['ROZLISENI: ',None, rp], ['RYCHLOST (cyklu/s): ', None, np]]  
        self.set_choices(choices)
        self.active_index = 0
        saved_font_size = self.font_size
        saved_instructions_txt = self.instructions_txt
        self.set_font_size(25)
        self.instructions_txt = "ESC=ukoncit ENTER=potvrdit P_SIPKA=zvysit hodnotu L_SIPKA=snizit hodnotu "
        self.update()
        while running:
            for event in p.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == p.KEYDOWN:
                    if event.key == p.K_ESCAPE:
                        running = False
                    if event.key == p.K_UP:
                        self.update_pointer(-1)
                    if event.key == p.K_DOWN:
                        self.update_pointer(1) 
                    if event.key == 13: #enter
                       pass
                    if event.key == p.K_RIGHT:
                        self.choices[self.active_index][2].next()
                    if event.key == p.K_LEFT:
                        self.choices[self.active_index][2].prev()
                    self.update()            
            self.clock.tick(self.fps)  
            p.display.update() 
        
        resX,resY = rp.get_value()
        update_conf_val('resX',resX)
        update_conf_val('resY',resX)       
        np_val = np.get_value()
        update_conf_val('fps', np_val)
        self.set_font_size(saved_font_size)  
        self.instructions_txt = saved_instructions_txt 
        MainMenu()   

    def configure_and_play(self):
        #stranka s konfiguracemi a moznosti spustit samotnou simulaci
        running = True
        save_txt = self.instructions_txt
        self.instructions_txt = "ESC=ukoncit ENTER=potvrdit P_SIPKA=zvysit hodnotu L_SIPKA=snizit hodnotu "
        pckr_zp = NumberPicker(200, 1, 500, 10)
        pckr_ur = NumberPicker(90, 1, 99, 1)
        pckr_sp = NumberPicker(15, 1, 100, 1)
        pckr_up = NumberPicker(15, 1, 100, 1)
        pckr_vek = NumberPicker(100, 1 , 500, 1)
        pckr_sex = NumberPicker(30, 0, 100, 1)
        pckr_jid = NumberPicker(25, 0, 200, 5)
        choices = [
            ['ZACATECNI POPULACE: ',None, pckr_zp],
            ['URODNOST: ', None, pckr_ur],
            ['LAVOVYCH POLICEK: ', None, pckr_sp],
            ['URODNYCH POLICEK: ', None, pckr_up],
            ['VEK DOSPELEHO ZUVAKA: ', None, pckr_vek],
            ['NAKLADNOST SEXU (energie):  ', None, pckr_sex],
            ['ENERGICNOST JIDLA: ', None, pckr_jid],
            ["[-SPUSTIT-]", self.launch_game, ]]  
        saved_font_size = self.font_size
        saved_first_banner_off = self.first_banner_off 
        saved_banner_off = self.banner_off
        self.banner_off = 0.06
        self.first_banner_off = 0.3
        self.set_font_size(20)
        self.set_choices(choices)
        self.update()
        while running:
            for event in p.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == p.KEYDOWN:
                    if event.key == p.K_ESCAPE:
                        running = False
                    if event.key == p.K_UP:
                        self.update_pointer(-1)
                    if event.key == p.K_DOWN:
                        self.update_pointer(1) 
                    if event.key == 13: #enter
                        if self.choices[self.active_index][1] != None:
                            update_conf_val('startPopulation', pckr_zp.get_value())
                            update_conf_val('fertility', pckr_ur.get_value())
                            update_conf_val('numberOfDangerFields', pckr_sp.get_value())
                            update_conf_val('numberOfFertileFields', pckr_up.get_value())
                            update_conf_val('zuvak', pckr_sex.get_value(), 'sexEnergyReq')
                            update_conf_val('zuvak', pckr_vek.get_value(), 'adultAge')
                            update_conf_val('fertility', 100-pckr_ur.get_value())
                            update_conf_val('food',[pckr_jid.get_value(),pckr_jid.get_value()], 'energyRange')
                            f = self.choices[self.active_index][1]
                            f()
                    if event.key == p.K_RIGHT:
                        picker_obj = self.choices[self.active_index][2]
                        picker_obj.next()
                    if event.key == p.K_LEFT:
                        picker_obj = self.choices[self.active_index][2]
                        picker_obj.prev()
                    self.update()            
            self.clock.tick(self.fps)  
            p.display.update() 
            
        self.set_font_size(saved_font_size) 
        self.active_index = 0
        self.first_banner_off = saved_first_banner_off 
        self.banner_off = saved_banner_off 
        self.instructions_txt = save_txt 
        
    def launch_game(self):
        Manager()   
        MainMenu()   

if __name__ ==  '__main__':
    MainMenu()   