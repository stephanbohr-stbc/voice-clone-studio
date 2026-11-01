#!/bin/bash
# Akustische Ansagen ums Aufnehmen herum. Wichtig: die Ansage laeuft VOR dem
# Start und NACH dem Ende - waehrend der Aufnahme ist Ruhe, sonst nimmt das
# Mikrofon die Stimme des Rechners mit auf.
sage() { say -v Anna -r 190 "$1" 2>/dev/null; }

aufnehmen() {   # $1=Zieldatei  $2=Sekunden  $3=Geraeteindex  $4=Ansagetext
  sage "$4"
  sage "Start in drei, zwei, eins"
  sleep 1.2                       # Nachhall der Ansage abklingen lassen
  ffmpeg -hide_banner -loglevel warning -y -f avfoundation -i ":$3" \
         -t "$2" -ac 1 -ar 48000 -sample_fmt s32 -c:a pcm_s24le "$1" 2>"${1%.wav}.log"
  sage "Fertig"
}
