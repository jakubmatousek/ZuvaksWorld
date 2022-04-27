import glob
import multiprocessing
from customErrors import WorkerError
import time
from probabilityTools import * 
from matrixTools import pos_of_wrapping_points_list_format
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os
from PIL import Image, ImageDraw

class WorkerWMag():

    def __init__(self,init_state,batch_size, task, args = None):
        self.mag = list()

        if not callable(task):
            msg = 'not a valid task supplied'
            raise WorkerError(msg)

        self.batch_size = batch_size
        self.task = task
        self.args = args
        self.last_computed_val  = init_state
        self.compute()

    def compute(self):
        for i in range(0,self.batch_size):
            last_val = self.lastVal()

            if self.args != None:
                    fRes = self.task(last_val,*self.args)
            else:
                fRes = self.task(last_val)
            self.mag.append(fRes)

    def lastVal(self):
        if len(self.mag)!=0:
            return self.mag[-1]
        else:
            return self.last_computed_val  

    def get_batch(self):
        self.compute()
        if len(self.mag)==self.batch_size:
            self.last_computed_val = self.mag[:1]
        if len(self.mag) >= self.batch_size:
            bs = self.batch_size
        else:
            bs = len(self.mag)        
        to_ret = self.mag[:bs]
        
        self.mag = self.mag[bs:]
        return to_ret    

    def  __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )      

        
class FoodWorker():
    '''tato trida bude bezet v samostatnem vlakne a bude pracovat s sdilenymi prostredky, vypocitava pozice jidla'''
    def __init__(self,init_state, fertile_tiles, shared_q, fps, stock_for_s):

        #--osetreni vstupu
        if type(shared_q) != multiprocessing.queues.Queue:
            m = 'must supply a valid multiprocessing queue'
            raise ValueError(m)
        assert fps > 0 and fps < 1000, 'fps musi splnovat: fps > 0 and fps < 1000'    
        assert type(fertile_tiles) == list
        #--osetreni vstupu

        self.max_usage = stock_for_s * fps # kolik maximalne muze odebrat jine vlakno vypocitanych hodnot
        self.fps = fps
        self.food_pos = init_state
        self.shared_q = shared_q
        self.calc_times = list()
        self.calc_times_stored = 15
        self.advance_koef = 0.5 
        self.t1 = 0
        self.fertile_tiles = fertile_tiles
        self.stock_for_s = stock_for_s

    def start_timer(self):
        self.t1 = time.time()

    def end_timer(self):
        t2 = time.time()
        diff = t2 - self.t1         
        self.calc_times.append(diff)
        if len(self.calc_times) > self.calc_times_stored:
            self.calc_times.pop(0)

    def calculate_advance_koef(self,generated):
        citatel = 0
        for t in self.calc_times:
            citatel += t
        jmenovatel = len(self.calc_times)
        avg_time = citatel / jmenovatel
        o = generated * avg_time 
        return  o

    def start(self):
        while 1:
            qs = self.shared_q.qsize()
            to_generate = self.max_usage-qs
            for i in range(to_generate):
                self.start_timer()
                self.food_pos = []
                #--
                for fertileTile in self.fertile_tiles:
                    fPos = [fertileTile.pos.x,fertileTile.pos.y]
                    doGenerate = decideBasedOnProbability(fertileTile.fertility*0.05)
                    if doGenerate:
                        #rndFoodObj = random.choice(self.food_sprites)
                        self.food_pos.append(fPos)
                self.shared_q.put(self.food_pos) 
                #--
                self.end_timer()
            nap_time = self.calculate_advance_koef(to_generate)
            time.sleep(self.stock_for_s/5)
             
    def  __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )                 



class ZuvaksWorker(): # dodelat
    '''tato trida vypocitava kam se pohnou zuvaci v pristim kole, rozdeli praci na vice vlaken a nasledne vysledky spoji a posle hlavnimu vlaknu'''

    sub_workers_count  = 5
    
    def __init__(self,deaths_births, next_positions, danger_tiles, matrix_dimensions):
        assert type(deaths_births) == multiprocessing.queues.Queue, f"argument deaths_births musi byt typu queue"
        assert type(zuvak_positions) == multiprocessing.queues.Queue, f"argument zuvak_positions musi byt typu queue"
        assert type(danger_tiles) == list, f"danger_tiles musi byt typu list a nesmi byt prazdny"
        assert matrix_dimensions[0] > 1 and matrix_dimensions[1] > 1, 'neplatne rozmery matice' 

        x,y = matrix_dimensions
        self.size_x = x
        self.size_y = y
        self.danger_tiles = danger_tiles
        self.next_positions = next_positions # shared Q
        self.deaths_births = deaths_births 
        self.zuvak_positions = list() # shared Q
        self.start()

    def start(self):
        while True:    
            d_b = self.deaths_births.get()
            if len(d_b['deaths']) > 0:
                for dead_zuvak in d_b['deaths']:
                    self.zuvak_positions.remove(dead_zuvak)
            if len(d_b['births']) > 0:
                for born_zuvak in d_b['births']:
                    self.zuvak_positions.append(born_zuvak)
            pool = multiprocessing.Pool()
            mapped_new_positins = pool.map(self.get_next_move, range(10))                  



    def divide_work(self):
        obj_c = len(self.new_pos)
        segments = list()
        segmentFormat = { "from": None, "to": None }
        sgmt_size  = obj_c // self.sub_workers_count
        rest = obj_c % self.sub_workers_count
        #if obj_c =< self.sub_workers_count
        for i in range(self.sub_workers_count):
            sgmt = segmentFormat.copy()
            frm  = i*sgmt_size
            to = (i+1) * sgmt_size - 1
            if i == self.sub_workers_count-1:
                to = to + rest
            sgmt['from'] = frm
            sgmt['to'] = to
            segments.append(sgmt)
        return segments

    def sub_worker_task(self):
        pass



    def get_next_move(self, current_pos, avoid_danger = False):
        wrapping_points = pos_of_wrapping_points_list_format(self.size_x,self.size_y,current_pos,1)
        if avoid_danger:
            for wp in wrapping_points:
                if wp in self.danger_tiles:
                    wrapping_points.remove(wp)            
        return random.choice(wrapping_points)             




class GraphMaker():

    def __init__(self, shared_q, shared_op_q, size):
        self.shared_q = shared_q
        self.shared_op_q = shared_op_q
        self.saved_data = [[0,0,0]]
        self.graph_disp_batches = 50
        self.g_path = 'graphs/*'
        self.size = size 
        files = glob.glob(self.g_path)
        for f in files:
            os.remove(f)
        border_size = 8
        self.border_color = (255,255,255)    
        w = int(size * 5/4)  
        h = size    
        self.rect_shape_btm = (
            (0,h-border_size),
            (w,h)
        )
        self.rect_shape_left = (
            (0,0),
            (border_size,h)
        )
        self.rect_shape_top = (
            (0,0),
            (w,border_size)
        )    

    def start(self):
        while 1:
            batch = self.shared_q.get()
            data_avgs = [0,0,0]
            for ds in batch:
                data_avgs[0] = data_avgs[0] + ds[0]
                data_avgs[1] = data_avgs[1] + ds[1] 
                data_avgs[2] = data_avgs[2] + ds[2]
            number_of_els = len(batch)    
            for x in range(3):
                data_avgs[x] = data_avgs[x] / number_of_els
            if self.graph_disp_batches == len(self.saved_data):
                self.saved_data.pop(0)
            self.saved_data.append(data_avgs)   
            df = pd.DataFrame(self.saved_data,
                    columns =[ 'IQ',
                               'VELIKOST',
                               'AGRESIVITA']
                    , dtype = float
                    )   
            matplotlib.style.use('dark_background')
            df.plot( linewidth=3,  linestyle="-", grid=True, xticks=())
            fls = glob.glob(self.g_path)
            name = 'graphs/' + str(len(fls))+'.png'
            plt.savefig(name)
            plt.close()
            with Image.open(name) as im:
                (width, height) = (im.width // 2, im.height // 2)
                im_resized = im.resize((int(self.size*5/4),self.size))
                draw = ImageDraw.Draw(im_resized)  
                draw.rectangle(self.rect_shape_top, fill=self.border_color)
                draw.rectangle(self.rect_shape_btm, fill=self.border_color)
                draw.rectangle(self.rect_shape_left, fill=self.border_color)
            self.shared_op_q.put(
                im_resized
            )
            os.remove(name)    



if __name__ == '__main__':
    # testing class
    zw = ZuvaksWorker(None,[1]*5)
    zw.divide_work()
    print(zw.divide_work())



