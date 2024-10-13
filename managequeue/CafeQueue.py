import copy

class CafeQueue():
    def __init__(self):
        self.myQueue = {}
    
    def add(self, table_no, track_name, track_id, time):
        try:
            self.myQueue[table_no] += [(track_name, track_id, time)]
        except KeyError:
            self.myQueue[table_no] = [(track_name, track_id, time)]

    def getqueue(self):
        dit = self.myQueue
        lst = []
        while dit:  
            lst += sorted([(table_no, enl.pop(0)) for table_no, enl in dit.items() if enl], key=lambda x: x[1][2])
            dit = {table_no: enl for table_no, enl in dit.items() if enl}
        
        return [(i[0], i[1][0], i[1][1])for i in lst]
    def remove(self, table_no):
        self.myQueue.pop(table_no)

    def __reduce__(self):
        # This returns a tuple of the class constructor and its arguments for reconstruction
        return (self.__class__, (), copy.deepcopy(self.__dict__))






if __name__ == '__main__':
    from datetime import datetime
    import time
    c = CafeQueue()

    c.add(3, '1', datetime.now())
    time.sleep(2)
    c.add(3, '5', datetime.now())
    time.sleep(2)
    c.add(3, '8', datetime.now())
    time.sleep(2)
    c.add(1, '2', datetime.now())
    time.sleep(2)
    c.add(1, '6', datetime.now())
    time.sleep(2)
    c.add(2, '3', datetime.now())
    time.sleep(2)
    c.add(3, '11', datetime.now())
    time.sleep(2)
    c.add(1, '9', datetime.now())
    time.sleep(2)
    c.add(2, '7', datetime.now())
    time.sleep(2)
    c.add(2, '10', datetime.now())
    time.sleep(2)
    c.add(5, '4', datetime.now())
    time.sleep(2)
    c.add(3, '12', datetime.now())

    print('Testing :',c.getqueue())
