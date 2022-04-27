class NumberPicker():
    '''nastroj pro vyber ciselne hodnoty. Pouzito v hlavnim menu'''
    def __init__(self,default, from_n, to_n, step):
        self.current = default
        self.from_n = from_n
        self.to_n = to_n
        self.step = step
    def next(self):
        if self.step + self.current > self.to_n:
            self.current = self.from_n-1
        self.current = self.current + self.step

    def prev(self):
        if self.current - self.step <  self.from_n:
            self.current = self.to_n
        self.current = self.current - self.step

    def get_value(self):
        return self.current   
    
    def  __str__(self):
        return str(self.current)


class ResolutionPicker():
    '''nastroj pro vyber rozliseni. Pouzito v hlavnim menu'''
    def __init__(self):
        choices = [
            '750x750',
            '750x1000',
            '1000x1000',
            '1920x1080'
        ]
        self.current = 0 
        self.choices = choices        

    def next(self):
        if self.current == len(self.choices) - 1:
            self.current = 0
        else:
            self.current = self.current + 1

    def prev(self):
        if self.current == 0:
            self.current = len(self.choices) - 1
        else:
            self.current -= 1

    def get_value(self):
        str = self.choices[self.current]
        x = int(str.split('x')[0])
        y = int(str.split('x')[1])
        return (x,y)

    def __str__(self) -> str:
        return self.choices[self.current]    

class BoolPicker(NumberPicker):
    '''nastroj pro vyber hodnoty bitu. Pouzito v hlavnim menu'''
    
    def __init__(self, default = 0):
        frm = 0
        to =  1
        step = 1
        super().__init__(default, frm, to, step)

    def __str__(self):
        if self.current == 1:
            return 'ANO'
        else:
            return 'NE'
