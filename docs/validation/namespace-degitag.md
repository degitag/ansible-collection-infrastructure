# Namespace-Umbenennung zu degitag.infrastructure

Stand: 2026-10-27. Lokale Validierung des vorhandenen Arbeitsstands; keine Veroeffentlichung und kein Deployment.

## Aenderung und Migrationsgrenze

Die Host-Collection verwendet `degitag.infrastructure` statt `degit.infrastructure`. Metadaten, Generator-Konfiguration, Rollen- und Filteraufrufe, Beispiele, CI-/Release-Artefakte sowie lokale Validierungspfade sind umgestellt. Version: 2.0.0.

Bestehende uncommittete Arbeiten wurden erhalten. Separate Collections (`degit.k3s`, `degit.monitoring`, `degit.database`) und deren Repositories wurden nicht umbenannt. Ihre Abhaengigkeiten und Infrastructure-Aufrufe muessen vor gemeinsamer Verwendung separat angepasst werden. Bestehende Host-Besitzkennungen bleiben unveraendert, damit die reine Namespace-Aenderung keine neuen Netzwerkprofile oder Audit-Schluessel erzeugt. Historische JSON-Nachweise werden nicht nachtraeglich umetikettiert.

## Ausgefuehrte Pruefungen

`bash tests/run_checks.sh` ist mit Exitcode 0 abgeschlossen:

- Generator `--check` erfolgreich, YAML formatiert und YAML-Lint bestanden.
- 74 Unit-Tests bestanden.
- Collection gebaut, Artefaktidentitaet und ausgeschlossene Caches/Secrets geprueft; lokal unter `ansible_collections/degitag/infrastructure` installiert.
- Vorhandene UKHD-Renderpruefungen bestanden, einschliesslich Filteraufruf unter dem neuen FQCN.
- Syntaxpruefung aller 47 Rollen-Testplaybooks mit Facts auf Play-Ebene bestanden.
- Ansible-Lint, Profil `production`: 0 Fehler, 0 Warnungen, 1039 Dateien verarbeitet.
- `ansible-test sanity` fuer `compile` und `import` mit Python 3.12 ausserhalb des ignorierten Installationsverzeichnisses bestanden.

## Verbleibende Laufzeitpruefungen

Docker ist auf diesem Controller nicht verfuegbar. Die fuenf Container-Smoke-Laeufe samt Idempotenz sowie die bestehenden Dante-/WPAD-Functional-Tests wurden deshalb nicht erneut ausgefuehrt. Die CI verwendet fuer diese Tests bereits das neue Artefakt und die neuen FQCNs. Dedizierte VMs waren fuer diesen Auftrag nicht freigegeben; keine erneute Abnahme von Netzwerk, Firewall, Dienststarts, SELinux oder Neustarts. Historische VM-Ergebnisse sind kein erneuter Laufzeitnachweis fuer diesen Arbeitsstand.

## Artefakt

- Datei: `degitag-infrastructure-2.0.0.tar.gz`
- SHA256: `54f31aa5b2f1f17ceb1e03409ae5edb4f0ed1a852e5775dfbddb8049be2155b0`
