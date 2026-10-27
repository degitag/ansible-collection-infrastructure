# Telegraf-Keyring: Idempotenz und Rotation

Stand: 2026-10-27. Patchversion `degitag.infrastructure` 2.0.1. Der bereits veroeffentlichte Tag `v2.0.0` bleibt unveraendert.

## Befund und Korrektur

Die native Monitoring-Abnahme meldete auf Ubuntu 22.04, 24.04 und 26.04 bei identischer Wiederholung ausschliesslich den Task `Dearmor InfluxData archive key for Debian` als geaendert. Der bisherige Task lief bedingungslos bei aktiviertem Debian-Repository.

Die Rolle registriert jetzt das Download-Ergebnis und prueft den vorhandenen Keyring. Die Konvertierung laeuft bei einer Download-Aenderung oder einem fehlenden/leeren Keyring. Ein unveraenderter, vorhandener Keyring wird nicht neu geschrieben. Ein pauschales `creates` wird nicht verwendet, damit echte Schluesselrotation weiterhin wirkt. Oeffentliche Rollenvariablen und die RedHat-Implementierung bleiben erhalten.

## Lokaler Nachweis

`tests/unit/test_telegraf_keyring.py` verwendet die tatsaechlichen drei Rollentasks mit echten Ansible-Modulen, einem lokalen HTTP-Server und GPG. Alle Pfade liegen im temporaeren Testverzeichnis; es werden keine privaten Schluessel erzeugt und keine Host-Repositories geaendert. Die GPG-Armierung verwendet bewusst einfache Fixture-Bytes; dies ist ein Konvertierungs- und Ablaufnachweis, keine Signaturfreigabe eines Repository-Schluessels.

Gepruefte Ablaeufe: Erstinstallation, unveraenderte Wiederholung mit `changed=0`, Wiederherstellung eines fehlenden und eines leeren Keyrings, Rotation unter derselben URL, anschliessende Wiederholung mit `changed=0` und Repository-Verwaltung deaktiviert.

Der vollstaendige lokale Pruefeinstieg `bash tests/run_checks.sh` ist unter Python 3.12/Core 2.21 mit Exit 0 abgeschlossen: 90 Unit-Tests, Repository-/Scaffold-/YAML-Pruefung, Syntax, Production-Lint, Build/Artefakt/Installation und Sanity Compile/Import. Die native Bestaetigung wird mit dem Monitoring-Verantwortlichen auf dessen dedizierten Linux-Gaesten abgestimmt; dort werden echte InfluxData-Schluessel und die laufende Telegraf-Konfiguration verwendet. Der Releaseabschluss erfordert zusaetzlich die GitHub-Matrix und die Artefaktpruefung.
