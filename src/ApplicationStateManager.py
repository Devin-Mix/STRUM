from ConfigurationStateManager import ConfigurationStateManager
from GUIEventBroker import GUIEventBroker
from RecordingStateManager import RecordingStateManager
from Message import Message
from pygame import QUIT
from queue import Queue

# Should contain the classes of all processes to be launched
# Python treats classes like objects themselves, so just load them up here
process_classes = {"ConfigurationStateManager": ConfigurationStateManager,
                   "GUIEventBroker": GUIEventBroker,
                   "RecordingStateManager": RecordingStateManager}


# Main function of the application state manager
# All functionality (launching state-specific managers/GUI event broker, querying messages, etc.) should go here
def main():
    # Create dictionary mapping classes to their respective queues
    outgoing_process_queues = {}
    incoming_process_queues = {}
    for class_needing_queue in process_classes.values():
        outgoing_process_queues[class_needing_queue] = Queue()
        incoming_process_queues[class_needing_queue] = Queue()

    # Create objects from sub-process classes and initialize with their incoming and outgoing queues
    # Each sub-process class should accept two arguments in its __init__:
    # - A manager.Queue incoming_queue that provides messages from this ASM and corresponds with the ASM's outgoing
    # - A manager.Queue outgoing_queue that is used to send messages to the ASM and corresponds with its incoming
    process_objects = {}
    for class_needing_init in process_classes.values():
        process_objects[class_needing_init] = class_needing_init(
            incoming_queue=outgoing_process_queues[class_needing_init],
            outgoing_queue=incoming_process_queues[class_needing_init])

    # All processes are now launched. The "processes" dictionary can be queried for the results of a process
    # Values of the "processes" dictionary are multiprocessing.pool.AsyncResult objects

    # TODO: A message should be queued here for the title screen state manager in order to start the application's
    #  interaction process. For now, this can be used for debugging.
    incoming_process_queues[GUIEventBroker].put(Message(target="RecordingStateManager",
                                                        source="GUIEventBroker",  # A little lying never hurt
                                                        message_type="Start Recording",
                                                        content={"tab_file": "../test/TabParseTest.txt"}))

    # Main loop of the ASM. Should involve checking individual processes' queues and responding to/forwarding messages
    while True:
        for class_needing_check in process_classes.values():
            # Get all messages in the incoming queue for the class
            while not incoming_process_queues[class_needing_check].empty():
                # Get the message at the head of the queue
                message = incoming_process_queues[class_needing_check].get()
                # Pass along and handle the message itself here
                outgoing_process_queues[process_classes[message.target]].put(message)
                process_objects[process_classes[message.target]].handle()


# Automatically run main() if script is run on its own (intended behavior)
if __name__ == "__main__":
    main()
