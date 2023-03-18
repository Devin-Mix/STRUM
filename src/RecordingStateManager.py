from multiprocessing import queues
from Tab import Tab
from time import time

class RecordingStateManager:
    def __init__(self, incoming_queue, outgoing_queue):
        if not type(incoming_queue) == queues.SimpleQueue:
            raise TypeError
        elif not type(outgoing_queue) == queues.SimpleQueue:
            raise TypeError
        else:
            self.incoming_queue = incoming_queue
            self.outgoing_queue = outgoing_queue

    def main(self):
        while True:
            if not self.incoming_queue.empty():
                message = self.incoming_queue.get()
                if message.type == "Start Recording":
                    tab_file = message.content["tab_file"]
                    current_tab = Tab(tab_file)
                    start_time = time()
                    #TODO: Send first batch of GUI output to GUI event broker and begin recording (need to know what GUI event broker expects before implementing this)
                elif message.type == "Get GUI update":
                    now_time = time() - start_time
                    next_chords = current_tab.get_next_chords(now_time)
                    #TODO: This may cause playback to end prematurely. Investigate.
                    if len(next_chords) == 0:
                        #TODO: Signal that song is over and end recording
                    else:
                        #TODO: Send current batch of GUI output to GUI event broker (need to know what GUI event broker expects before implementing this)