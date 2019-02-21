import os

def convertAnythingToWav(fileName):
    os.system('ffmpeg -i ' + fileName + ' subject.wav')

def convertWavToMidi():
    os.system('./waon -i subject.wav -o subject.mid')

def convertRecordToMidi(fileName):
    convertAnythingToWav(fileName)
    convertWavToMidi()
