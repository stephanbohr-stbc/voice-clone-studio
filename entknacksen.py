#!/usr/bin/env python3
"""Repariert Sprungstellen (verlorene Samples) in Aufnahmen.

Ein USB-Aussetzer verliert einen Block Samples. Das Signal springt dadurch
schlagartig auf einen anderen Wert und laeuft dort glatt weiter - hoerbar als
Knacks. Beide Seiten sind gueltiges Audio, es fehlt nur ein Stueck dazwischen.

Rekonstruieren laesst sich das Fehlende nicht. Man kann den Sprung aber mit
einer kurzen Ueberblendung (Standard 3 ms) unhoerbar machen. Die Datei wird
dabei um wenige Millisekunden pro Fundstelle kuerzer.

    entknacksen.py eingabe.wav ausgabe.wav [--schwelle 8] [--fenster-ms 3]
"""
import sys, wave, numpy as np

def lese(p):
    w = wave.open(p, "rb")
    par = w.getparams()
    roh = w.readframes(w.getnframes())
    w.close()
    if par.sampwidth != 3 or par.nchannels != 1:
        sys.exit(f"{p}: erwartet 24 Bit mono, gefunden {par.sampwidth*8} Bit / {par.nchannels} Kanal")
    b = np.frombuffer(roh, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
    x = (b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16))
    x = np.where(x & 0x800000, x - 0x1000000, x).astype(np.float64) / 8388608.0
    return x, par

def schreibe(p, x, par):
    y = np.clip(np.round(x * 8388608.0), -8388608, 8388607).astype(np.int32)
    b = np.empty((len(y), 3), dtype=np.uint8)
    b[:, 0] = y & 0xFF; b[:, 1] = (y >> 8) & 0xFF; b[:, 2] = (y >> 16) & 0xFF
    w = wave.open(p, "wb")
    w.setnchannels(1); w.setsampwidth(3); w.setframerate(par.framerate)
    w.writeframes(b.tobytes()); w.close()

def finde(x, faktor, sr=48000):
    """Sucht Bruchstellen in der Glattheit des Signals.

    Ein Aussetzer bricht die lineare Fortsetzung des Signalverlaufs. Verglichen
    wird gegen den oertlichen Durchschnitt statt gegen einen festen Wert - sonst
    findet man nur die lautesten Stellen und uebersieht alles in leisen Passagen.
    """
    vorhersage = 2 * x[1:-1] - x[:-2]
    fehler = np.abs(x[2:] - vorhersage)
    # gleitender Mittelwert ueber Summenbildung - np.convolve waere bei
    # 90 Millionen Samples um Groessenordnungen langsamer
    f = max(1024, sr // 4)
    kum = np.concatenate(([0.0], np.cumsum(fehler)))
    lo = np.clip(np.arange(len(fehler)) - f // 2, 0, len(fehler))
    hi = np.clip(np.arange(len(fehler)) + f // 2, 0, len(fehler))
    lokal = (kum[hi] - kum[lo]) / np.maximum(hi - lo, 1) + 1e-9
    treffer = np.nonzero(fehler / lokal > faktor)[0] + 2
    if len(treffer) == 0:
        return treffer, 0.0
    gruppen = [treffer[0]]
    for i in treffer[1:]:
        if i - gruppen[-1] > 64:
            gruppen.append(i)
    return np.array(gruppen), 0.0


def repariere(x, stellen, w):
    """Blendet an jeder Fundstelle ueber w Samples von links nach rechts ueber."""
    teile = []
    ende_vorher = 0
    rampe = 0.5 * (1 - np.cos(np.pi * np.arange(w) / w))   # weiche Flanke
    for i in stellen:
        a, b = int(i) - w, int(i) + w
        if a <= ende_vorher or b >= len(x): continue
        teile.append(x[ende_vorher:a])
        teile.append(x[a:i] * (1 - rampe) + x[i:b] * rampe)
        ende_vorher = b
    teile.append(x[ende_vorher:])
    return np.concatenate(teile)

if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2: sys.exit(__doc__)
    ein, aus = a[0], a[1]
    faktor = float(a[a.index("--schwelle") + 1]) if "--schwelle" in a else 200.0
    ms     = float(a[a.index("--fenster-ms") + 1]) if "--fenster-ms" in a else 2.0
    x, par = lese(ein)
    stellen, _ = finde(x, faktor, par.framerate)
    w = max(16, int(par.framerate * ms / 1000))
    y = repariere(x, stellen, w) if len(stellen) else x
    schreibe(aus, y, par)
    nach, _ = finde(y, faktor, par.framerate)
    print(f"  {ein.split('/')[-1]:20s} {len(stellen):4d} Stellen -> {len(nach):3d} übrig   "
          f"{len(x)/par.framerate/60:5.1f} min, {(len(x)-len(y))/par.framerate*1000:.0f} ms entfernt")
