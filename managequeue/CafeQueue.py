import copy

class CafeQueue():
    def __init__(self):
        self.myQueue = {}
    
    def add(self, table_no: int, track_name: str, time: str, track_img_url: str, track_artist_name: str, track_id=0):
        """
        Adds a track to the queue for a specific table.
        """
        try:
            self.myQueue[table_no] += [(track_name, track_id, time, track_img_url, track_artist_name)]
        except KeyError:
            self.myQueue[table_no] = [(track_name, track_id, time, track_img_url, track_artist_name)]

    def getqueue(self):
        """
        Retrieves a flattened list of the queue sorted by timestamp.
        """
        dit = copy.deepcopy(self.myQueue)
        try:
            tail = dit[-1]
            dit.pop(-1)
        except Exception as e:
            pass
        lst = []
        flag = False
        while dit:
            lst += sorted(
                [(table_no, enl.pop(0)) for table_no, enl in dit.items() if enl],
                key=lambda x: x[1][2]  # Sort by time
            )
            dit = {table_no: enl for table_no, enl in dit.items() if enl}
            flag = True
        if flag:
            lst = [
                {
                    "id": i[0],
                    "track_name": i[1][0],
                    "track_id": i[1][1],
                    "timestamp": i[1][2],
                    "track_img_url": i[1][3],
                    "track_artist_name": i[1][4],
                }
                for i in lst
            ]
        try:
            for i in tail:
                lst.append({
                    "id": -1,
                    "track_name": i[0],
                    "track_id": i[1],
                    "timestamp": i[2],
                    "track_img_url": i[3],
                    "track_artist_name": i[4],
            })
        except Exception as e:
            pass
        return lst
    
    def remove(self, table_no: int):
        """
        Removes the queue for a specific table.
        """
        self.myQueue.pop(table_no, None)  # Use .pop() with a default to avoid errors
        
    def poper(self):
        """
        Removes the top track from the queue.
        """
        top_table_no = int(self.get_top()["id"])
        if self.myQueue[top_table_no]:
            self.myQueue[top_table_no].pop(0)

    def get_top(self):
        """
        Retrieves the top track from the queue.
        """
        q = self.getqueue()
        if len(q) == 0:
            return None
        return q[0]
    
    def remove_track(self,id: int, track_id: int):
        for i in self.myQueue[id]:
            if i[1] == track_id:
                self.myQueue[id].remove(i)
                return True
        return False
    def __reduce__(self):
        """
        Serialization helper for deep copying or pickling.
        """
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

    print('Testing :',c.getqueue(),  c.myQueue)
