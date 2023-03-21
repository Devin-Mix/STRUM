from Message import Message
from queue import Queue
from Renderables import *
from Tab import Tab
from time import time


class RecordingStateManager:
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
            self.current_tab = None
            self.fret_count = None
            self.recording_fall_time = None
            self.recording_vertical_scale = None
            self.start_time = None
            self.final_fret_offset = None
            self.last_render_time = None
            self.fading_chords = []
            self.now_time = None
            self.playback_started = None
            self.playback_start_time = None

    def handle(self):
        if not self.incoming_queue.empty():
            message = self.incoming_queue.get()
            if message.type == "Start Recording":
                # TODO: Tell GUI event broker to start recording and playback (need to know how audio is going to work
                #  to do this)
                tab_file = message.content["tab_file"]
                self.current_tab = Tab(tab_file)
                self.start_time = time()
                self.playback_started = False
                self.outgoing_queue.put(Message(target="ConfigurationStateManager",
                                                source="RecordingStateManager",
                                                message_type="Get fret count",
                                                content=None))
            elif message.type == "Fret count":
                self.fret_count = message.content
                self.final_fret_offset = self.get_final_fret_offset()
                self.outgoing_queue.put(Message(target="ConfigurationStateManager",
                                                source="RecordingStateManager",
                                                message_type="Get recording vertical scale",
                                                content=None))
            elif message.type == "Recording vertical scale":
                self.recording_vertical_scale = message.content
                self.outgoing_queue.put(Message(target="ConfigurationStateManager",
                                                source="RecordingStateManager",
                                                message_type="Get recording fall time",
                                                content=None))
            elif message.type == "Recording fall time":
                self.recording_fall_time = message.content
                to_draw = self.get_string_lines() + self.get_fret_lines()
                self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                source="RecordingStateManager",
                                                message_type="render",
                                                content=to_draw))
            elif message.type == "Get GUI update":
                if self.now_time is not None and self.now_time >= self.current_tab.get_next_chords(0.0)[-1][1] + \
                        self.current_tab.get_next_chords(0.0)[-1][2]:
                    self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                    source="RecordingStateManager",
                                                    message_type="Quit",
                                                    content=None))
                    pass
                else:
                    self.now_time = time() - self.start_time
                    fading_chords = self.get_fading_chords()
                    if not self.playback_started and not len(fading_chords) == 0:
                        self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                        source="RecordingStateManager",
                                                        message_type="Start playback",
                                                        content=self.current_tab.song_file))
                        self.playback_started = True
                        self.playback_start_time = self.now_time
                    self.fading_chords = self.fading_chords + self.get_fading_chords()
                    self.fading_chords = [ii.update_time(self.now_time) for ii in self.fading_chords]
                    self.fading_chords = [ii for ii in self.fading_chords if ii.is_alive()]
                    to_draw = self.get_string_lines() + self.get_fret_lines() + self.get_falling_chords() + \
                        self.fading_chords
                    if self.playback_started:
                        self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                        source="RecordingStateManager",
                                                        message_type="Update playback",
                                                        content=self.now_time - self.playback_start_time))
                    self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                    source="RecordingStateManager",
                                                    message_type="render",
                                                    content=to_draw))
                    self.last_render_time = self.now_time

    def get_string_lines(self):
        res = []
        for ii in range(6):
            res.append(StringLine(95, 95 - (5 * ii * self.recording_vertical_scale)))
        return res

    def get_final_fret_offset(self):
        offset = 0.0
        for ii in range(0, self.fret_count):
            offset = ((95.0 - offset) / 17.817) + offset
        return offset

    def get_fret_lines(self):
        res = []
        offset = 0.0
        for ii in range(0, self.fret_count):
            offset = ((95.0 - offset) / 17.817) + offset
            res.append(offset)
        res = [95.0 * ii / self.final_fret_offset for ii in res]
        res = [FretLine(ii + 2.5, 25.0 * self.recording_vertical_scale) for ii in res]
        return res

    def get_falling_chords(self):
        next_chords = [ii for ii in self.current_tab.get_next_chords(self.now_time)
                       if ii[1] < self.now_time + self.recording_fall_time]
        res = []
        for ii in next_chords:
            remaining_fall_time = ii[1] - self.now_time
            y_offset = (95 - (25 * self.recording_vertical_scale)) - ((90 - (25 * self.recording_vertical_scale)) *
                                                                      remaining_fall_time / self.recording_fall_time)
            for jj in range(6):
                res.append(StringLine(95, y_offset + jj * 5 * self.recording_vertical_scale))
            for string_number in range(len(ii[0].play_string)):
                if ii[0].play_string[string_number]:
                    fret_number = ii[0].string_fret[string_number]
                    fret_offset = 0.0
                    for kk in range(fret_number):
                        fret_offset = ((95.0 - fret_offset) / 17.817) + fret_offset
                    fret_offset = 2.5 + (95 * fret_offset / self.final_fret_offset)
                    res.append(FretMark(fret_offset, y_offset + (5 - string_number) * 5 *
                                        self.recording_vertical_scale))
        return res

    def get_fading_chords(self):
        res = []
        if self.last_render_time is not None:
            last_chords = self.current_tab.get_next_chords(self.last_render_time)
            now_chords = self.current_tab.get_next_chords(self.now_time)
            if len(now_chords) > 0 and now_chords[0] in last_chords:
                fade_chords = last_chords[:last_chords.index(now_chords[0])]
            else:
                fade_chords = last_chords
            y_offset = 95 - (25 * self.recording_vertical_scale)
            for fade_chord in fade_chords:
                for string_number in range(len(fade_chord[0].play_string)):
                    if fade_chord[0].play_string[string_number]:
                        fret_number = fade_chord[0].string_fret[string_number]
                        fret_offset = 0.0
                        for kk in range(fret_number):
                            fret_offset = ((95.0 - fret_offset) / 17.817) + fret_offset
                        fret_offset = 2.5 + (95 * fret_offset / self.final_fret_offset)
                        res.append(FadingFretMark(fret_offset,
                                                  y_offset + (5 - string_number) * 5 * self.recording_vertical_scale,
                                                  fade_chord[1], fade_chord[2], self.now_time))
        return res
