import pygame, Renderables
from Message import Message
from queue import Queue


class GUIEventBroker:
    def __init__(self, incoming_queue, outgoing_queue):
        if not isinstance(incoming_queue, Queue):
            raise TypeError("Invalid incoming_queue type for GUIEventBroker (expected queue.Queue, got {})".
                            format(type(incoming_queue)))
        elif not isinstance(outgoing_queue, Queue):
            raise TypeError("Invalid outgoing_queue type for GUIEventBroker (expected queue.Queue, got {})"
                            .format(type(incoming_queue)))
        else:
            self.incoming_queue = incoming_queue
            self.outgoing_queue = outgoing_queue

            # TODO: Replace with configuration from either a file or another state manager
            # A default set of config values could potentially be used in lieu of "real" values as well
            self.config = {"resolution": (640, 480),
                           "background color": "blue"}
            self.current_source = None

            pygame.init()
            self.screen = pygame.display.set_mode(self.config["resolution"])
            pygame.display.set_caption("S.T.R.U.M.")

    def handle(self):
        if not self.incoming_queue.empty():
            message = self.incoming_queue.get()
            if message.type == "render":
                self.current_source = message.source
                self.screen.fill(self.config["background color"])
                # GUI event broker expects a list of Renderable objects in message content
                # Objects should be provided in the order in which they should be rendered
                for render_object in message.content:
                    if not type(render_object) in Renderables.available:
                        raise TypeError("Invalid render object type (got {})".format(type(render_object)))
                    else:
                        render_object.draw(self.screen)
                pygame.display.flip()
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        pygame.quit()
                self.outgoing_queue.put(Message(target=self.current_source,
                                                source="GUIEventBroker",
                                                message_type="Get GUI update",
                                                content=events))