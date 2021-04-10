"""Script to make initial pickle of songs, chords and notes (or to reset when things go wrong)"""
import pickle

notedict = {  # midi base notes (octave -1)
    "C": 0,
    "C#": 1,
    "D": 2,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "G#": 8,
    "A": 9,
    "Bb": 10,
    "B": 11}  # midi base notes

custom_chords = {  # Code identifies these by the presence of a no.
    "C1": [36, 60, 64, 67],  # higher 5th
    "D1": [38, 54, 57, 62],  # low 3rd
    "Bbm1": [46, 49, 65, 70],  # low 3rd
    "E1": [40, 52, 44, 47],  # C, guitar capo 4
    "Bmod1": [37, 45, 49, 51],  # second chord in excelsis
    "C#m1": [55, 43, 49],
    "sys1": [62, 62, 50, 47],
    "sys2": [62, 61, 50, 45],
    "sys3": [71, 59, 50, 43],
    "B1": [63, 66, 47, 59],
    "sys4": [62, 66, 54, 50]
}  # user defined chords

songdict = {
    "basic": ["C", "G", "F", "Am", "Em", "D", "C1"],
    "pachabel": ["D", "A", "Bm", "F#m", "G", "D1", "D"],
    "emotional": ["E", "B1", 'F#', "G#m", "Ebm", "Cm", "B"],
    "excelsis": ["E1", "B", 'F#', "C#m1", "Ebm", "Bmod1", "B"],
    "see you soon": ["sys1", "sys2", "sys3", "sys4", "Bbm1", "D1", "C"]
}  # sets of chords for custom songs

# basic chord list for web server dropdown
dropnotes = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B',
             'Cm', 'C#m', 'Dm', 'Ebm', 'Em', 'Fm', 'F#m', 'Gm', 'G#m', 'Am',
             'Bbm', 'Bm']

alldata = [notedict, custom_chords, songdict, dropnotes]
pickle.dump(alldata, open("data.p", "wb"))

if __name__ == "__main__":
    # example how to load data.p
    a, b, c, d = pickle.load(open("data.p", "rb"))
    print(a, b, c, d)
