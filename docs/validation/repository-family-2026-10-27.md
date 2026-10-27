# Gesamt-Abgleich der degitag-Collections

Stand: 2026-10-27. Der gemeinsame Vertrag `degitag-collections-v1` wurde vor den Strukturarbeiten zwischen den Collection-Verantwortlichen abgestimmt. Jeder Chat bearbeitete ausschliesslich sein zugewiesenes Repository. Infrastructure uebernahm K3s anfangs mangels sichtbarem Owner; der spaeter hinzugekommene K3s-Chat verifizierte den fertigen Stand anschliessend unabhaengig und ohne Aenderungen. Der alte default-server-Pfad ist nur ein lokaler Symlink auf Infrastructure.

## Gemeinsamer Stand

Alle fuenf Repositories bestehen `tools/check_repository.py`. Acht Dateien sind bytegleich: gemeinsamer Vertrag, EditorConfig, Repository-/Artefakt-/Metadatenpruefer, Sanity-Runner und die beiden generischen Regressionstestdateien. Ihre vollstaendigen SHA256-Werte stehen im [lokalen JSON-Nachweis](repository-standard-2026-10-27.json).

Alle Repositories verwenden dieselbe README-H2-Gliederung, CONTRIBUTING/SECURITY, Make-Wrapper und `bash tests/run_checks.sh` als vollstaendigen lokalen/CI-Einstieg. CI prueft Python 3.12 mit Core 2.20/2.21, Actions sind SHA-gepinnt und Releases bleiben auf passende Versionstags nach Checks beschraenkt. Laufzeit-Artefakte schliessen Entwicklungsdateien und Caches aus; Identitaet, Version, Manifest und Payload-Hashes werden geprueft.

## Lokale Pruefergebnisse

| Collection | Core 2.21: vollstaendiger Einstieg | Unit-/Vertragstests | Besondere Pruefungen |
| --- | --- | --- | --- |
| `degitag.infrastructure` | Exit 0 | 89 | UKHD-Rendervertrag, Rollen-/Functional-/Integration-Syntax, Paket/Installation, Sanity |
| `degitag.database` | Exit 0 | 49 | Sichere Preflights, Rollen-/Beispiel-/Integration-Syntax, Paket/Installation, Sanity |
| `degitag.monitoring` | Exit 0 laut verantwortlichem Chat | 48 | Binaer-Provenienz, Preflight, LPM-/PVE-Promtool, sieben Mailfaelle, Paket/Installation, Sanity |
| `degitag.k3s` | Exit 0, unabhaengig nachgeprueft | 29 | Clusterplaybook-Syntax, Infrastructure-Abhaengigkeit, Paket/Installation, Sanity |
| `degitag.proxmox` | Exit 0 laut verantwortlichem Chat | 67 plus drei Subtests | Firewall-/Installer-Render, BIOS/UEFI-Medien und Cache, materialisiertes Runtime-Paket, frische Installation, Legacy-Adapter, Sanity |

Proxmox hat den vollstaendigen Umfang zusaetzlich unter Core 2.20.10 mit Exit 0 abgeschlossen (ebenfalls 67 Tests plus drei Subtests). Der eigene Nachweis liegt in `ansible-role-proxmox-automatic/docs/validation/repository-standard-2026-10-27.json`. Die echte OS-Boot-/Live-VM-Abnahme und die Linux-nft-Kernelpruefung wurden auf dem macOS-Controller nicht ausgefuehrt. Fuer Infrastructure, Database und K3s wurde Core 2.20 im Strukturauftrag lokal nicht erneut ausgefuehrt. GitHub-Workflows wurden hier nicht neu gestartet oder veroeffentlicht.

## Bewusste Unterschiede

Monitoring behaelt Windows-Fact-Handling, operative Rollenhinweise und die lokale `.venv-v2`-Formatterausnahme. Die Generatoren unterstuetzen weiterhin unterschiedliche Rollen-Lizenzen. Proxmox behält seine internen Rollen und den Legacy-Rootadapter; Symlinks werden nur im temporaeren Build-Staging materialisiert, damit die strikte gemeinsame Paketpruefung unveraendert bleibt. Fachliche Hooks bleiben benannt und werden nicht durch kuenstliche gemeinsame Smoke-Tests ersetzt.

## Grenzen und weitere Arbeit

Diese Ergebnisse schliessen den abgestimmten Strukturauftrag ab. Die weitergehende native Monitoring-/LPM-/Telegraf-Releaseabnahme laeuft im Monitoring-Auftrag und hat eigene Nachweise. Fuer Infrastructure, Database und K3s wurden keine neuen Container- oder dedizierten VM-/Cluster-Runtimefaelle ausgefuehrt; Docker steht auf diesem Controller nicht bereit. Proxmox-Live-E2E bleibt separat. Historische Validierungsberichte und Artefakt-Hashes wurden nicht umetikettiert. Vorhandene lokale Arbeiten und Fremdlizenzen bleiben erhalten. Keine produktiven Deployments, Pushes, Tags oder Veroeffentlichungen aus diesem Strukturauftrag.
