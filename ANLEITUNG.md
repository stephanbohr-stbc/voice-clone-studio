# Anleitung — vom leeren Studio zum fertigen Stimmklon

---

## Der Ablauf in einem Bild

```
Setup pruefen  ->  Mikro-DSP abschalten  ->  Rauschtest  ->  Pegel messen
      |
      v
Bloecke A-E einsprechen  ->  Takes pruefen  ->  Upload-Ordner  ->  ElevenLabs
```

Alles davon steckt im geführten Ablauf. Einfach starten:

```bash
./vc
```

Das Menü zeigt jederzeit, wie viele Minuten pro Block schon vorliegen und wie weit
es bis zum Ziel ist. Man kann jeden Schritt wiederholen und jederzeit aufhören.

---

## Schritt 1 — Mikrofon-DSP abschalten

**Das ist der Schritt, der am häufigsten vergessen wird und am meisten kaputt macht.**

Moderne USB-Mikros haben eine eingebaute Klangbearbeitung. Beim Shure MV7 in
ShurePlus MOTIV:

| Einstellung | Wert |
|---|---|
| Auto Level Mode | **AUS** → Manual Mode |
| EQ-Preset | **Flat** (nicht Dark, nicht Bright) |
| Limiter | **AUS** |
| Compressor | **AUS** |
| Mic Gain | manuell, siehe Schritt 3 |

**Warum:** Auto Level ist eine Regelautomatik, also Kompression. ElevenLabs lernt sie
mit. Das Ergebnis ist ein Klon, der in jedem Satz pumpt — und das bekommt man nie
wieder heraus, außer durch komplettes Neuaufnehmen.

Das Mikro merkt sich die Einstellung. Einmal setzen, dann nicht mehr anfassen.

---

## Schritt 2 — Rauschtest

```
vc  ->  2
```

20 Sekunden absolute Stille. Ziel: **Grundrauschen ≤ −65 dBFS**.

Vorher durchgehen:

- Lüftung und Klimaanlage aus
- Kühlschrank, Rechnerlüfter, externe Festplatten aus dem Raum oder aus
- Handys in den Flugmodus, auch die von anwesenden Personen
- Fenster zu, Straßenlärm prüfen
- Keine Uhr mit Sekundenzeiger, kein Heizungsknacken

**Nachts aufnehmen ist meistens unnötig.** Ein dynamisches Nahbesprechungsmikro hört
den Raum kaum. Statt zu raten: den Rauschtest zu der Tageszeit laufen lassen, zu der
man aufnehmen will. Und bedenken: nachts ist die Stimme müde — und genau die lernt
der Klon. Eine frische Stimme im ordentlichen Raum schlägt eine matte im perfekten.

---

## Schritt 3 — Pegel messen

```
vc  ->  3
```

12 Sekunden in normaler Vortragslautstärke sprechen. Das Werkzeug sagt dann, um wie
viele dB der Gain **im Mikro** (also in MOTIV) nachzustellen ist. Ziel: Sprechspitzen
um −7 dBFS.

**Die Systemlautstärke von macOS wirkt bei vielen USB-Mikros gar nicht auf das
Signal.** Wenn sich der Pegel beim Verstellen nicht bewegt, ist entweder das der
Grund — oder Auto Level Mode ist noch an.

Wenn der Wert sitzt: **notieren und über alle Sessions identisch halten.** Ein
Gain-Wechsel zwischen zwei Sessions ist der häufigste Grund für einen Klon, der
„ausgefranst" klingt.

---

## Schritt 4 — Einsprechen

### Sprechhaltung

Der Klon reproduziert **exakt** den Duktus, den du einsprichst: Tempo, Melodie,
Energie, Pausenlänge, Akzent. Nicht mehr und nicht weniger.

Also so sprechen, wie man später klingen will — wach und zugewandt. Nicht
Nachrichtensprecher, nicht Hörbuch-Einschlafmodus, nicht Marktschreier.

- Aufrecht sitzen oder stehen, Brustkorb frei
- **Abstand 20–25 cm**, nicht näher — siehe [INSTALLATION.md](INSTALLATION.md#5-hardware-empfehlung)
- Vorher 10 Minuten warmsprechen, nicht kalt starten
- **Gegen Mundgeräusche:** Wasser bei Zimmertemperatur, über die ganze Session verteilt
  trinken. Kein Kaffee, keine Milchprodukte in den zwei Stunden davor. Und der alte
  Sprecher-Trick: **ein Stück grüner Apfel** vor der Aufnahme bricht den Speichelfilm,
  der die Schnalzgeräusche verursacht
- Bei Versprecher: kurz Pause, **ganzen Satz neu**. Nicht mittendrin flicken
- **Atmer drin lassen.** Sie machen den Klon menschlich
- Pro Take 3–5 Minuten, dann absetzen. Nicht 40 Minuten durchziehen — die Stimme
  kippt und der Klon lernt die müde Version mit

### Die fünf Blöcke

| Block | Ziel | Inhalt | Quelle |
|---|---|---|---|
| **A** | 2 min | Phonetik: alle Laute, Umlaute, Cluster | `sprechtexte/block-a.txt` |
| **B** | 3 min | Zahlen, Kürzel, Anglizismen, Eigennamen | `sprechtexte/block-b.txt` |
| **C** | **40 min** | Narration, Fließtext | **eigene Inhalte** |
| **D** | **30 min** | Lehr-Duktus, Erklären, Ansprache | **eigene Inhalte** + `block-d.txt` |
| **E** | 3 min | Dynamik: Fragen, Betonung, Wärme | `sprechtexte/block-e.txt` |

**Rund 75 % des Materials sind eigene Inhalte.** Das ist kein Sparen, das ist besser:
Der Klon lernt genau das Vokabular, das er später sprechen muss.

Als Quelle für Block C und D eignen sich Broschüren, Curricula, Modulskripte,
Blogartikel, Handouts — alles, was ohnehin in der eigenen Sprache geschrieben ist.
Tabellen, Überschriften und Aufzählungen vorher entfernen, es soll sprechbarer
Fließtext sein.

### Hinweise pro Block

- **Block A** — ruhig und deutlich, aber nicht künstlich überartikuliert.
- **Block B** — Kürzel **einzeln buchstabieren**, jeden Buchstaben mit gleichem
  Nachdruck. A-Z-A-V, D-S-G-V-O, L-L-M. Das ist der Block, der dem Klon beibringt,
  nicht über Abkürzungen zu stolpern. Lieber langsam.
- **Block C** — der wichtigste. Er prägt den Duktus, in dem später fast alles läuft.
  Hier hetzen oder leiern heißt: für immer hetzen und leiern.
- **Block D** — etwas lebendiger als C, mehr Betonungsspitzen, mehr Pausen.
- **Block E** — Fragen müssen in der Melodie wirklich hochgehen, sonst klingt später
  jede generierte Frage wie eine Aussage.

### Optional: zwei getrennte Klone

Wer sehr unterschiedliche Anwendungen hat, legt besser zwei Stimmen an —
„Narration" (ruhig, Modul-Vertonung) und „Bühne" (energetisch, Trailer). Dann pro
Klon in genau diesem Duktus einsprechen. Für den ersten Durchlauf: erst mal einen.

---

## Schritt 5 — Kontrolle

```
vc  ->  9
```

Pro Take werden drei Dinge geprüft:

```
  block-c-01.wav   1.6 min
  OK    Clipping   keins
  OK    Spitze       -6.3 dBFS
        Lautheit    -28.4 LUFS
  OK    Rauschabstand    52 dB   (Ziel >= 45)   Rauschen -77 dBFS
```

**Zwei Zahlen entscheiden: Rauschabstand und Mundgeräusche.**

Die Lautheit wird nur informativ angezeigt — ElevenLabs normalisiert selbst, wichtig ist
nur, dass sie über alle Takes ähnlich ist.

**Warum Mundgeräusche auf −16 LUFS gemessen werden:** Rohaufnahmen liegen bei etwa
−26 LUFS. Auf diesem Pegel sind Lippen- und Zungengeräusche unter der Hörschwelle und
fallen beim Abhören nicht auf. ElevenLabs gibt aber rund −16 LUFS aus, also 10 dB
lauter — und dort sind sie deutlich hörbar. Wer nur auf Rohpegel kontrolliert, merkt
es erst am fertigen Klon. Genau das ist hier einmal passiert: 136 Minuten Material mit
durchgehend 38–63 Knacksern pro Minute, technisch einwandfrei nach allen anderen
Kriterien.

`vc check` prüft das jetzt automatisch. **Ziel: maximal 20 pro Minute.**

Takes mit Clipping wegwerfen und neu aufnehmen. Takes mit zu wenig Rauschabstand
ebenfalls — daran lässt sich nachträglich nichts reparieren.

---

## Schritt 6 — Upload-Ordner

```
vc  ->  10
```

Kürzt Pausen über 2 Sekunden, lässt Fehl-Takes unter 30 Sekunden weg und schreibt
alles nach `~/Music/VoiceClone-Takes/_upload/`.

**Sonst nichts bearbeiten.** Kein Denoise, keine Normalisierung, kein EQ.

---

## Schritt 7 — Bei ElevenLabs anlegen

### Instant Voice Clone

Braucht nur 1–3 Minuten Material und ist in zwei Minuten fertig. Gut als Hörprobe.

1. Voices → **Add Voice** → *Instant Voice Clone*
2. Dateien aus `_upload/` hineinziehen, Name und Sprache setzen
3. Fertig

**Für den Instant Clone Block A und B weglassen.** Pangramme und buchstabierte Kürzel
ziehen einen Instant Clone in Richtung „Rezitieren". Nimm C, D und E — die tragen den
Duktus, den du willst. (Beim PVC bleiben A und B drin, dort helfen sie.)

Falls die API genutzt wird: **maximal 11 MB pro Datei.** Rohe 24-Bit-WAVs sind dafür
zu groß, vorher nach MP3 192 kbps wandeln:

```bash
ffmpeg -i take.wav -ac 1 -ar 48000 -c:a libmp3lame -b:a 192k take.mp3
```

### Professional Voice Clone

1. Voices → **Add Voice** → *Professional Voice Clone*
2. Name, Sprache, alle Dateien aus `_upload/` hochladen
3. **Voice Captcha** — ElevenLabs blendet einen Satz ein, den man live einspricht.
   Das ist die Einwilligungsprüfung. **Mit demselben Mikro machen**, sonst kann die
   Verifikation fehlschlagen
4. Training starten: **3 bis 6 Stunden**, gelegentlich länger. Nicht neu starten

Für den Upload zählt die **Gesamtlaufzeit**, nicht die Zahl der Dateien. Sehr lange
Aufnahmen am besten in Abschnitten von rund 30 Minuten hochladen — `vc` legt ohnehin
Takes in dieser Größenordnung an.

### Einstellungen nach dem Training

| Parameter | Startwert | Warum |
|---|---|---|
| Modell | Eleven Multilingual v2 | stabilste Wahl für deutsche Narration |
| Stability | 40–50 % | zu hoch = monoton, zu niedrig = sprunghaft |
| Similarity | 75–85 % | über 90 % zieht Artefakte aus dem Material mit |
| Style Exaggeration | **0** | verschlechtert beim PVC fast immer die Ähnlichkeit |
| Speaker Boost | an | |

Testsatz, der alle Schwachstellen auf einmal trifft:

> Willkommen zum Modul vier. Wir sprechen heute über Agenten — also über Systeme,
> die nicht nur antworten, sondern handeln. Dauer: etwa fünfundzwanzig Minuten.
> Und ja: Sie brauchen dafür Ihren Laptop.

Wenn dieser Satz sitzt, sitzt der Klon.

---

## Wichtig: Räume nicht mischen

Wer die erste Hälfte im Studio und die zweite zu Hause aufnimmt, bringt dem Klon zwei
verschiedene Raumsignaturen bei — und er klingt danach in keiner von beiden richtig.

**Alles an einem Ort aufnehmen**, mit demselben Mikro, demselben Abstand und
demselben Gain. Wenn ein Ortswechsel unvermeidlich ist: vorher Rauschtest am neuen
Ort, und die Werte müssen vergleichbar sein.

---

## Eine Session nach Tagen oder Wochen fortsetzen

Der haeufigste Grund fuer einen ausgefransten Klon ist nicht schlechtes Material,
sondern **Material aus zwei verschiedenen Bedingungen**. Deshalb vor jeder
Folge-Session drei Werte gegen die erste Session pruefen:

| Wert | Woher | Toleranz |
|---|---|---|
| Grundrauschen des Raums | `vc` -> 2 | +/- 3 dB |
| Sprech-Pegel (Median RMS) | `vc` -> 3 bzw. Testaufnahme | +/- 1 dB |
| Rauschabstand | `vc` -> 9 nach dem ersten Take | +/- 3 dB |

Ablauf:

1. Mikro anschliessen, `vc` -> 1
2. **Rauschtest zuerst.** Weicht der Raum um mehr als 3 dB ab, erst die Ursache
   suchen — nicht einfach aufnehmen
3. Kurze Testaufnahme von einer Minute, Sprech-Pegel gegen den alten Wert halten.
   Nachgestellt wird **im Mikro** (MOTIV), nie an der Systemlautstaerke
4. Erst dann den richtigen Take starten, danach `vc` -> 9 zur Kontrolle

**Beim Shure MV7 guenstig:** Gain, EQ und die abgeschalteten DSP-Funktionen sind in
der Mikrofon-Firmware gespeichert und reisen mit dem Geraet. An einem anderen Rechner
stimmen die Einstellungen also weiterhin — nur den Raum muss man neu pruefen.

**Bei einem anderen Mikrofon-Modell:** nicht mischen. Der Unterschied zwischen zwei
Mikrofontypen ist deutlich groesser als jede Raumdifferenz. Dann lieber alles neu
aufnehmen.

## Rechtliches

- **Eigene Stimme, eigene Nutzung** → unkritisch. Das Voice Captcha dokumentiert die
  Einwilligung.
- **EU AI Act, Artikel 50** — Transparenzpflichten gelten seit dem 02.08.2026.
  KI-generierte Audio-Inhalte müssen maschinenlesbar gekennzeichnet und gegenüber
  Nutzern offengelegt werden. Für Bildungsträger kein Nebenschauplatz.
  Beispielhinweis: *„Die Sprachausgabe dieses Moduls wurde mit einem KI-Stimmklon der
  eigenen Stimme des Dozenten erzeugt."*
- **Stimme ist ein biometrisches Datum** (DSGVO Artikel 9). Bei der eigenen Stimme
  unproblematisch, aber sofort relevant, sobald **fremde Stimmen** geklont werden —
  dann Einwilligung, Zweckbindung und gegebenenfalls AVV.
- Trainingsdateien und Einwilligung ins QMS aufnehmen. Das ist ein prüffähiger Prozess.
