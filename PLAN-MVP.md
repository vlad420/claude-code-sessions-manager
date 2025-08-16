# MVP — Automatizare sesiuni Claude Pro (5h / ~45 mesaje)

## Context

Ai planul Pro care oferă ferestre de 5 ore cu ~45 de mesaje. Vrei să optimizezi folosirea acestor ferestre prin activarea automată a sesiunilor și o evidență clară a timpului și a numărului de sesiuni/zi, astfel încât să poți rula aproape non-stop cu monitorizare și strategie.

## Obiectiv

Un MVP local pe macOS care:

- pornește automat o nouă sesiune la fiecare 5 ore sau la comandă;
- păstrează un istoric al sesiunilor (număr, început, sfârșit, durată, notițe);
- afișează timpul scurs în format **h:mm** și timpul estimat până la reset;
- oferă un status rapid privind “fereastra” curentă și apropierea de limită;
- rulează 100% local, fără a depinde de UI-ul aplicației desktop.

## Arhitectură (high-level)

1. **Activator sesiune (kicker)** — declanșează o nouă sesiune trimițând un mesaj “ping” minim către Claude Code și loghează startul în baza de date locală.
2. **Status Poller** — interoghează la cerere sau periodic starea ferestrei (ex. “în fereastra curentă”, “aproape de limită”) și salvează instantanee.
3. **Scheduler** — un LaunchAgent macOS care rulează la interval regulat (ex. 5 minute) și decide dacă trebuie pornită o nouă sesiune (>=5h de la start).
4. **CLI minimal** — comenzi pentru utilizator: `start-now`, `status`, `log`. (Descriere conceptuală; implementarea efectivă a codului nu este inclusă aici.)
5. **Afișaj rapid (opțional)** — un plugin de tip menubar (ex. SwiftBar) care prezintă starea: `Claude: S#<n> <h:mm> / <h:mm>`.

## Flux de lucru

- La prima utilizare te autentifici în Claude Code și pornești manual o sesiune (“aliniere” a ferestrei cu programul tău).
- Scheduler-ul verifică periodic: dacă nu există sesiune activă sau au trecut 5 ore, pornește automat următoarea.
- Poți declanșa oricând manual o nouă sesiune pentru a realinia fereastra înainte de un sprint.
- Statusul curent este disponibil instant (număr sesiune, timp scurs, timp rămas).

## Date și metrici urmărite

- **sessions**: id sesiune, start, end (opțional), durată, notă.

## Funcționalități cheie în MVP

- **Start automat la 5h**: la expirarea ferestrei precedente.
- **Start la comandă**: forțezi o nouă sesiune pentru a te încadra într-un orar.
- **Status**: afișarea concisă a sesiunii curente în terminal/menubar.

## UX minimal

- **Terminal**: comanda `status` returnează `#<session_no>  elapsed h:mm  (eta reset HH:MM)`.
- **Menubar (opțional)**: etichetă concisă + meniu cu acțiuni („Start now”, „Open log”).

## Strategia de optimizare

1. **Aliniere**: pornești prima sesiune la ora la care vrei să devină “ritmul” de 5h (ex. 08:00).
2. **Cadentă**: la fiecare ~5h se creează automat o sesiune nouă; când ai un sprint important, o pornești manual chiar înainte.
3. **Monitorizare**: urmărești h:mm scurs și istoricul pentru a identifica intervalele în care valorifici cel mai bine fereastra.
4. **Ajustări**: dacă sesiunile tind să “cadă” în ore nepotrivite, folosește `start-now` pentru a realinia ciclul.

## Extensii după MVP

- **v1.1**: export CSV al sesiunilor (număr, start, end, durată, mesaje estimate).
- **v1.2**: dashboard web local (FastAPI) cu grafic al sesiunilor și al utilizării.
- **v2**: integrare OpenTelemetry → Prometheus/Grafana sau servicii managed pentru alerte și vizualizări.
- **v2.1**: fallback pentru trimiterea “ping”-ului via AppleScript către aplicația desktop (doar dacă e necesar, UI-dependent).

## Considerații & limite

- Scopul este **programarea inteligentă** a ferestrelor, nu ocolirea limitelor.
- Mesajele “ping” consumă minim din bugetul de mesaje, dar contează în fereastră.
- Automatizarea prin CLI este mai robustă decât scripting de UI; aplicația desktop rămâne opțională.
- Păstrează log-uri locale și respectă politica de utilizare a serviciului.

## Pași concreți de început (fără cod)

1. **Instalare și autentificare** în Claude Code pe macOS (o singură dată).
2. **Inițializare date locale**: creezi un fișier/bază de date simplă pentru sesiuni (ex. SQLite sau CSV).
3. **Configurare scheduler**: setezi un LaunchAgent macOS care rulează periodic un script “tick” (verifică dacă au trecut 5h; dacă da, pornește o nouă sesiune și loghează).
4. **Comenzi utilizator**: definești trei acțiuni – „pornește acum”, „status”, „istoric” – accesibile din terminal.
5. **(Opțional) Menubar**: instalezi un utilitar de tip SwiftBar/BitBar și adaugi un plugin minimal care citește statusul.
6. **Test & ajustare**: pornești manual prima sesiune, verifici că după 5h se creează automat următoarea, rafinezi mesajul „ping” și frecvența verificării.
