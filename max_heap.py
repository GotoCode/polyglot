#
# max heap data structure
#

import heapq

class MaxHeap(object):

    def __init__(self):

        self.items = []
        self.top = None

    def push(self, k, v):

        heapq.heappush(self.items, (-k, v))
        
        self.top = self.items[0]

    def pop(self):

        if len(self.items) > 0:

            k, v = heapq.heappop(self.items)
            
            self.top = self.items[0]

            return (-k, v)

        return None
