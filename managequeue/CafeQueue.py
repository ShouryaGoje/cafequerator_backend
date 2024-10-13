from datetime import datetime

class CafeQueue():
    def __init__(self):
        self.myQueue = {}
    
    def add(self, table_no, track_name, time):
        try:
            self.myQueue[table_no] += [(track_name, time)]
        except KeyError:
            self.myQueue[table_no] = [(track_name, time)]

    def getqueue(self):
        # Flatten the dictionary into a list of tuples (table_no, track_name, time)
        flattened_queue = [(table_no, track_name, time) for table_no, tracks in self.myQueue.items() for track_name, time in tracks]
        
        # Sort by table_no first, then by time
        sorted_queue = sorted(flattened_queue, key=lambda x: (x[2], x[0]))
        
        return sorted_queue

if __name__ == '__main__':
    c = CafeQueue()

    c.add(3, 'test1', datetime.now())
    c.add(3, 'test2', datetime.now())
    c.add(3, 'test3', datetime.now())
    c.add(1, 'test1', datetime.now())

    print('Testing :', c.getqueue())
