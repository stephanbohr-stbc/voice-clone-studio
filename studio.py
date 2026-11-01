#!/usr/bin/env python3
"""Aufnahme-Studio im Browser.

Die Seite ist Bedienpult und Prompter - aufgenommen wird sie NICHT.
Das erledigt sox auf der Serverseite, roh in 24 Bit / 48 kHz / mono.
(Nicht ffmpeg/avfoundation: das verliert Samples, hoerbar als elektronisches
Knacken - 170/min gegen 11/min bei sox im Paralleltest vom 31.10.2026.)

Grund: Der Browser wuerde ueber getUserMedia automatisch Verstaerkungsregelung,
Rauschunterdrueckung und Echokompensation anlegen und obendrein resampeln.
Genau diese Bearbeitung darf im Trainingsmaterial nicht landen - der Klon
lernt sie sonst mit. Deshalb liefert der Browser nur Knoepfe, Text und Anzeige.

Start:  ./studio.py      (oeffnet den Browser von selbst)
"""

import atexit, http.server, json, math, os, re, signal, subprocess, sys, threading, time, urllib.parse, wave, webbrowser

HIER   = os.path.dirname(os.path.abspath(__file__))
MIC    = os.environ.get("VC_MIC", "Shure MV7+")   # zur Laufzeit ueber die Oberflaeche aenderbar
WUNSCH = os.environ.get("VC_WUNSCH", "Shure MV7+")   # Geraet, mit dem trainiert werden soll
TAKES  = os.path.expanduser(os.environ.get("VC_TAKES", "~/Music/VoiceClone-Takes"))
TEXTE  = [os.path.join(HIER, "sprechtexte"),
          os.path.expanduser(os.environ.get("VC_TEXTE", "~/Music/VoiceClone-Texte"))]
PORT   = int(os.environ.get("VC_PORT", "8765"))
MARKE  = "vc_studio_meter"   # damit eigene ffmpeg-Prozesse wiederfindbar sind

# ---------------------------------------------------------------- Audio-Motor

class Motor:
    """Haelt genau einen ffmpeg-Prozess: entweder nur Messung oder Messung + Aufnahme."""

    def __init__(self):
        self.pr = None
        self.pegel = -90.0
        self.datei = None          # Zieldatei des laufenden Takes
        self.start = None          # Beginn des aktuellen Abschnitts
        self.gelaufen = 0.0        # Sekunden aus bereits beendeten Abschnitten
        self.abschnitte = []       # Teildateien, am Ende zusammengefuegt
        self.pausiert = False
        self.marken = []           # Zeitstempel von Versprechern
        self.lock = threading.Lock()

    def sekunden(self):
        laufend = (time.time() - self.start) if (self.start and not self.pausiert) else 0
        return self.gelaufen + laufend

    def geraete(self):
        """Alle Audio-Eingaenge, die avfoundation kennt."""
        r = subprocess.run('ffmpeg -f avfoundation -list_devices true -i "" 2>&1',
                           shell=True, capture_output=True, text=True)
        txt = (r.stdout + r.stderr).split("AVFoundation audio devices")[-1]
        raus = []
        for ln in txt.splitlines():
            m = re.search(r"\[(\d+)\]\s+(.*?)\s*$", ln)
            if m and not m.group(2).startswith("["):
                raus.append({"index": int(m.group(1)), "name": m.group(2)})
        return raus

    def mic_index(self):
        for g in self.geraete():
            if MIC.lower() in g["name"].lower():
                return g["index"]
        return None

    def mic_name(self):
        for g in self.geraete():
            if MIC.lower() in g["name"].lower():
                return g["name"]
        return None

    def _lauf(self, datei=None):
        name = self.mic_name()
        if name is None:
            return None
        # sox liefert rohe 24-Bit-Samples, Python schreibt die WAV und misst mit
        cmd = ["rec", "-q", "-t", "raw", "-e", "signed-integer", "-b", "24",
               "-c", "1", "-r", "48000", "-"]
        pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                              env=dict(os.environ, AUDIODEV=name), start_new_session=True)
        self.leser = threading.Thread(target=self._lesen, args=(pr, datei), daemon=True)
        self.leser.start()
        return pr

    def _lesen(self, pr, datei=None):
        w = None
        if datei:
            w = wave.open(datei, "wb")
            w.setnchannels(1); w.setsampwidth(3); w.setframerate(48000)
        try:
            while True:
                buf = pr.stdout.read(4800 * 3)          # 0,1 s
                if not buf:
                    break
                if w:
                    w.writeframes(buf)
                spitze = max((abs(int.from_bytes(buf[i:i + 3], "little", signed=True))
                              for i in range(0, len(buf) - 2, 3)), default=0)
                self.pegel = 20 * math.log10(spitze / 8388608) if spitze else -90.0
        finally:
            if w:
                w.close()

    def messen(self):
        with self.lock:
            if self.pr and self.datei is None:
                return True
            self._stopp()
            self.pr = self._lauf()
            return self.pr is not None

    def aufnehmen(self, block):
        with self.lock:
            self._stopp()
            os.makedirs(TAKES, exist_ok=True)
            n = 1
            while os.path.exists(os.path.join(TAKES, f"{block}-{n:02d}.wav")):
                n += 1
            self.datei = os.path.join(TAKES, f"{block}-{n:02d}.wav")
            self.gelaufen = 0.0
            self.abschnitte = []
            self.marken = []
            self.pausiert = False
            teil = self.datei.replace(".wav", ".teil01.wav")
            self.pr = self._lauf(teil)
            if self.pr is None:
                self.datei = None
                return None
            self.abschnitte.append(teil)
            self.start = time.time()
            return self.datei

    def pausieren(self):
        """Abschnitt sauber schliessen. Der naechste wird spaeter angehaengt."""
        with self.lock:
            if not self.datei or self.pausiert:
                return False
            self.gelaufen += time.time() - self.start
            self._stopp()
            self.pausiert = True
            self.start = None
        time.sleep(0.4)
        self.messen()
        return True

    def fortsetzen(self):
        with self.lock:
            if not self.datei or not self.pausiert:
                return False
            self._stopp()
            teil = self.datei.replace(".wav", f".teil{len(self.abschnitte)+1:02d}.wav")
            self.pr = self._lauf(teil)
            if self.pr is None:
                return False
            self.abschnitte.append(teil)
            self.pausiert = False
            self.start = time.time()
            return True

    def marke(self):
        """Versprecher merken - die Stelle findet man spaeter sofort wieder."""
        if self.datei:
            self.marken.append(round(self.sekunden(), 1))
            return self.marken[-1]
        return None

    def _stopp(self):
        if self.pr:
            try:
                os.killpg(os.getpgid(self.pr.pid), signal.SIGINT)
                self.pr.wait(timeout=5)
                self.leser.join(timeout=5)   # WAV-Header ist erst danach geschrieben
            except Exception:
                try: os.killpg(os.getpgid(self.pr.pid), signal.SIGKILL)
                except Exception:
                    try: self.pr.kill()
                    except Exception: pass
        self.pr = None
        self.pegel = -90.0

    def beenden(self):
        with self.lock:
            ziel = self.datei
            teile = list(self.abschnitte)
            marken = list(self.marken)
            if self.start and not self.pausiert:
                self.gelaufen += time.time() - self.start
            self._stopp()
            self.datei = None; self.start = None
            self.abschnitte = []; self.pausiert = False; self.gelaufen = 0.0
        time.sleep(0.6)          # ffmpeg den WAV-Header schreiben lassen
        if not ziel:
            return None, marken
        teile = [t for t in teile if os.path.exists(t) and os.path.getsize(t) > 1000]
        if not teile:
            return None, marken
        if len(teile) == 1:
            os.rename(teile[0], ziel)
        else:
            liste = ziel + ".liste"
            with open(liste, "w") as f:
                for t in teile:
                    f.write(f"file '{t}'\n")
            r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                                "-f", "concat", "-safe", "0", "-i", liste,
                                "-c", "copy", ziel], capture_output=True)
            os.remove(liste)
            if r.returncode == 0:
                for t in teile: os.remove(t)
            else:
                os.rename(teile[0], ziel)      # Notnagel: wenigstens der erste Abschnitt
        return ziel, marken


MOTOR = Motor()

# ------------------------------------------------------------------ Auswertung

def pruefen(datei):
    """Dieselben Kennzahlen wie `vc check`, als JSON fuer die Seite."""
    def ff(af, extra=None):
        cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", datei]
        if extra: cmd += extra
        cmd += ["-af", af, "-f", "null", "-"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.stdout + r.stderr

    erg = {"datei": os.path.basename(datei)}
    try:
        erg["minuten"] = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", datei], capture_output=True, text=True).stdout.strip()) / 60
    except Exception:
        erg["minuten"] = 0.0

    t = ff("astats")
    m = re.findall(r"Peak level dB:\s*(-?[\d.]+)", t)
    erg["spitze"] = float(m[0]) if m else None

    t = ff("ebur128")
    m = re.findall(r"I:\s+(-?[\d.]+)\s+LUFS", t)
    erg["lufs"] = float(m[-1]) if m else None

    # Rauschabstand: leiseste gegen 90. Perzentil der Sekundenpegel
    t = ff("asetnsamples=n=48000:p=0,astats=metadata=1:reset=1,"
           "ametadata=print:key=lavfi.astats.1.RMS_level")
    v = sorted(float(x) for x in re.findall(r"RMS_level=(-?[\d.]+)", t))
    if len(v) >= 5:
        erg["rauschen"] = v[0]
        erg["snr"] = v[int(len(v) * 0.9)] - v[0]
    else:
        erg["rauschen"] = erg["snr"] = None

    erg["mund"] = mundgeraeusche(datei)
    return erg


def mundgeraeusche(datei):
    """Knackser pro Minute, gemessen auf Sendepegel (-16 LUFS)."""
    tmp = "/tmp/vc_studio_mund.wav"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", datei,
                        "-ac", "1", "-ar", "48000",
                        "-af", "loudnorm=I=-16:TP=-1.5,highpass=f=2000",
                        "-c:a", "pcm_s16le", tmp], capture_output=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        return None
    import wave, struct, statistics
    w = wave.open(tmp); n = w.getnframes(); sr = w.getframerate()
    d = struct.unpack(f"<{n}h", w.readframes(n)); win = int(sr * 0.005)
    e = [(sum(x * x for x in d[i:i+win]) / win) ** 0.5 for i in range(0, n - win, win)]
    if len(e) < 10:
        return None
    med = statistics.median([x for x in e if x > 0] or [1]); c = 0
    for i in range(2, len(e) - 2):
        u = statistics.median(e[i-2:i+3])
        if e[i] > max(u * 6, med * 3) and e[i-1] < e[i] * 0.5 and e[i+1] < e[i] * 0.6:
            c += 1
    return round(c / (len(e) * 0.005) * 60, 1)


def texte():
    raus = []
    for ordner in TEXTE:
        if not os.path.isdir(ordner):
            continue
        for f in sorted(os.listdir(ordner)):
            if not f.endswith(".txt"):
                continue
            p = os.path.join(ordner, f)
            try:
                w = len(open(p, encoding="utf-8").read().split())
            except Exception:
                continue
            name = f[:-4]
            if any(r["name"] == name for r in raus):
                continue
            raus.append({"name": name, "pfad": p, "woerter": w,
                         "minuten": round(w / 130, 1)})
    return raus


def material():
    import glob
    ges = 0.0
    for f in glob.glob(os.path.join(TAKES, "*.wav")):
        try:
            d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                      "format=duration", "-of", "csv=p=0", f],
                                     capture_output=True, text=True).stdout.strip())
            if d >= 30:
                ges += d
        except Exception:
            pass
    return round(ges / 60, 1)

# ---------------------------------------------------------------------- Server

class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"      # Safari braucht sauberes keep-alive

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)

        if u.path == "/":
            b = open(os.path.join(HIER, "studio.html"), "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            # sonst zeigt der Browser nach einem Update die alte Seite
            self.send_header("Cache-Control", "no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        elif u.path == "/api/blocks":
            self._json({"texte": texte(), "material": material(),
                        "mikro": MIC, "gefunden": MOTOR.mic_index() is not None})

        elif u.path == "/api/text":
            name = q.get("block", [""])[0]
            for t in texte():
                if t["name"] == name:
                    self._json({"text": open(t["pfad"], encoding="utf-8").read()})
                    return
            self._json({"text": ""}, 404)

        elif u.path == "/api/geraete":
            self._json({"geraete": MOTOR.geraete(), "aktuell": MIC, "wunsch": WUNSCH,
                        "gefunden": MOTOR.mic_index() is not None})

        elif u.path == "/api/pegel":
            self._json({"pegel": round(MOTOR.pegel, 1),
                        "aufnahme": MOTOR.datei is not None,
                        "pausiert": MOTOR.pausiert,
                        "marken": len(MOTOR.marken),
                        "sekunden": round(MOTOR.sekunden(), 1)})

        elif u.path == "/api/meter":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            # Safari gibt den Strom erst nach ein paar Kilobyte frei
            self.wfile.write(b": " + b"-" * 2048 + b"\n\n")
            self.wfile.flush()
            try:
                while True:
                    if getattr(self.connection, "_closed", False): break
                    d = {"pegel": round(MOTOR.pegel, 1),
                         "aufnahme": MOTOR.datei is not None,
                         "pausiert": MOTOR.pausiert,
                         "marken": len(MOTOR.marken),
                         "sekunden": round(MOTOR.sekunden(), 1)}
                    self.wfile.write(f"data: {json.dumps(d)}\n\n".encode())
                    self.wfile.flush()
                    time.sleep(0.1)
            except Exception:
                pass
            finally:
                self.close_connection = True
        else:
            self._json({"fehler": "unbekannt"}, 404)

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        laenge = int(self.headers.get("Content-Length") or 0)
        daten = json.loads(self.rfile.read(laenge) or "{}")

        if u.path == "/api/geraet":
            global MIC, WUNSCH
            MIC = daten.get("name", MIC)
            if daten.get("als_referenz"):      # dieses Geraet ist ab jetzt das richtige
                WUNSCH = MIC
            MOTOR.messen()
            self._json({"aktuell": MIC, "gefunden": MOTOR.mic_index() is not None,
                        "warnung": None if MIC == WUNSCH else
                                   f"Trainiert wird mit {WUNSCH}. Takes mit einem anderen "
                                   f"Mikro gehoeren NICHT ins Material."})

        elif u.path == "/api/pause":
            self._json({"pausiert": MOTOR.pausieren()})

        elif u.path == "/api/weiter":
            self._json({"laeuft": MOTOR.fortsetzen()})

        elif u.path == "/api/marke":
            self._json({"bei": MOTOR.marke(), "anzahl": len(MOTOR.marken)})

        elif u.path == "/api/messen":
            self._json({"ok": MOTOR.messen()})

        elif u.path == "/api/start":
            d = MOTOR.aufnehmen(daten.get("block", "take"))
            self._json({"datei": os.path.basename(d) if d else None})

        elif u.path == "/api/stop":
            d, marken = MOTOR.beenden()
            if not d or not os.path.exists(d):
                self._json({"fehler": "keine Datei"}, 400); return
            erg = pruefen(d)
            erg["material"] = material()
            erg["marken"] = marken
            MOTOR.messen()
            self._json(erg)
        else:
            self._json({"fehler": "unbekannt"}, 404)


def altlasten_raeumen():
    """ffmpeg-Prozesse aus einem abgestuerzten Vorlauf toeten.

    Sonst halten zwei Prozesse gleichzeitig das Audiogeraet und alles haengt.
    """
    r = subprocess.run(["pgrep", "-f", "rec -q -t raw -e signed-integer"],
                       capture_output=True, text=True)
    pids = [int(x) for x in r.stdout.split() if x.strip().isdigit() and int(x) != os.getpid()]
    for pid in pids:
        try: os.kill(pid, signal.SIGKILL)
        except Exception: pass
    if pids:
        print(f"  {len(pids)} verwaiste ffmpeg-Prozesse beendet.")
        time.sleep(0.7)


def main():
    altlasten_raeumen()
    atexit.register(lambda: MOTOR.beenden())
    for sig in (signal.SIGTERM, signal.SIGHUP):
        try: signal.signal(sig, lambda *a: (MOTOR.beenden(), sys.exit(0)))
        except Exception: pass
    if MOTOR.mic_index() is None:
        print(f"  Achtung: '{MIC}' nicht am USB gefunden - anschliessen und Seite neu laden.")
    MOTOR.messen()
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}/"
    print(f"  Studio laeuft auf {url}")
    print(f"  Takes landen in {TAKES}")
    print("  Ctrl-C beendet.\n")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        MOTOR.beenden()
        print("\n  beendet.")


if __name__ == "__main__":
    main()
