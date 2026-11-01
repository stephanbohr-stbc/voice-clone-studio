#!/usr/bin/env python3
"""Prueft Aufnahmen auf genau die Fehler, die einen Stimmklon ruinieren.

Sechs Pruefungen, jede mit klarem Urteil:
  1. Clipping          - uebersteuerte Stellen sind irreparabel
  2. Rauschabstand     - Rauschen lernt der Klon mit
  3. Sprechpegel       - muss ueber alle Takes gleich sein
  4. Drift             - laeuft der Pegel innerhalb des Takes weg?
  5. Aussetzer         - verlorene USB-Pakete, hoerbar als Knacken
  6. Fremdsignal       - steht am Anfang etwas, das nicht hingehoert?

Punkt 5 ist der, der beim MV7 vier Wochen unentdeckt blieb: Aussetzer
zeigen sich daran, dass sie AUCH IN DEN SPRECHPAUSEN auftreten. Transienten
aus Plosiven sitzen dagegen ausschliesslich in der Sprache.
"""
import subprocess, sys, re, statistics, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from entknacksen import lese, finde

G, Y, R, D, B = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[1m"
N = "\033[0m"

def ff(f, af, key):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f, "-af", af,
                        "-f", "null", "-"], capture_output=True, text=True)
    return re.findall(key, r.stdout + r.stderr)

def sekunden(f):
    return [float(x) for x in ff(f, "asetnsamples=n=48000:p=0,astats=metadata=1:reset=1,"
            "ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-",
            r"RMS_level=(-?[\d.]+)")]

def zeile(ok, text, warnung=False):
    m, c = ("OK  ", G) if ok else (("WARN", Y) if warnung else ("FEHL", R))
    print(f"  {c}{m}{N}  {text}")

def pruefe(pfad):
    name = os.path.basename(pfad)
    v = sekunden(pfad)
    if len(v) < 20:
        print(f"\n{B}  {name}{N}\n  zu kurz zum Pruefen"); return
    sp = [x for x in v if x > -45]
    if len(sp) < 20:
        print(f"\n{B}  {name}{N}\n  zu wenig Sprache"); return
    ruhe = sorted(v)
    pegel = statistics.median(sp)
    rausch = statistics.median(ruhe[:8])
    snr = pegel - rausch
    d = len(sp) // 3
    drift = statistics.median(sp[2*d:]) - statistics.median(sp[:d])

    pk = float(ff(pfad, "astats", r"Peak level dB:\s*(-?[\d.]+)")[0])
    flat = float(ff(pfad, "astats", r"Flat factor:\s*(-?[\d.]+)")[0])

    x, par = lese(pfad); sr = par.framerate
    stellen, _ = finde(x, 200.0, sr)
    n = len(x) // sr
    laut = [20*np.log10(np.sqrt(np.mean(x[i*sr:(i+1)*sr]**2)) + 1e-12) for i in range(n)]
    in_stille = sum(1 for i in stellen if laut[min(int(i/sr), n-1)] <= -45)
    minuten = len(x)/sr/60

    # Fremdsignal am Anfang?
    fremd = 0
    for i in range(min(60, len(v))):
        if v[i] > -45:
            j = i
            while j < len(v)-3 and not all(y <= -60 for y in v[j:j+3]): j += 1
            if j < 60: fremd = j
            break

    print(f"\n{B}  {name}   {minuten:.1f} min, davon {len(sp)/60:.1f} min Sprache{N}")
    zeile(pk < -0.5, f"Clipping        {'keins' if pk < -0.5 else 'JA - Take verwerfen'}   (Spitze {pk:+.1f} dBFS)")
    zeile(snr >= 45, f"Rauschabstand   {snr:5.0f} dB   (Ziel >= 45, Rauschen {rausch:+.0f} dBFS)", warnung=snr >= 40)
    zeile(True,      f"Sprechpegel     {pegel:+6.1f} dBFS")
    zeile(abs(drift) <= 1.5, f"Drift           {drift:+6.1f} dB   (Ziel unter 1,5)", warnung=abs(drift) <= 2.5)
    zeile(in_stille < 5, f"Aussetzer       {in_stille:5d} in Sprechpausen   ({len(stellen)} gesamt, Rest sind Plosive)")
    zeile(fremd == 0, f"Anfang          {'sauber' if not fremd else f'Fremdsignal bis {fremd} s - abschneiden!'}", warnung=bool(fremd))
    return pegel

if __name__ == "__main__":
    ziele = sys.argv[1:] or ["."]
    dateien = []
    for z in ziele:
        dateien += sorted([os.path.join(z, f) for f in os.listdir(z) if f.endswith(".wav")]) \
                   if os.path.isdir(z) else [z]
    pegel = [p for p in (pruefe(f) for f in dateien) if p]
    if len(pegel) > 1:
        print(f"\n{B}  Gleichmaessigkeit ueber alle Takes{N}")
        zeile(max(pegel)-min(pegel) <= 2.0,
              f"Pegelspanne     {max(pegel)-min(pegel):5.1f} dB   (Ziel unter 2)",
              warnung=max(pegel)-min(pegel) <= 3.0)
