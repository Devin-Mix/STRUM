from pyaudio import PyAudio


# Generic class for holding functions shared by both input and output interfaces
class AudioInterface(PyAudio):
    def __init__(self):
        super().__init__()

        # Public attribute for unique device names available to PyAudio
        device_names = []
        for ii in range(self.get_device_count()):
            ii_device_info = self.get_device_info_by_index(ii)
            if not ii_device_info["name"] in device_names:
                device_names.append(ii_device_info["name"])

    # Find device whose name matches device_name with lowest input latency
    def get_lowest_latency_instance(self, device_name):
        if not type(device_name) == str:
            raise (TypeError("Invalid argument type for AudioInterface.get_lowest_latency_instance (expected str"
                             ", got {})".format(type(device_name))))
        else:
            minimum_device_latency = float("inf")
            target_device_info = None
            for ii in range(self.get_device_count()):
                ii_device_info = self.get_device_info_by_index(ii)
                if ii_device_info["name"] == device_name and ii_device_info[
                        "defaultLowInputLatency"] < minimum_device_latency:
                    minimum_device_latency = ii_device_info["defaultLowInputLatency"]
                    target_device_info = ii_device_info
            return target_device_info
