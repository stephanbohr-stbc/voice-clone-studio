# Voice Clone Studio

Ein kleines Aufnahme-Studio für macOS, mit dem du Trainingsmaterial für einen
**Professional Voice Clone bei ElevenLabs** aufnimmst: roh, sauber und ohne
Bearbeitung, die der Klon mitlernen würde.

Entstanden in zwei Anläufen über zehn Wochen. Im ersten Anlauf knackte jede Aufnahme,
und der fertige Klon auch. Kein Reparaturwerkzeug hat das gerettet. Dieses Repo ist
das Werkzeug, mit dem es im zweiten Anlauf an einem Nachmittag geklappt hat.

Unabhängiges Projekt, nicht mit ElevenLabs oder Shure verbunden.

---

## Was das Studio kann

- **Prompter mit Lauftext** im Browser. Das **Mausrad** regelt das Tempo, auch während
  der Aufnahme. **Shift + Mausrad** holt eine verpasste Zeile zurück.
- **Leseposition pro Text merken.** Lange Texte nimmst du in Teilen von 7–8 Minuten
  auf, nach dem Stopp geht es genau dort weiter.
- **Mikrofon-Check vor dem Start:** richtiges Gerät gewählt, nicht stummgeschaltet,
  Signal kommt an.
- **Live-Pegelanzeige**, Tasten für Pause (`P`) und Versprecher-Markierung (`M`).
- **Prüfung nach jedem Take:** Spitze, Lautheit, Rauschabstand, Clipping, Mundgeräusche
  pro Minute.
- **Aufnahme über sox, nicht über den Browser und nicht über ffmpeg.** Der Browser
  würde Rauschunterdrückung und Pegelautomatik anlegen. ffmpeg (avfoundation) hat auf
  dem Mac Samples verloren, hörbar als Knacken:

  | Aufnahmeweg | Knackser pro Minute | Dauer bei 22 s Soll |
  |---|---|---|
  | ffmpeg avfoundation | 168 | 20,0 s |
  | sox (CoreAudio) | 11 | 22,0 s |

---

## Schnellstart

```bash
git clone https://github.com/stephanbohr-stbc/voice-clone-studio.git
cd voice-clone-studio
brew install sox ffmpeg switchaudio-osx
./vc kalibrieren        # Rauschtest und Pegel, vor jeder Session
./vc studio             # Studio im Browser öffnen
```

Einstellungen über Umgebungsvariablen:

| Variable | Standard | Bedeutung |
|---|---|---|
| `VC_MIC` | `Shure MV7+` | Name des Mikrofons, wie macOS es anzeigt |
| `VC_TAKES` | `~/Music/VoiceClone-Takes` | Ablage der Aufnahmen |
| `VC_TEXTE` | `~/Music/VoiceClone-Texte` | zusätzlicher Ordner mit eigenen Prompter-Texten |

Details: **[INSTALLATION.md](INSTALLATION.md)** · **[ANLEITUNG.md](ANLEITUNG.md)**

---

## Die Texte

In `sprechtexte/` liegen vier Beispielblöcke:

| Block | Inhalt |
|---|---|
| A | phonetische Abdeckung (alle Laute des Deutschen) |
| B | Zahlen, Kürzel, Anglizismen, Eigennamen. **Die Namen durch deine eigenen ersetzen** |
| D | Lehr-Duktus: erklären, Fragen stellen, Pausen |
| E | Dynamik: Fragen, Betonung, Zuspruch, Warnung |

Block C ist dein eigener Fließtext, zum Beispiel ein Artikel oder eine Broschüre, die du
ohnehin sprechen würdest. Leg ihn als `.txt` in `sprechtexte/` oder in `VC_TEXTE`.
`sprechbar.py` entfernt vorher alles, was man nicht vorlesen kann (Markdown, Code, Links).

---

## Was ich vorher gern gewusst hätte

- **Raum:** klein, möbliert, alles Summende aus. Kissen vor und neben das Mikrofon,
  eine Decke hinter den Stuhl. Ein Handtuch unter den Mikrofonfuß nimmt Körperschall
  vom Tisch (bei mir 11 dB weniger Brummen unter 120 Hz).
- **Rechner:** neu starten und alle Apps schließen, die du nicht brauchst. Cloud-Sync
  im Hintergrund hat bei mir den Lüfter laufen lassen.
- **Mikrofon:** direkt am Rechner, **kein USB-Hub**. Alle Effekte in der Mikrofon-App
  aus, Verstärkung von Hand und gesperrt. Am besten an einem Tischarm, dann bleibt die
  Position gleich.
- **Abstand:** ca. 20 cm (Handbreite plus zwei Finger), leicht seitlich vorbei sprechen,
  vor jedem Take nachmessen. Über eine Session rutscht man sonst unmerklich nach hinten.
- **Trinken:** stilles Wasser in Zimmertemperatur. Kein Sprudel, keine Zitrone.
  Ein paar Bissen grüner Apfel vor dem Start lösen den Speichelfilm.
- **Pausen:** Takes von 7–8 Minuten, nach einer Stunde 10–15 Minuten Pause, nach zwei
  Stunden Schluss. Mit der Zeit wird der Mund trocken, und die Mundgeräusche steigen.
- **Reparieren hilft nicht.** Audiofilter, Mehrband-Kompressor, eigener De-Clicker:
  Jede Reparatur nimmt der Stimme etwas weg, und der Klon lernt das mit. Lieber zehn
  Minuten testen als zehn Stunden reparieren.

---

## Zielwerte

| Kennwert | Ziel |
|---|---|
| Rauschabstand | ≥ 45 dB |
| Raum in Stille | ca. −70 bis −85 dBFS (deutlich darunter = Denoiser aktiv) |
| Sprechspitzen | um −7 dBFS, kein Clipping |
| Mundgeräusche | ≤ 20 pro Minute |
| Pegel über alle Takes | möglichst gleich |

ElevenLabs verlangt mindestens 30 Minuten Sprache für einen Professional Voice Clone,
empfohlen sind 1–3 Stunden. Den PVC gibt es ab dem Tarif „Creator“. Ein teurerer Tarif
macht den Klon nicht besser, die Qualität hängt am Material.

---

## Voraussetzungen

macOS, Python 3, Homebrew, ein USB-Mikrofon. Getestet mit Shure MV7+ und MOTIV Mix.

## Lizenz

MIT, siehe [LICENSE](LICENSE).
