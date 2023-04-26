# Should contain the names of the classes of all processes to be launched as strings
# This is essentially a duplicated version of ApplicationStateManager.process_classes.keys(), but is included to prevent
# a circular dependency issue.
process_class_keys = ["AnalysisStateManager", "ConfigurationStateManager", "GUIEventBroker", "RecordingStateManager", "SongSelectStateManager", "TitleScreenStateManager"]


# Defines messages to be exchanged between processes
class Message:
    def __init__(self, target, source, message_type, content):
        # Defines types of messages to be exchanged
        self.valid_types = ["Config",
                            "End recording",
                            "Fret count",
                            "Get config",
                            "Get GUI update",
                            "Prime playback",
                            "Prime recording",
                            "Quit",
                            "render",
                            "Send recording",
                            "Start analysis",
                            "Start playback",
                            "Start recording",
                            "Start recording session",
                            "Toggle fullscreen",
                            "Update playback"]

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
