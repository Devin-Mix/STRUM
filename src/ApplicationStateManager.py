from RecordingStateManager import RecordingStateManager

from multiprocessing import Pool, SimpleQueue


class ApplicationStateManager:
    # Should contain the classes of all processes to be launched
    # Python treats classes like objects themselves, so just load them up here
    process_classes = [RecordingStateManager]

# Main function of the application state manager
# All functionality (launching state-specific managers/GUI event broker, querying messages, etc.) should go here
def main():
    # Create dictionary mapping classes of sub-processes to their respective queues
    outgoing_process_queues = {}
    incoming_process_queues = {}
    for class_needing_queue in ApplicationStateManager.process_classes:
        outgoing_process_queues[class_needing_queue] = SimpleQueue()
        incoming_process_queues[class_needing_queue] = SimpleQueue()

    # Create objects from sub-process classes and initialize with their incoming and outgoing queues
    # Each sub-process class should accept two arguments in its __init__:
    # - A SimpleQueue incoming_queue that provides messages from this ASM and corresponds with the ASM's outgoing
    # - A SimpleQueue outgoing_queue that is used to send messages to the ASM and corresponds with its incoming
    process_objects = {}
    for class_needing_init in ApplicationStateManager.process_classes:
        process_objects[class_needing_init] = class_needing_init(
            incoming_queue=outgoing_process_queues[class_needing_init],
            outgoing_queue=incoming_process_queues[class_needing_init])

    # Create multiprocessing pool with number of processes equal to the number of process classes to be launched
    pool = Pool(processes=len(ApplicationStateManager.process_classes))

    # Create dictionary mapping classes of sub-processes to the processes themselves (to be populated later)
    processes = {}

    # Launch individual processes
    # Each class to be launched should contain a main() method to be run by its process. main() should take no arguments
    for class_needing_launch in ApplicationStateManager.process_classes:
        processes[class_needing_launch] = pool.apply_async(process_objects[class_needing_launch].main)

    # All processes are now launched. The "processes" dictionary can be queried for the results of a process
    # Values of the "processes" dictionary are multiprocessing.pool.AsyncResult objects

    #TODO: A message should be queued here for the title screen state manager in order to start the application's interaction process

    # Main loop of the ASM. Should involve checking individual processes' queues and responding to/forwarding messages
    while True:
        for class_needing_check in ApplicationStateManager.process_classes:
            # Check if sub-process has died or not.
            # ValueError is raised if the process is still running. This is intended behavior.
            try:
                processes[class_needing_check].successful()
                # Assume process is dead. Error handling should occur here.
                # If the process died due to an exception, processes[class_needing_check].get() will return it
            except ValueError:
                # Assume process is live. No error handling needed.
                # Get all messages in the incoming queue for the process
                while not incoming_process_queues[class_needing_check].empty():
                    # Get the message at the head of the queue
                    message = incoming_process_queues[class_needing_check].get()
                    # Handle the message itself here
                    outgoing_process_queues[message.target].put(message)

# Automatically run main() if script is run on its own (intended behavior)
if __name__ == "__main__":
    main()