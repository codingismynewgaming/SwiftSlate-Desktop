<div align="center">

<img src="assets/icon.png" alt="SwiftSlateJMKEdition Icon" width="96">

# SwiftSlateJMKEdition

**Systemweite KI Textbearbeitung für Windows.** Befehl wie `.fix` ans Textende tippen, kurz warten, Text wird ersetzt.

[![Release](https://img.shields.io/github/v/release/codingismynewgaming/SwiftSlateJMKEdition?style=flat-square)](https://github.com/codingismynewgaming/SwiftSlateJMKEdition/releases/latest)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=flat-square)](#installation)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

</div>

> [!NOTE]
> **Fork von [Musheer360/SwiftSlate-Desktop](https://github.com/Musheer360/SwiftSlate-Desktop).** Herzlichen Dank an [Musheer Alam](https://github.com/Musheer360) für das Original und die freie MIT Lizenz. Gefällt dir das Tool, gib bitte auch dem Original einen ⭐.

## Unterschiede zum Original

- Auslöser `.befehl` mit Leerzeichen davor (`Text .fix`) statt `?befehl`. Satzpunkte, `3.5` oder URLs lösen nicht aus.
- Tipp Pause vor dem Auslösen (Standard 1 s, 0 bis 5000 ms). Weitertippen bricht ab.
- Deutsche Standardbefehle.
- Einstellungsfenster (tkinter) mit Befehls Editor für Befehle und Prompts.
- OpenAI kompatible Schnittstelle als Standard im Installer, Endpoint und Modell frei, Key optional (z. B. für Ollama).
- Hot Reload behält bei fehlerhafter Config den letzten gültigen Stand.
- Kurze Wiederholung bei HTTP 429, `<think>` Blöcke von Reasoning Modellen werden entfernt.
- Eigenes Icon für Tray und Fenster.
- Neuer Installer aus dem Release mit SHA256 Prüfung, ohne `irm | iex`, übernimmt eine ältere Installation.
- Tray Icon reagiert korrekt auf Klick, Doppelklick und Rechtsklick.

## Installation

Voraussetzung: Windows 10/11, Python 3.10+ mit tkinter (fehlt Python, installiert der Installer es per winget). In einer normalen PowerShell ohne Adminrechte:

```powershell
cd $env:USERPROFILE\Downloads
Invoke-WebRequest https://github.com/codingismynewgaming/SwiftSlateJMKEdition/releases/download/v1.1.0/Install-SwiftSlateJMKEdition.ps1 -OutFile Install-SwiftSlateJMKEdition.ps1 -UseBasicParsing
powershell -ExecutionPolicy Bypass -File .\Install-SwiftSlateJMKEdition.ps1 -Endpoint https://api.example.com/v1 -Model modellname
```

Der Key wird verdeckt abgefragt. Prüfsummen stehen im [Release](https://github.com/codingismynewgaming/SwiftSlateJMKEdition/releases/latest). Weitere Schalter: `-SetKey`, `-ResetConfig`, `-ResetCommands`, `-NoAutostart`, `-Uninstall`.

## Bedienung

- Text tippen, ` .befehl` anhängen, 1 Sekunde warten.
- Klick oder Doppelklick auf das Tray Icon öffnet die Einstellungen, Rechtsklick zeigt das Menü (Einstellungen, Beenden).
- Änderungen an Einstellungen und Befehlen gelten sofort, ohne Neustart.

## Befehle

| Befehl | Wirkung |
|:--|:--|
| `.fix` | Rechtschreibung und Grammatik korrigieren |
| `.kurz` | Text kürzen |
| `.en` / `.de` | Ins Englische / Deutsche übersetzen |
| `.höflich` / `.hoeflich` | Höflich umformulieren |
| `.locker` | Locker formulieren |
| `.besser` | Klarheit verbessern |
| `.mensch` | Natürlich und menschlich formulieren |
| `.antwort` | Kurze Antwort auf eine Nachricht |
| `.datum` / `.zeit` | Datum / Uhrzeit einfügen |
| `.translate:XX` | In Sprache XX übersetzen, z. B. `.translate:es` |
| `.undo` | Letzte Ersetzung rückgängig |
| `.copy` `.cut` `.paste` `.replace` | Interne Zwischenablage |

Eigene Befehle legst du im Einstellungsfenster an.

## Konfiguration

Dateien liegen in `%LOCALAPPDATA%\SwiftSlateJMKEdition\app` (`config.json`, `commands.json`). Minimalbeispiel:

```json
{
  "provider": "custom",
  "endpoint": "https://api.example.com/v1",
  "model": "modellname",
  "api_keys": []
}
```

Texte gehen nur an die eingestellte Schnittstelle, es gibt keine Telemetrie. Fehlersuche: `SwiftSlateJMKEdition.pyw --debug` schreibt nach `debug.log`. Beiträge siehe [CONTRIBUTING.md](CONTRIBUTING.md).

## Lizenz und Dank

MIT Lizenz, siehe [LICENSE](LICENSE). Original © Musheer Alam, [SwiftSlate-Desktop](https://github.com/Musheer360/SwiftSlate-Desktop). Danke, Musheer!
