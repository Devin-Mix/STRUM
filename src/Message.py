from ApplicationStateManager import ApplicationStateManager

# Defines messages to be exchanged between processes
class Message:
    def __init__(self, target, message_type, content):
        # Defines types of messages to be exchanged
        self.valid_types = []

        # Type checking ensures that every message has a type
        if message_type in self.valid_types:
            self.type = message_type
        else:
            raise ValueError("Invalid message type")

        # Target checking ensures that messages are properly routed
        if target in ApplicationStateManager.process_classes:
            self.target = target
        else:
            raise ValueError("Invalid message target")

        # Content is optional
        self.content = content