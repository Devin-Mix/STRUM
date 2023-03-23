from Message import Message
from queue import Queue
from Renderables import *
from time import sleep

class AnalysisStateManager:
    def __init__(self, incoming_queue, outgoing_queue):
        if not isinstance(incoming_queue, Queue):
            raise TypeError("Invalid incoming_queue type for RecordingStateManager (expected queue.Queue, got {})".
                            format(type(incoming_queue)))
        elif not isinstance(outgoing_queue, Queue):
            raise TypeError("Invalid outgoing_queue type for RecordingStateManager (expected queue.Queue, got {})"
                            .format(type(incoming_queue)))
        else:
            self.incoming_queue = incoming_queue
            self.outgoing_queue = outgoing_queue
            self.input_latency = None
            self.recording_data = None
            self.recording_start_time = None
            self.playback_start_time = None
            self.tone_wave = None
            self.load_percent = None

    def handle(self):
        if not self.incoming_queue.empty():
            message = self.incoming_queue.get()
            if message.type == "Start analysis":
                self.input_latency = message.content["latency"]
                self.recording_data = message.content["data"]
                self.recording_start_time = message.content["recording_start_time"]
                self.playback_start_time = message.content["playback_start_time"]
                self.tone_wave = message.content["tone_wave"]
                self.load_percent = 0.0
                print("Input latency: {}, Input start time: {}, Output start time: {}".format(self.input_latency, self.recording_start_time, self.playback_start_time))
                self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                source="AnalysisStateManager",
                                                message_type="render",
                                                content=[LoadBar(45.0, 95.0, 10.0, self.load_percent)]))

            if message.type == "Get GUI update":
                self.load_percent = self.load_percent + 1.0
                sleep(0.5)
                if self.load_percent >= 100.0:
                    self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                    source="AnalysisStateManager",
                                                    message_type="Quit",
                                                    content=None))
                else:
                    self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                    source="AnalysisStateManager",
                                                    message_type="render",
                                                    content=[LoadBar(45.0, 95.0, 10.0, self.load_percent)]))