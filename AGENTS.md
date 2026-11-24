# Hinweise für Coding-KIs

- **Einzeldatei & Standardbibliothek:** Die Anwendung besteht aus einer einzigen Datei `SwiftSlateJMKEdition.pyw` (Python 3.10+, Windows 10/11). Es dürfen ausschließlich Module der Python-Standardbibliothek verwendet werden (`tkinter` ist erlaubt, aber nur lazy innerhalb von Funktionen importieren).
- **Pre-Commit-Hook:** Vor dem ersten Commit `git config core.hooksPath .githooks` ausführen, damit die SHA256-Pins automatisch aktuell bleiben.
- **Testbare Logik:** Neue Logik als reine Funktionen auf Modulebene (ohne Win32-Aufrufe) schreiben und Tests in `tests/` per `ast`-Loader anlegen (wie in `tests/test_api_utils.py`).
- **Prüfbefehle:**
  - `python -m py_compile SwiftSlateJMKEdition.pyw`
  - `python -m unittest discover -s tests -v`
  - `pyflakes SwiftSlateJMKEdition.pyw`
  - `ruff check --select F,E9,B,UP024,UP041,PLW1510 SwiftSlateJMKEdition.pyw`
- **Sicherheit & Datenschutz:** Niemals API-Keys, `config.json` oder echte Endpoints mit Zugangsdaten committen. Keys niemals loggen oder in Benachrichtigungen anzeigen.
- **Sprache:** Neue Oberflächentexte auf Deutsch. Bestehende englische Meldungen nur ändern, wenn ein Issue es ausdrücklich verlangt.
