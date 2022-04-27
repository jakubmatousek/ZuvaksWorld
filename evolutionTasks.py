from probabilityTools import * 
'''v tomto souboru skladuji dodatecne metody pro modul evolution.py'''



def kill_zuvak(self,pos):
    '''metoda pro ostraneni zuvaka z mapy'''
    try:
        pos = [
            int(pos[0]/self.tileSize),
            int(pos[1]/self.tileSize)
            ]
        zuvaks_on_pos = self.grid[pos[0]][pos[1]]
        fought = False
        to_be_killed_index = None
        if len(zuvaks_on_pos) > 0:
            for i in range(len(zuvaks_on_pos)):
                zuvak = zuvaks_on_pos[i]
                if zuvak.being_attacked or zuvak.in_fight: 
                    fought = True
                    to_be_killed_index = i
                    break
        if not fought:
            print(pos)
            zuvaks_on_pos = self.gridUpdated[pos[0]][pos[1]]
            for i in range(len(zuvaks_on_pos)):
                zuvak = self.gridUpdated[pos[0]][pos[1]][i]
                if zuvak.in_fight or zuvak.being_attacked:
                    to_be_killed_index = i
                    fought = True
                    break
            del self.gridUpdated[pos[0]][pos[1]][to_be_killed_index]
            if len(self.gridUpdated[pos[0]][pos[1]]) == 1:
                self.populationPositionsUpdated.remove(pos)
        else:
            del self.grid[pos[0]][pos[1]][to_be_killed_index]
            if len(self.grid[pos[0]][pos[1]]) == 1:
                self.populationPositions.remove(
                    pos
                    )          
    except Exception as e:
        pass

def kill_zuvak_w_obj(self,pos,zuvak_obj):
    '''metoda pro ostraneni zuvaka z mapy pomoci porovnavani objektu'''
    try:
        assert pos in self.populationPositions
        objs_on_tile = self.grid[pos[0]][pos[1]]
        numer_of_objs_on_tile = len(objs_on_tile)
        if numer_of_objs_on_tile == 1:
            self.populationPositions.remove(
                pos
                )
        else:
            self.grid[pos[0]][pos[1]].remove(zuvak_obj)    
    except:
        assert pos in self.populationPositionsUpdated
        objs_on_tile = self.gridUpdated[pos[0]][pos[1]]
        numer_of_objs_on_tile = len(objs_on_tile)
        if numer_of_objs_on_tile == 1:
            self.populationPositionsUpdated.remove(pos)
        else:
            self.grid[pos[0]][pos[1]].remove(zuvak_obj)