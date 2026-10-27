# Repository-Angleich Infrastructure

Stand: 2026-10-27, Vertrag `degitag-collections-v1`. Koordination erfolgte vor Umsetzung mit den Database-, Monitoring- und Proxmox-Chats. Infrastructure uebernahm zusaetzlich K3s; der lokale default-server-Pfad ist nur ein Symlink auf Infrastructure. Kein Rollout und keine Veroeffentlichung.

## Ergebnis

Einheitliche README-H2-Struktur, CONTRIBUTING/SECURITY, EditorConfig, Make-Wrapper, gemeinsamer lokaler/CI-Einstieg sowie datengesteuerte Artefakt- und Sanity-Pfade. Acht gemeinsame Dateien wurden ueber alle fuenf Repositories bytegleich verglichen. Fachliche Erweiterungen bleiben erhalten: Monitoring besitzt Windows-/Exporter-/Regelpruefungen; Proxmox den Legacy-Adapter und Installer-Medientests. Der abgestimmte [Repository-Vertrag](../repository-standard.md) dokumentiert diese Grenzen.

Collection: `degitag.infrastructure`, Version `2.0.0`. Namespace-Referenzen und benoetigte Geschwister-Abhaengigkeiten verwenden `degitag`. Host-Besitzkennungen und Rollen-APIs bleiben erhalten.

## Pruefungen

Vollstaendiger Einstieg: `bash tests/run_checks.sh` mit Python 3.12 und Ansible Core 2.21.5. 89 Unit-Tests, Repository-/Scaffold-/YAML-Pruefung, Build/Artefakt/Installation, Syntax der 47 Rollen und vorhandener fachlicher Testplaybooks, Ansible-Lint `production` und Sanity Compile/Import bestanden. Sanity lief ausserhalb des ignorierten Installationspfads. Zusaetzlich bestanden `make package-smoke`, Shellsyntax und `git diff --check`.

Hashes und genaue Pruefliste stehen in [repository-standard-2026-10-27.json](repository-standard-2026-10-27.json). Historische JSON-Nachweise wurden nicht geaendert.

## Offene Laufzeitabnahme

Docker ist auf diesem Controller nicht verfuegbar. Container-Smoke/Functional-Runtime und dedizierte VM-/Cluster-Tests wurden nicht erneut ausgefuehrt. Core 2.20 ist in CI konfiguriert, wurde hier lokal nicht erneut getestet. Die GitHub-Workflows wurden nicht ausgefuehrt oder veroeffentlicht. Gruene Controllerchecks sind keine neue Abnahme von Netzwerk, Firewall, Diensten, SELinux, Reboots oder K3s-Clusterfunktionen.
