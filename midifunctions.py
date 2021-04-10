# This class contains variables and functions used in threadbutton.py, mostly to do with translating chord names to sets
# of midi notes
import pickle
import re

class midf:
    def __init__(self):
        # Load all notes,chords and songs from pickle file
        self.notedict,self.custom_chords,self.songdict,self.dropnotes = pickle.load(open("/home/pi/data.p","rb"))
        # add all custom chords to the dropnotes list
        self.savedrop=self.dropnotes.copy() #don't want to save droplist with custom appended
        for chord in list(self.custom_chords.keys()):
            self.dropnotes.append(chord)
        self.allnotes = self.dropnotes

    def pdump(self): # save current class data to pkl
        alldata=[self.notedict,self.custom_chords,self.songdict,self.savedrop] 
        pickle.dump(alldata,open("/home/pi/data.p","wb"))

    def num_there(self, s):  # checks if a string has a number in it
        return any(i.isdigit() for i in s)

    def note2midi(self,note):
    # takes a note in the form "C#5" and returns the midi number. Can deal with #/b, but ignores octave 10
        if not re.fullmatch(r'\b[A-G][b#]?[0-9]', note):
            print("Unknown note "+note+". Format should be e.g. 'C#5'")
            print("Returning 60 (midi C5)")
            return 60

        notelist = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        offsets = dict(zip(notelist, range(0, 12)))
        num = int(re.findall(r'\d', note)[0])
        text = re.split(r'\d', note)[0]
        corrections = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
        if 'b' in text:
            text = corrections[text]
        return 12 * num + offsets[text]
    
    def midi2note(self, midi):
        octave=midi//12
        note=midi%12
        letnote=self.dropnotes[note]
        return letnote+str(octave)
    

    def chord2midi(self, chord):  # takes chord as string i.e "Ebm", "C1" returns list of midi numbers

        chord = chord.replace(" ", "")  # strip any spaces

        if self.num_there(chord):  # custom chords e.g. "C3"
            midi = self.custom_chords[chord]

        elif 'm' in chord:  # minor
            root = self.notedict[chord[:-1]]  # remove m to allow dict lookup

            # low root, high 5th, high root, high min 3rd
            midi = [root + 36, root + 55, root + 60, root + 63]

        else:  # major
            root = self.notedict[chord]

            # low root, high 5th, high root, high maj 3rd
            midi = [root + 36, root + 55, root + 60, root + 64]
        return midi

    def setup2midi(self, chords):  # takes list of chords, outputs list of midi lists, and the same list of chords
        output = []
        for chord in chords:
            output.append(self.chord2midi(chord))
        return output

    def song2midi(self, song):  # takes a song i.e. "pachabel" and returns a list of midi notes and the chords in the song
        chords = self.songdict[song]
        output = self.setup2midi(chords)
        return output, chords

    def start(self, user_input):  # user_input is song name, outputs list of notes and list of chords

        notes, setup = self.song2midi(user_input)



        print("Song is:", user_input)
        print("Chords are:", setup)


        return notes, setup

