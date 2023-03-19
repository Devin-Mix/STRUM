# Should contain the names of the classes of all processes to be launched as strings
# This is essentially a duplicated version of ApplicationStateManager.process_classes.keys(), but is included to prevent
# a circular dependency issue.
process_class_keys = ["GUIEventBroker", "RecordingStateManager"]

# Defines messages to be exchanged between processes
class Message:
    def __init__(self, target, source, message_type, content):
        # Defines types of messages to be exchanged
        self.valid_types = ["Get GUI update", "render", "Start Recording"]

        # Type checking ensures that every message has a type
        if message_type in self.valid_types:
            self.type = message_type
        else:
            raise ValueError("Invalid message type")

        # Target checking ensures that messages are properly routed
        if target in process_class_keys:
            self.target = target
        else:
            raise ValueError("Invalid message target")

        if source in process_class_keys:
            self.source = source
        else:
            raise ValueError("Invalid message source")

        # Content is optional
        self.content = content