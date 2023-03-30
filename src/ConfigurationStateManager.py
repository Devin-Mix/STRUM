import pygame
from Message import Message
from queue import Queue


class ConfigurationStateManager:
    def __init__(self, incoming_queue, outgoing_queue):
        if not isinstance(incoming_queue, Queue):
            raise TypeError(
                "Invalid incoming_queue type for ConfigurationStateManager (expected queue.Queue, got {})".
                format(type(incoming_queue)))
        elif not isinstance(outgoing_queue, Queue):
            raise TypeError(
                "Invalid outgoing_queue type for ConfigurationStateManager (expected queue.Queue, got {})"
                .format(type(incoming_queue)))
        else:
            self.incoming_queue = incoming_queue
            self.outgoing_queue = outgoing_queue
            # These defaults are arbitrary and should be better specified elsewhere
            self.resolution = (640, 480)
            self.recording_vertical_scale = 0.5
            self.fret_count = 30
            self.recording_fall_time = 1.0
            self.chroma_key = pygame.color.Color(50, 50, 50)
            self.hue = 39
            self.outgoing_queue.put(Message(target="GUIEventBroker",
                                            source="ConfigurationStateManager",
                                            message_type="Config",
                                            content=self))

    def handle(self):
        if not self.incoming_queue.empty():
            message = self.incoming_queue.get()
            if message.type == "Get config":
                self.outgoing_queue.put(Message(target=message.source,
                                                source="ConfigurationStateManager",
                                                message_type="Config",
                                                content=self))