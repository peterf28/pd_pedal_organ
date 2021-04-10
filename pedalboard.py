#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import os
import subprocess
import threading
from midifunctions import midf  # functions for translating notes or songnames to midi chords
from flask import Flask, flash, redirect, render_template, \
    request, url_for


def send_pd(note, switch):  # sends a message to the terminal that pd can pick up
    if switch == "on":
        message = str(note) + ' 100' + ';'
    if switch == "off":
        message = str(note) + ' 0' + ';'
    os.system("echo '" + message + "'  | pdsend 3000")
    print(m.midi2note(note) + " " + switch)


# Setup

# initialise midf class (to give notes, chords etc)
m = midf()

# Set rPi pins etc
pins = [7, 5, 6, 22, 23, 27, 4]  # pins used on the pisound board
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # GPIO.setmode(GPIO.BOARD)
for pin in pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

sustain = True
on = [0, 0, 0, 0, 0, 0, 0]

# Get initial pedal chord setup
song = "excelsis"
notes, setup = m.start(song)  # get the note list and chord list
noteout = setup  # this remains until user changes the notes on the server, updating noteout

os.system("/usr/local/pisound/scripts/pisound-btn/start_puredata.sh")

# FLASK ---------------------------------------------------------------------------------------------------------------#
app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template("pedalboard.html", options=m.allnotes, defaults=noteout, s_list=m.songdict, s_def=song)


@app.route('/update', methods=['GET', 'POST'])
def update():
    # called by update keys and save song
    global noteout, song

    noteout = [request.form.get("key" + str(k + 1)) for k in range(7)]
    if request.form["submit"] == "Add Song":  # called from add song button
        sn = request.form.get("sname")  # song name
        m.songdict[sn] = noteout
        m.pdump()
        song = sn
        print("Added ", noteout, " as ", sn)
    return render_template("pedalboard.html", options=m.allnotes, defaults=noteout, s_list=m.songdict, s_def=song)


@app.route('/loads', methods=['GET', 'POST'])
def loads():
    global noteout
    news = request.form.get("s_sel")
    noteout = m.songdict[news]

    print("Song is: " + news)
    return render_template("pedalboard.html", options=m.allnotes, defaults=noteout, s_list=m.songdict, s_def=news)


@app.route('/newc', methods=['GET', 'POST'])
def newc():
    newch = []
    for i in range(4):
        notename = request.form.get("c" + str(i + 1))
        midnum = m.note2midi(notename)
        newch.append(midnum)
    name = request.form.get("cname")
    m.custom_chords[name] = newch
    m.pdump()
    if name not in m.dropnotes:
        m.dropnotes.append(name)
    print("Added ", newch, " as ", name)

    return render_template("pedalboard.html", options=m.allnotes, defaults=noteout, s_list=m.songdict, s_def=song)


@app.route('/sustain', methods=['POST'])
def sust():
    global sustain
    sustain = not sustain
    print("Sustain is:", sustain)
    return render_template("pedalboard.html", options=m.allnotes, defaults=noteout, s_list=m.songdict, s_def=song)


# ---------------------------------------------------------------------------------------------------------------------#


# thread1
def notethread():
    global noteout
    global setup
    global notes
    global on
    lastnotes = [0, 0, 0, 0]
    lastkey = 6
    deboun = False
    # try:
    while True:  # Run forever
        # check if setup has changed
        if noteout != setup:
            time.sleep(0.2)  # wait to allow the other thread to finish updating
            notes = m.setup2midi(noteout)  # ignore second output
            print("New chords are: ", noteout)
            # print("New notes are: ", notes)
            setup = noteout
        if sustain:
            for i in range(6):  # for each key apart from last
                if GPIO.input(pins[i]) == GPIO.HIGH and on[i] == 0:  # if the button has been pressed + it wasn't before
                    on[6] = 0
                    for lnote in lastnotes:
                        send_pd(lnote, "off")
                    print("")  # newline to separate chord printout
                    lastnotes = []
                    on[lastkey] = 0
                    for note in notes[i]:
                        send_pd(note, "on")
                        lastnotes.append(note)
                    on[i] = 1
                    lastkey = i

            if GPIO.input(pins[6]) == GPIO.HIGH and on[6] == 0:  # if last key is pressed
                for lnote in lastnotes:
                    send_pd(lnote, "off")
                lastnotes = [0, 0, 0, 0]
                on = [0, 0, 0, 0, 0, 0, 1]
        else:
            for i in range(7):  # for each key
                if GPIO.input(pins[i]) == GPIO.HIGH and on[i] == 0:  # if the button has been pressed + it wasn't before
                    for note in notes[i]:
                        send_pd(note, "on")
                    print("")  # newline to separate chord printout
                    on[i] = 1
                    deboun = True

                if GPIO.input(pins[i]) == GPIO.LOW and on[i] == 1:  # if the button is not pressed + it was before
                    for note in notes[i]:
                        send_pd(note, "off")
                    print("\n")  # newline to separate chord printout
                    on[i] = 0
                    deboun = True

        if deboun:  # if debouncing is needed
            deboun = False
            time.sleep(0.1)
    # except Exception as e:
    # send_pd('0;')
    # print(str(e))


if __name__ == '__main__':
    n = threading.Thread(target=notethread)
    n.start()
    app.run(host='0.0.0.0')  # flask has to be in the main thread to work
    print("Started flaskthread")
    time.sleep(0.6)
    print("Ready")
