from Message import Message
from queue import Queue
from Renderables import *
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
            self.config = None
            self.first_session_render = True
            self.doing_fade_in = False
            self.fade_in_start_time = None
            self.doing_fade_out = False
            self.fade_out_start_time = None
            self.outgoing_queue.put(Message(target="ConfigurationStateManager",
                                            source="RecordingStateManager",
                                            message_type="Get config",
                                            content=None))

    def handle(self):
        if not self.incoming_queue.empty():
            message = self.incoming_queue.get()
            if message.type == "Config":
                self.config = message.content
            elif message.type == "Start recording session":
                self.current_tab = message.content["tab_file"]
                self.playback_started = False
                self.final_fret_offset = self.get_final_fret_offset()
                to_draw = self.get_string_lines() + self.get_fret_lines()
                self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                source="RecordingStateManager",
                                                message_type="Prime playback",
                                                content={"song_file": self.current_tab.song_file,
                                                         "tab_object": self.current_tab}))
                self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                source="RecordingStateManager",
                                                message_type="Prime recording",
                                                content=None))
                to_draw.append(Blackout(0, self.config.fade_length))
                for ii in range(len(to_draw)):
                    to_draw[ii].function = no_function
                self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                source="RecordingStateManager",
                                                message_type="render",
                                                content=to_draw))
            elif message.type == "Get GUI update":
                to_draw = self.get_string_lines() + self.get_fret_lines()
                if self.first_session_render:
                    self.now_time = time()
                    self.fade_in_start_time = self.now_time
                    self.doing_fade_in = True
                    self.first_session_render = False
                if not self.doing_fade_in and not self.doing_fade_out:
                    if self.now_time is not None and self.now_time >= (1 / self.config.playback_speed_scale) * (self.current_tab.get_next_chords(0.0, self.config)[-1][1] + \
                            self.current_tab.get_next_chords(0.0, self.config)[-1][2]):
                        self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                        source="RecordingStateManager",
                                                        message_type="End recording",
                                                        content=self.current_tab))
                        self.fade_out_start_time = self.now_time
                        self.now_time = None
                        self.start_time = None
                        self.fading_chords = []
                        self.last_render_time = None
                        self.doing_fade_out = True
                    else:
                        if self.start_time is None:
                            self.start_time = time() + self.config.recording_fall_time
                        self.now_time = time() - self.start_time
                        if not self.playback_started and not len(self.current_tab.get_next_chords(self.now_time, self.config)) == len(self.current_tab.get_next_chords(0.0, self.config)):
                            self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                            source="RecordingStateManager",
                                                            message_type="Start playback",
                                                            content=None))
                            self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                            source="RecordingStateManager",
                                                            message_type="Start recording",
                                                            content=None))
                            self.playback_started = True
                            self.playback_start_time = self.now_time
                        self.fading_chords = self.fading_chords + self.get_fading_chords()
                        self.fading_chords = [ii.update_time(self.now_time) for ii in self.fading_chords]
                        self.fading_chords = [ii for ii in self.fading_chords if ii.is_alive()]
                        to_draw = to_draw + self.get_falling_chords() + \
                            self.fading_chords + [Text(2.5, 2.5, 95, 10.0, self.current_tab.title, self.config.header, align_center=False),
                                                  Text(2.5, 12.5, 95, 5.0, self.current_tab.artist, self.config.italic, align_center=False)]
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
                elif self.doing_fade_in:
                    self.now_time = time()
                    to_draw = to_draw + [Text(2.5, 2.5, 95, 10.0, self.current_tab.title, self.config.header, align_center=False),
                                              Text(2.5, 12.5, 95, 5.0, self.current_tab.artist, self.config.italic, align_center=False)]
                    to_draw.append(Blackout(self.now_time - self.fade_in_start_time, self.config.fade_length))
                    for ii in range(len(to_draw)):
                        to_draw[ii].function = no_function
                    if self.now_time - self.fade_in_start_time >= self.config.fade_length:
                        self.doing_fade_in = False
                        self.now_time = None
                    self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                    source="RecordingStateManager",
                                                    message_type="render",
                                                    content=to_draw))
                elif self.doing_fade_out:
                    self.now_time = time()
                    to_draw = to_draw + [
                        Text(2.5, 2.5, 95, 10.0, self.current_tab.title, self.config.header, align_center=False),
                        Text(2.5, 12.5, 95, 5.0, self.current_tab.artist, self.config.italic, align_center=False)]
                    to_draw.append(Blackout(self.now_time - self.fade_out_start_time, self.config.fade_length, False))
                    for ii in range(len(to_draw)):
                        to_draw[ii].function = no_function
                    if self.now_time - self.fade_out_start_time >= self.config.fade_length:
                        self.doing_fade_out = False
                        self.now_time = None
                        self.first_session_render = True
                        self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                        source="RecordingStateManager",
                                                        message_type="Send recording",
                                                        content=self.current_tab))
                    else:
                        self.outgoing_queue.put(Message(target="GUIEventBroker",
                                                        source="RecordingStateManager",
                                                        message_type="render",
                                                        content=to_draw))



    def get_string_lines(self):
        res = []
        for ii in range(6):
            res.append(StringLine(95, 95 - (5 * ii * self.config.recording_vertical_scale)))
        return res

    def get_final_fret_offset(self):
        offset = 0.0
        for ii in range(0, self.config.fret_count):
            offset = ((95.0 - offset) / 17.817) + offset
        return offset

    def get_fret_lines(self):
        res = []
        offset = 0.0
        for ii in range(0, self.config.fret_count):
            offset = ((95.0 - offset) / 17.817) + offset
            res.append(offset)
        res = [95.0 * ii / self.final_fret_offset for ii in res]
        res = [FretLine(ii + 2.5, 25.0 * self.config.recording_vertical_scale) for ii in res]
        return res

    def get_falling_chords(self):
        next_chords = [ii for ii in self.current_tab.get_next_chords(self.now_time, self.config)
                       if ii[1] < (self.now_time * self.config.playback_speed_scale) + self.config.recording_fall_time]
        res = []
        for ii in next_chords:
            if not (True in [ii[0].play_string[jj] for jj in range(6)]):
                continue
            else:
                res.append(FallingChord(ii, (self.now_time * self.config.playback_speed_scale), self.config, self.final_fret_offset))
        return res

    def get_fading_chords(self):
        res = []
        if self.last_render_time is not None:
            last_chords = self.current_tab.get_next_chords(self.last_render_time, self.config)
            now_chords = self.current_tab.get_next_chords(self.now_time, self.config)
            if len(now_chords) > 0 and now_chords[0] in last_chords:
                fade_chords = last_chords[:last_chords.index(now_chords[0])]
            else:
                fade_chords = last_chords
            y_offset = 95 - (25 * self.config.recording_vertical_scale)
            for fade_chord in fade_chords:
                for string_number in range(len(fade_chord[0].play_string)):
                    if fade_chord[0].play_string[string_number]:
                        fret_number = fade_chord[0].string_fret[string_number]
                        fret_offset = 0.0
                        for kk in range(fret_number):
                            fret_offset = ((95.0 - fret_offset) / 17.817) + fret_offset
                        fret_offset = 2.5 + (95 * fret_offset / self.final_fret_offset)
                        res.append(FadingFretMark(fret_offset,
                                                  y_offset + (5 - string_number) * 5 * self.config.recording_vertical_scale,
                                                  fade_chord[1] * (1 / self.config.playback_speed_scale), fade_chord[2] * (1 / self.config.playback_speed_scale), self.now_time * self.config.playback_speed_scale))
        return res
