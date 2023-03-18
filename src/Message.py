# Defines messages to be exchanged between processes
class Message:
    def __init__(self, message_type, content):
        # Defines types of messages to be exchanged
        self.valid_types = []

        if message_type in self.valid_types:
            self.type = message_type
        else:
            raise TypeError("Invalid message type")

        self.content = content