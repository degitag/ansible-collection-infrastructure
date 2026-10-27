# Mitarbeit an degitag.infrastructure

Der [gemeinsame Repository-Standard](docs/repository-standard.md) beschreibt Struktur, Review-Grenzen und Pruefvertrag. Die Collection verwaltet Linux-Hosts; Kubernetes, Datenbank-HA und Monitoring haben eigene Collections. Bestehende lokale Aenderungen anderer Arbeiten erhalten.

## Lokale Einrichtung

Auf macOS Homebrew Python 3.12 ohne sudo verwenden:

```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv
make prepare
```

Unter Linux die `.venv` mit `python3.12 -m venv .venv` anlegen. Die Tools verwenden danach die `.venv`. `requirements.yml` enthaelt Laufzeit-Collections, `requirements-dev.yml` nur Testabhaengigkeiten. `make prepare` installiert diese explizit; Checks installieren keine ungeprueften Controller-Werkzeuge nach.

## Implementierung und Review

Oeffentliche Rollen-APIs, Beispiele, Beschreibungen und Betreiberhinweise in `tools/role_scaffold_config.yml` pflegen, fachliche Tasks in `roles/<rolle>/tasks/configuration.yml`. Plattformdetails gehoeren in `vars/platform/`. Oeffentliche Variablen werden typisiert und dokumentiert. Zur Bearbeitung beispielsweise `vim tools/role_scaffold_config.yml` verwenden.

```bash
.venv/bin/python tools/generate_role_scaffold.py
.venv/bin/python tools/format_yaml.py
make ci
```

`make ci` und `make test` rufen denselben Einstieg `bash tests/run_checks.sh` auf. `make unit`, `lint`, `syntax`, `build` und `package-smoke` sind gezielte Teilpruefungen; Syntax setzt ein installiertes aktuelles Artefakt voraus. CI prueft Python 3.12 mit Core 2.20 und 2.21. Der lokale Lauf verwendet die installierte Core-Version.

Aenderungen mit konkretem Problem, Verhalten, Tests und verbleibenden Luecken beschreiben. Inkompatible API-Aenderungen gehoeren in `docs/migration.md` und `CHANGELOG.md`; Nachweise in `docs/validation/`. Fremdlizenzen und Herkunft erhalten. Aenderungen am gemeinsamen Vertrag vorher mit den anderen Collection-Verantwortlichen abstimmen.

## Laufzeitabnahme

Infrastructure prueft Debian 13, Ubuntu 22.04/24.04/26.04 und Rocky 9 mit Container-Smoke/Functional-Tests samt zweitem Lauf `changed=0`. Docker ist dafuer erforderlich. Netzwerk, Firewall, SELinux, Dienststeuerung und Neustarts zusaetzlich auf dedizierten VMs abnehmen. Ein Rocky-Test ist kein RHEL-Test. Syntax und Renderpruefungen ersetzen keine echten Logins oder Paketinstallationen. Produktionsaenderungen, Migrationen und Releases sind separate Auftraege.
