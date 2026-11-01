# Installation

macOS. Alles zusammen etwa 20 Minuten.

---

## 1. Homebrew

Falls noch nicht vorhanden:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## 2. Pflicht-Werkzeuge

```bash
brew install sox ffmpeg switchaudio-osx
```

- **sox** — Aufnahme (direkt über CoreAudio, verliert keine Samples)
- **ffmpeg** — Messung und Umwandlung
- **switchaudio-osx** — damit `vc` den Systemeingang selbst auf das Mikro schalten kann

Python 3 bringt macOS mit. Falls `python3` fehlt: `brew install python`.

## 3. Mikrofon-Software

**Shure MV7+ (und neuere Shure-USB-Mikros):** Die App heißt **MOTIV Mix** und kommt
direkt von Shure: <https://www.shure.com/en-US/support/downloads/software-firmware-archive/motiv-mix>

**Älteres Shure MV7 / MV88+:** Die alte App „ShurePlus MOTIV“ geht noch über Homebrew:

```bash
brew install --cask shureplus-motiv
```

Ab Werk sind beim MV7+ automatischer Pegel, Echtzeit-Denoiser, Popper Stopper und
Limiter **eingeschaltet**. Alles ausschalten, Verstärkung von Hand setzen und mit dem
Schloss sperren. Der Denoiser drückt sonst die Sprechpausen auf digitale Stille, und
der Klon lernt dieses Pumpen mit.

Bei anderen Mikrofonen: die Herstellersoftware, falls das Mikro einen eigenen DSP hat
(Rode NT-USB, Elgato Wave, Blue Yeti …). Bei XLR-Mikro am Interface entfällt das.

---

## 4. Teleprompter

Ohne Prompter liest man 100 Minuten Text vom Blatt — das hört man dem Ergebnis an.

| Option | Kosten | Anmerkung |
|---|---|---|
| **Teleprompter App** (Setapp) | im Setapp-Abo | Wurde hier benutzt, funktioniert gut |
| **cueprompter.com** | kostenlos | Läuft im Browser, nichts zu installieren. Für den Zweck völlig ausreichend |
| Mac App Store, Suche „Teleprompter" | 0–20 € | Mehrere brauchbare Apps, Qualität schwankt |
| Notfalls: Textdatei in großer Schrift | kostenlos | Manuell scrollen, funktioniert, ist aber unruhiger |

**Wenn kein Setapp vorhanden ist: cueprompter.com nehmen.** Text reinkopieren,
Geschwindigkeit einstellen, fertig.

### Einstellungen, die den Klang entscheiden

- **Langsamer als das Bauchgefühl sagt.** Wer dem Prompter hinterherliest, hebt am
  Zeilenende die Stimme — und genau das lernt der Klon mit.
- **Große Schrift, schmale Spalte.** Weniger Augenbewegung, ruhigerer Ton.
- **Prompter direkt hinter oder über dem Mikro**, nie seitlich. Jede Kopfdrehung
  ändert den Abstand zur Kapsel und damit den Pegel.
- Bei Versprecher: **Prompter anhalten**, kurz Pause, ganzen Satz neu.

---

## 5. Hardware-Empfehlung

- **Dynamisches Nahbesprechungsmikro** (Shure MV7, SM7B, SM58, Rode PodMic).
  Im nicht bedämpften Raum deutlich besser als ein Kondensator — es hört den Raum weniger.
- **Abstand 20–25 cm**, konstant. Position markieren (Klebeband am Tisch).
  **Nicht näher.** Bei Nahbesprechung unter 15 cm werden Lippen- und Zungengeräusche
  massiv überbetont — im Klon sind sie danach dauerhaft drin. Für Podcasts sind 5–12 cm
  richtig, für Klon-Training nicht.
- **Leicht off-axis** sprechen, ca. 10–15° am Mikro vorbei → weniger Plosive.
- **Pop-Schirm** zwingend.
- **Geschlossene Kopfhörer** — Mundgeräusche muss man live hören.
- Bei **XLR-Mikro mit wenig Ausgangspegel** (SM7B, SM58) am Interface: Cloudlifter CL-1
  oder Triton FetHead. Bei **USB-Mikros wie dem MV7 nicht nötig** — die haben einen
  eigenen Vorverstärker.

---

## 6. ElevenLabs-Konto

Tarif vorher prüfen — siehe Tabelle in der [README](README.md#voraussetzungen-an-den-elevenlabs-tarif).
Kurz: **Starter reicht nur für den Instant Clone. Der Professional Voice Clone
braucht Creator.**

API-Key (optional, für den Upload per Kommandozeile):
elevenlabs.io → Profilbild → *API Keys* → *Create API Key*

```bash
mkdir -p ~/.config/elevenlabs
printf 'sk_dein_key_hier' > ~/.config/elevenlabs/key
chmod 600 ~/.config/elevenlabs/key
```

Der Upload geht genauso gut über die Weboberfläche — der Key ist reiner Komfort.

---

## 7. Prüfen, ob alles steht

```bash
./vc doctor
```

Erwartete Ausgabe: Mikro gefunden, Systemeingang gesetzt, Herstellersoftware vorhanden.
