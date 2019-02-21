from music21 import *
from copy import deepcopy
from random import randrange,choice,shuffle

# funkcje modyfikujące melodię

def cutHalfVoice(voice):
    l = len(voice)
    new_voice1 = stream.Voice()
    new_voice2 = stream.Voice()
    for n in voice:
        if n.offset < l/2:
            new_voice1.append(n)
        else:
            new_voice2.append(n)
    return new_voice1, new_voice2

def polaczGlosy(v1,v2):
    maxOff = 0
    if len(v1) != 0:
        maxOff = v1.highestOffset + v1[-1].duration.quarterLength
    else:
        maxOff = v1.highestOffset

    for n in v2:
        v1.insertAndShift(maxOff,deepcopy(n))
        maxOff += n.duration.quarterLength

def przyspiesz(voice, mnoznik):
    return voice.augmentOrDiminish(1.0/mnoznik)

def przyspieszPrawidlowo(voice):
    new_voice = przyspiesz(voice,2.0)
    voice.removeByClass('Note')
    polaczGlosy(voice,new_voice)
    polaczGlosy(voice,new_voice)

def zwolnij(voice, mnoznik):
    return voice.augmentOrDiminish(mnoznik)

def zwolnijPrawidlowo(voice):
    p1, p2 = cutHalfVoice(voice)
    voice.removeByClass('Note')
    polaczGlosy(voice,zwolnij(p1,2.0))

def odwrocKolejnosc(voice):
    res = stream.Voice()
    for i in range(len(voice)-1,-1,-1):
        res.append(deepcopy(voice[i]))
    voice.removeByClass('Note')
    polaczGlosy(voice, res)

def przewrot(voice):
    dlug = randrange(1,len(voice))
    liczba_oktaw = dlug // len(voice)
    dlug %= len(voice)
    res = stream.Voice()
    for i in range(dlug, len(voice)):
        res.append(deepcopy(voice[i]))
    for i in range(dlug):
        new_note = deepcopy(voice[i])
        new_note.octave += 1 + liczba_oktaw
        res.append(new_note)
    voice.removeByClass('Note')
    polaczGlosy(voice,res)

def transponuj(voice):
    inter = choice([3,4,7,-3,-4,-7])
    inter = interval.ChromaticInterval(inter)
    new_voice = deepcopy(voice)
    for i in range(len(new_voice)):
        new_voice[i] = new_voice[i].transpose(inter)
    voice.removeByClass('Note')
    polaczGlosy(voice, new_voice)

def zmienLosowyDzwiek(voice):
    num = randrange(1,4)
    new_voice = deepcopy(voice)
    for i in range(num):
        index = randrange(len(new_voice))
        new_voice[index] = new_voice[index].transpose(interval.Interval(randrange(-6,7)))
    voice.removeByClass('Note')
    polaczGlosy(voice, new_voice)

def inwersja(voice):
    new_voice = stream.Voice()
    new_voice.append(deepcopy(voice[0]))
    for i in range(1,len(voice)):
        inter = interval.Interval(voice[i-1],voice[i])
        new_voice.append(interval.transposeNote(new_voice[i-1],inter.reverse()))
    voice.removeByClass('Note')
    polaczGlosy(voice, new_voice)

# stworzenie jakiejś melodyjki
# s = stream.Stream()
# v = stream.Voice()
# notes = list(map(note.Note,['B-3','D4','G4','B-4','D5','B-4','G4','D4']))
# for n in notes:
#     v.append(n)

subject = [("C5", 1),("C5", 0.5), ("B4", 0.5), ("C5", 1), ("G4", 1), ("A-4", 1), ("C5", 0.5),
    ("B4", 0.5), ("C5", 1), ("D5", 1), ("G4", 1), ("C5", 0.5), ("B4", 0.5), ("C5", 1),
    ("D5", 1), ("F4", 0.5), ("G4", 0.5), ("A-4", 1), ("G4", 0.5), ("F4", 0.5), ("E4", 1)]

subject_voice = stream.Voice()
subject_voice.id = 'Subject'

for n, d in subject:
    if n == "":
        n1 = note.Rest()
    else:
        n1 = note.Note(n)
    n1.duration.quarterLength = d/2
    subject_voice.append(n1)

# s.insert(0,v)

# TESTY DROBNYCH FUNKCJI
# t = stream.Voice(s[0].augmentOrDiminish(0.5))
# t2 = zmienLosowyDzwiek(t,3)
# # polaczGlosy(s[0],t2)
# transponuj(t,'d9')
# polaczGlosy(s[0],t)
# z = odwrocKolejnosc(t)
# polaczGlosy(s[0],z)
# polaczGlosy(s[0], przewrot(t,12))

# t = inwersja(s[0])
# s.insert(0,t)

def mocne(i,j):
    if i == j:
        return 0
    inter = interval.notesToChromatic(i,j).mod12
    if inter in [0,7]:
        return 1
    return 0

def slabe(i,j):
    if i == j:
        return 0
    inter = interval.notesToChromatic(i,j).mod12
    if inter in [3,4,8,9]:
        return 1
    return 0

def zmierzOdleglosci(nuty, pred):
    if len(nuty) == 1:
        return -1
    return sum([pred(i,j) for i in nuty for j in nuty])

def ocena(takt):
    mocnaCzesc = True
    wszystkieNuty = set()
    liczbaZgodnych = 0
    left_offset = 0.0
    right_offset = 0.5
    while left_offset <= takt.highestOffset:
        nuty = []
        for v in takt:
            nuty += list(v.getElementsByOffset(left_offset,right_offset))

        if not all(map(lambda x: id(x) in wszystkieNuty, nuty)):
            if mocnaCzesc:
                liczbaZgodnych += zmierzOdleglosci(nuty,mocne)
            else:
                liczbaZgodnych += zmierzOdleglosci(nuty,slabe)
        for n in nuty:
            wszystkieNuty.add(id(n))
        left_offset += 0.5
        right_offset += 0.5
        if int(left_offset)%2 == 0:
            mocnaCzesc = True
        else:
            mocnaCzesc = False
    return len(wszystkieNuty) + (liczbaZgodnych / len(wszystkieNuty)) * 1000.0


def dokonajKrzyzowki(fuga, liczbaWlaczonychGlosow, przodkowie, glosProwadzacy):
    res1 = stream.Stream()
    res2 = stream.Stream()

    for i in range(len(fuga)):
        res1.insert(0,stream.Voice())
        res2.insert(0,stream.Voice())

    for i in range(liczbaWlaczonychGlosow):
        if i == glosProwadzacy:
            polaczGlosy(res1[i],choice(list(przodkowie.values()))[i])
            polaczGlosy(res2[i],choice(list(przodkowie.values()))[i])
        else:
            anc1 = choice(list(przodkowie.values()))[i]
            anc2 = choice(list(przodkowie.values()))[i]
            p1, p2 = cutHalfVoice(anc1)
            f1, f2 = cutHalfVoice(anc2)
            polaczGlosy(p1,f2)
            polaczGlosy(res1[i],p1)
            polaczGlosy(f1,p2)
            polaczGlosy(res2[i],f1)
    return res1, res2

bazaMutacji = [przyspieszPrawidlowo, zwolnijPrawidlowo, odwrocKolejnosc, przewrot, transponuj, zmienLosowyDzwiek, inwersja]
def dokonajMutacji(fuga, liczbaWlaczonychGlosow, przodkowie, glosProwadzacy):
    res = deepcopy(choice(list(przodkowie.values())))

    for i in range(randrange(1,4)):
        mutacja = choice(bazaMutacji)
        glos = randrange(liczbaWlaczonychGlosow)
        while glos == glosProwadzacy:
            glos = randrange(liczbaWlaczonychGlosow)
        if len(res[glos]) == 1:
            continue
        mutacja(res[glos])

    return res

def stworzGameDurowa(ton):
    gama = stream.Voice()
    gama.append(deepcopy(ton))
    interwaly = list(map(interval.Interval, [2,2,1,2,2,2,1]))
    prev = ton
    nuta = None
    for i in range(7):
        nuta = prev.transpose(interwaly[i])
        gama.append(nuta)
        prev = nuta
    return gama

def stworzBazePrzodkow(fuga, liczbaWlaczonychGlosow, temat, new_voice, glosProwadzacy, odwroconaMapaGlosow):
    przodkowie = {}
    for i in range(5):
        ancestor = stream.Stream()
        for j in range(len(fuga)):
            ancestor.insert(0,stream.Voice())

        for j in range(liczbaWlaczonychGlosow):
            if j == glosProwadzacy:
                polaczGlosy(ancestor[j], new_voice)
            else:
                gama = choice([stworzGameDurowa(temat.getElementsByOffset(0)[0])])
                mutacja = choice(bazaMutacji)
                mutacja(gama)

                roznica = odwroconaMapaGlosow[glosProwadzacy] - odwroconaMapaGlosow[j]
                for n in gama:
                    n.octave -= roznica

                polaczGlosy(ancestor[j], gama)

        przodkowie[ocena(ancestor)-randrange(300,400)] = ancestor

    return przodkowie

def usunPrzodkow(przodkowie, progOdrzucenia):
    posortowaneKlucze = sorted(przodkowie)
    liczbaOdrzuconych = int(len(przodkowie) * progOdrzucenia)
    for i in range(liczbaOdrzuconych):
        k = posortowaneKlucze[i]
        del przodkowie[k]

# optymalizuje fragment zawierajacy jeden temat
def algorytmEwolucyjny(fuga, liczbaWlaczonychGlosow, temat, progOdrzucenia, roznica, glosProwadzacy, odwroconaMapaGlosow):
    new_voice = deepcopy(temat)
    for n in new_voice:
        n.octave -= roznica
    przodkowie = stworzBazePrzodkow(fuga, liczbaWlaczonychGlosow, temat, new_voice, glosProwadzacy, odwroconaMapaGlosow)

    for i in range(100):
        for j in range(10):
            s1,s2 = dokonajKrzyzowki(fuga, liczbaWlaczonychGlosow, przodkowie, glosProwadzacy)
            przodkowie[ocena(s1)] = s1
            przodkowie[ocena(s2)] = s2
        for j in range(10):
            dokonajMutacji(fuga, liczbaWlaczonychGlosow, przodkowie, glosProwadzacy)

        usunPrzodkow(przodkowie, progOdrzucenia)

    zwyciezca = przodkowie[max(przodkowie.keys())]
    return zwyciezca

def dolaczNowyTakt(nowyTakt, fuga):
    for i in range(len(nowyTakt)):
        polaczGlosy(fuga[i],nowyTakt[i])

# zakladam, ze glosow będzie od 2 do 6
def makeFuga(liczbaGlosow, progOdrzucenia, liczbaPowtorzenTematu, temat):
    liczbaWlaczonychGlosow = 1
    mapaGlosow = {}
    # zapewnia, że w przypadku do 4 glosow pierwszy glos bedzie najwyzszy,
    #     a w przypadku 5-6 glosow, prawie najwyzszy
    # glosGlowny = min(4,max(2,liczbaGlosow)) - 1
    glosGlowny = 3
    sekwencjaGlosow = [i for i in range(liczbaGlosow) if i != glosGlowny]
    shuffle(sekwencjaGlosow)

    maxOff = temat.highestOffset + temat[-1].duration.quarterLength
    fuga = stream.Stream()
    for i in range(liczbaGlosow):
        if i == glosGlowny:
            fuga.insert(0, temat)
            mapaGlosow[glosGlowny] = 0
        else:
            fuga.insert(maxOff * (sekwencjaGlosow.index(i) + 1), stream.Voice())
            mapaGlosow[i] = sekwencjaGlosow.index(i) + 1

    for i in range(1,liczbaPowtorzenTematu):
        print("pokolenie:",i)
        wylosowany = None
        if liczbaWlaczonychGlosow != liczbaGlosow:
            wylosowany = sekwencjaGlosow[liczbaWlaczonychGlosow-1]
            liczbaWlaczonychGlosow += 1
        else:
            wylosowany = randrange(liczbaGlosow)

        roznica = glosGlowny - wylosowany
        wylosowany = mapaGlosow[wylosowany]
        odwroconaMapaGlosow = {mapaGlosow[k]:k for k in mapaGlosow}

        nowyTakt = algorytmEwolucyjny(fuga, liczbaWlaczonychGlosow, temat, progOdrzucenia, roznica, wylosowany, odwroconaMapaGlosow)

        dolaczNowyTakt(nowyTakt, fuga)

    return fuga

s = makeFuga(4, 0.9, 6, subject_voice)

# v = stworzGameDurowa(note.Note('c4'))
# u = deepcopy(v)
# zmienLosowyDzwiek(u)
# polaczGlosy(v,u)
# s = stream.Stream(v)

# s.show()
mf = midi.translate.streamToMidiFile(s)
mf.open('fuga.mid','wb')
mf.write()
mf.close()
