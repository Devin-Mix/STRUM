class Tab:
    def __init__(self, file_to_open):
        if type(file_to_open) != str:
            raise TypeError("Invalid argument for Tab.__init__(str) (Expected str, got {}".format(type(file_to_open)))
        with open(file_to_open, "r") as f:
            raw_data = f.read().splitlines()
            f.close()
        parsing_header = True
        self.tuning = [0, 0, 0, 0, 0, 0]
        self.bpm = 120
        self.artist = None
        self.title = None
        scan_time = 0.0
        self.chords = []
        for line in raw_data:
            if parsing_header:
                if line == "///":
                    parsing_header = False
                elif len(line) > 7 and line[0:7] == "Tuning=":
                    try:
                        t = [int(i) for i in line.split("Tuning=")[1].split(",")]
                    except ValueError:
                        print("ValueError setting tuning for {} (\"{}\"), discarding tuning".format(file_to_open, line))
                        continue
                    if len(t) != 6:
                        print("Invalid number of tuning arguments for {} (\"{}\"), discarding tuning".
                              format(file_to_open, line))
                    else:
                        self.tuning = t
                elif len(line) > 4 and line[0:4] == "BPM=":
                    try:
                        self.bpm = float(line.split("BPM=")[1])
                    except ValueError:
                        print("ValueError setting tempo for {} (\"{}\"), discarding tempo".format(file_to_open, line))
                elif len(line) > 6 and line[0:6] == "Title=":
                    self.title = line.split("Title=")[1]
                elif len(line) > 7 and line[0:7] == "Artist=":
                    self.artist = line.split("Artist=")[1]
                else:
                    print("Invalid header argument detected for {} (\"{}\"), disregarding...".
                          format(file_to_open, line))
            else:
                if len(line) < 6:
                    print("Line too short in {} (\"{}\"), disregarding...")
                else:
                    line_chord = Chord(line)
                    chord_len_sec = pow(self.bpm * (1.0 / 60.0), -1.0) * line_chord.chord_len
                    self.chords.append((line_chord, scan_time, chord_len_sec))
                    scan_time = scan_time + chord_len_sec

    def get_next_chords(self, current_time):
        return [i for i in self.chords if i[1] >= current_time]


class Chord:
    def __init__(self, chord_string):
        strings_string = chord_string[0:6]
        length_string = chord_string[6:]
        self.play_string = [i != "|" for i in strings_string]
        self.string_fret = []
        for i in strings_string:
            if i == "|":
                self.string_fret.append(0)
            else:
                self.string_fret.append(int(i))
        self.chord_len = 0.0
        for tie_part in length_string.split("+"):
            num_hyphens = tie_part.count("-")
            num_periods = tie_part.count(".")
            note_len = 1.0 / pow(2.0, num_hyphens)
            dots_len = 0.0
            for i in range(num_periods):
                dots_len = dots_len + (note_len * (1.0 / pow(2.0, i + 1)))
            self.chord_len = self.chord_len + note_len + dots_len
        self.chord_len = self.chord_len * 4.0
