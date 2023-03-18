from multiprocessing import queues

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