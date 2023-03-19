from Message import Message
from queue import Queue
from Renderables import *
from Tab import Tab
from time import time

class RecordingStateManager:
    def __init__(self, incoming_queue, outgoing_queue):
        if not isinstance(incoming_queue, Queue):
            raise TypeError("Invalid incoming_queue type for RecordingStateManager (expected managers.BaseProxy, got {})".
                            format(type(incoming_queue)))
        elif not isinstance(outgoing_queue, Queue):
            raise TypeError("Invalid outgoing_queue type for RecordingStateManager (expected managers.BaseProxy, got {})"
                            .format(type(incoming_queue)))
        else:
            self.incoming_queue = incoming_queue
            self.outgoing_queue = outgoing_queue
            self.current_tab = None
            self.start_time = None

    def handle(self):
        if not self.incoming_queue.empty():
            message = self.incoming_queue.get()
            if message.type == "Start Recording":
#                tab_file = message.content["tab_file"]
#                self.current_tab = Tab(tab_file)
                self.start_time = time()
                #TODO: Send first batch of GUI output to GUI event broker and begin recording (need to know what GUI event broker expects before implementing this)
                to_draw = [StringLine(95, 95), StringLine(90, 90), StringLine(85, 85), StringLine(80, 80)]
                self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                source="RecordingStateManager",
                                                message_type="render",
                                                content=to_draw))
            elif message.type == "Get GUI update":
                now_time = time() - self.start_time
#                next_chords = self.current_tab.get_next_chords(now_time)
                #TODO: This may cause playback to end prematurely. Investigate.
                if False: #len(next_chords) == 0:
                    #TODO: Signal that song is over and end recording
                    pass
                else:
                    #TODO: Send current batch of GUI output to GUI event broker (need to know what GUI event broker expects before implementing this)
                    to_draw = [StringLine(95, 95), StringLine(90, 90), StringLine(85, 85), StringLine(80, 80)]
                    self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                    source="RecordingStateManager",
                                                    message_type="render",
                                                    content=to_draw))