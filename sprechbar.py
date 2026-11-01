#!/usr/bin/env python3
"""Macht Prompter-Texte sprechbar.

Entfernt alles, was man nicht vorlesen kann: Kastengrafik, Tabellenzeilen,
HTML-Reste, Trennlinien, Markdown-Auszeichnung, nackte URLs und Symbole.
Prosa bleibt unangetastet.

    sprechbar.py datei.txt [datei2.txt ...]
"""
import re, sys, unicodedata

KASTEN = "─│┌┐└┘├┤┬┴┼━┃╔╗╚╝║═▪▸►"

def sprechbar(text):
    zeilen, raus = [], 0
    for roh in text.splitlines():
        z = roh

        z = re.sub(r"<[^>]*>?", "", z)                   # HTML-Reste, auch kaputte
        z = re.sub(r"^\s*(li|ul|ol|div|p|span|iframe|br)\b", "", z)  # Tag-Reste ohne Klammer
        z = re.sub(r"&\w+;", "", z)                      # HTML-Entities
        z = re.sub(r"^\s*=+\s*(.*?)\s*=+\s*$", r"\1", z) # === Ueberschrift ===
        z = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", z)
        z = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", z)
        z = re.sub(r"[*_`#>]+", "", z)                   # Markdown
        z = re.sub(r"^\s*[-•▪]\s+", "", z)               # Aufzaehlungszeichen
        z = z.replace("→", " ").replace("←", " ").replace("×", " mal ")
        z = "".join(c for c in z if c not in KASTEN)
        z = "".join(c for c in z
                    if unicodedata.category(c)[0] != "S" or c in "€§%+=<>")
        z = " ".join(z.split())

        if not z:
            zeilen.append(""); continue
        if re.fullmatch(r"[-=_.\s]{3,}", z):        raus += 1; continue  # Trennlinien
        if z.count("|") >= 1:                        raus += 1; continue  # Tabellenzeile
        if re.fullmatch(r"(https?://|www\.)\S+", z): raus += 1; continue  # nackte URL
        if re.fullmatch(r"[\w.-]+\.(ai|de|com|org|io|md|txt|js|py)(/\S*)?", z):
            raus += 1; continue                                          # Domain/Datei allein
        if re.fullmatch(r"[\d\s.,:;%/€-]+", z):      raus += 1; continue  # reine Zahlenzeile
        # Nur echtes JSON: Schluessel UND Wert in Anfuehrungszeichen.
        # "Erstens: Klarheit" oder "JavaScript: meist um ..." sind Prosa und bleiben.
        if re.match(r'^\s*[„"\u201c]\w+[""\u201d]?\s*:\s*[„"\u201c]', z):
            raus += 1; continue
        if "src=" in z or "class=" in z or "href=" in z: raus += 1; continue
        if len(z.split()) < 4:                       raus += 1; continue  # Fragment
        zeilen.append(z)

    # mehrfache Leerzeilen zusammenfassen
    out, leer = [], False
    for z in zeilen:
        if z == "":
            if not leer: out.append("")
            leer = True
        else:
            out.append(z); leer = False
    return "\n".join(out).strip() + "\n", raus


if __name__ == "__main__":
    for p in sys.argv[1:]:
        alt = open(p, encoding="utf-8").read()
        neu, raus = sprechbar(alt)
        open(p, "w", encoding="utf-8").write(neu)
        wa, wn = len(alt.split()), len(neu.split())
        print(f"  {p.split('/')[-1]:32s} {wa:6,} -> {wn:6,} Woerter   "
              f"{raus:3d} Zeilen entfernt   ~{wn/130:.0f} min")
