# Kernel-Crash-Recovery: Validierung am 29.10.2026

## Verantwortung und Zielzustand

Die neue Rolle `degitag.infrastructure.kernel_crash_recovery` gehoert zur Linux-Host-Baseline. Der Betreiber weist sie gezielt seinen Hosts zu. Die Rolle verwaltet ausschliesslich `kernel.panic` und `kernel.panic_on_oops` in `/etc/sysctl.d/90-kernel-crash-recovery.conf` und gleicht optional die laufenden Werte ab. Andere Sysctl-Quellen duerfen diese beiden Schluessel nicht gleichzeitig verwalten.

Bei aktivierter Rolle gelten standardmaessig `kernel.panic=60` und `kernel.panic_on_oops=1`. Das ist ein Wiederanlaufmechanismus nach einem Kernel-Fehler. Die Rolle behebt keine Kernel-Regression und erkennt nicht jeden vollstaendigen Hanger. Wiederholte Abstuerze koennen Neustartschleifen erzeugen; ungesicherte Schreibvorgaenge koennen verloren gehen. Persistente Journale/pstore sowie Alarmierung auf unerwartete Neustarts bleiben Betriebsaufgaben.

`kernel_crash_recovery_apply=false` schreibt nur die persistente Richtlinie. Sie wird beim naechsten Sysctl-Laden oder Boot trotzdem wirksam. Deshalb ist dieser Schalter kein Deaktivierungsschalter. Erkannte Container lehnen die direkte Laufzeitaktivierung ab; die Containerpruefungen verwenden ausschliesslich den Konfigurationsmodus.

## Struktur und lokale Pruefungen

- Generiertes Rollen-Schema einschliesslich Fact-/Release-Preflight, Plattformvariablen und typisiertem Argumentvertrag.
- `tools/generate_role_scaffold.py --check` erfolgreich.
- Alle 90 Unit-Tests erfolgreich. Der Workflow-Matrixtest bestimmt seine erwartete Matrix jetzt dynamisch statt eine feste Anzahl von Rollen vorauszusetzen.
- YAML-Lint und Ansible-Lint mit Profil `production` erfolgreich.
- Syntaxpruefung aller Rollen sowie Playbooks erfolgreich.
- Collection-Artefakt gebaut und installiert; Namespace, Nutzdaten und Ausschluesse erfolgreich geprueft.
- `ansible-test sanity --test compile --test import` mit Python 3.12 ausserhalb des ignorierten Installationsverzeichnisses erfolgreich.

Das lokale Entwicklungsartefakt traegt noch die vorhandene Version 2.0.1; diese neue Rolle ist ein nicht veroeffentlichter Aenderungsstand und kein Release 2.0.1. Kein Tag oder Galaxy-Release wurde erstellt.

## Laufzeittest auf datahub-test01

Vom Benutzer ausdruecklich bestaetigtes Testziel: Debian 13, `datahub-test01.id.reifen-wolf.de`. Verwendet wurde das aus dem aktuellen Checkout gebaute und installierte Artefakt mit dem vollqualifizierten Collection-Playbook. Kein produktiver oder weiterer Host wurde ausgerollt.

- Check-Modus mit Diff zeigte nur die neue Richtliniendatei und die beiden Laufzeitwerte.
- Aktivierung erfolgreich; `/usr/sbin/sysctl kernel.panic kernel.panic_on_oops` meldet `60` und `1`.
- Zweiter normaler Lauf: `ok=10 changed=0 unreachable=0 failed=0`.
- `tests/integration/kernel_crash_recovery.yml` erfolgreich: Rueckbau auf `0/0`, Rendern einer alternativen 120-Sekunden-Richtlinie ohne Laufzeitaenderung, Wiederaktivierung von `60/1` und Korrektur einer absichtlich auf `59` abweichenden Laufzeitverzoegerung bei unveraenderter Datei.
- Die `always`-Sektion des Laufzeittests stellt die freigegebene Richtlinie `60/1` auch bei einer fehlgeschlagenen Testassertion wieder her.
- Abschlusslauf nach den Verhaltenstests erneut `changed=0`.
- Boot-ID vor und nach dem Test identisch; kein Neustart und kein kuenstlicher Kernel-Oops/Panic ausgeloest.
- `kernel.panic_on_warn`, `vm.panic_on_oom`, `kernel.softlockup_panic` und `kernel.hardlockup_panic` unveraendert bei `0`.

Der Test belegt Dateikonfiguration, Laufzeitaktivierung, Rueckbau und Driftkorrektur. Ein tatsaechlicher Panic-Neustart oder Persistenznachweis durch erneuten VM-Boot wurde auf diesem gemeinsam genutzten Testserver bewusst nicht ausgefuehrt. Das bleibt ein gesonderter Test auf einer entbehrlichen VM. RHEL 9 und aktive Laufzeitwerte auf Ubuntu/Rocky wurden hier nicht auf echten VMs abgenommen.

## Rollout und Rueckbau

Nach Installation eines Artefakts bzw. Releases, das die Rolle enthaelt:

```sh
ansible-playbook degitag.infrastructure.kernel_crash_recovery \
  -i inventory/id.reifen-wolf.de/hosts.yml --limit datahub-test01 --check --diff
ansible-playbook degitag.infrastructure.kernel_crash_recovery \
  -i inventory/id.reifen-wolf.de/hosts.yml --limit datahub-test01
```

Das Playbook verwendet `serial: 1`. Weitere Hosts erst nach expliziter Auswahl ueber Inventory/Limit aufnehmen. Es konfiguriert laufend und persistent, startet Hosts jedoch nicht neu. Die bestehende allgemeine Sysctl-Rolle ist keine Abhaengigkeit; ihre Netzwerk-/VM-Defaults werden nicht mit angewendet.

Expliziter Rueckbau fuer dieselben ausgewaehlten Hosts:

```sh
ansible-playbook degitag.infrastructure.kernel_crash_recovery \
  -i inventory/id.reifen-wolf.de/hosts.yml --limit datahub-test01 \
  -e '{"kernel_crash_recovery_enabled": false, "kernel_crash_recovery_apply": true}'
```

Dies setzt die beiden eigenen persistenten und laufenden Werte auf `0`. Vorher bestehende abweichende Betreiberwerte bei Bedarf gezielt wiederherstellen. Nur Entfernen der Rolle bzw. Datei setzt die laufenden Werte nicht zurueck. Diagnose: `sudo /usr/sbin/sysctl kernel.panic kernel.panic_on_oops` und `sudo vim /etc/sysctl.d/90-kernel-crash-recovery.conf`; spaetere Sysctl-Dateien sowie `/etc/sysctl.conf` auf Konflikte pruefen.

## Container-Matrix

Controller: Ansible Core 2.21.5 / Python 3.13 auf dev.lenmail.de, isolierte temporaere Docker-Container. Beide Playbooks liefen je Image zweimal; nachstehend jeweils der zweite Lauf. Laufzeit-Sysctls des Containerhosts wurden nicht veraendert. Der Funktionstest prueft ausserdem die Ablehnung eines ungueltigen Zeitwerts vor Aenderungen und unveraenderte Host-Sysctls im Konfigurationsmodus.

| Image | Baseline-Smoke | Rollen-Funktionstest | Zweiter Lauf |
| --- | --- | --- | --- |
| debian-13 | bestanden (119 Tasks) | bestanden (20 Tasks) | changed=0, unreachable=0, failed=0 |
| ubuntu-22.04 | bestanden (130 Tasks) | bestanden (22 Tasks) | changed=0, unreachable=0, failed=0 |
| ubuntu-24.04 | bestanden (130 Tasks) | bestanden (22 Tasks) | changed=0, unreachable=0, failed=0 |
| ubuntu-26.04 | bestanden (130 Tasks) | bestanden (22 Tasks) | changed=0, unreachable=0, failed=0 |
| rockylinux-9 | bestanden (118 Tasks) | bestanden (22 Tasks) | changed=0, unreachable=0, failed=0 |

Die fuenf Images decken die freie Plattformmatrix ab. Das ist Konfigurationsabnahme im Container, keine Abnahme eines echten Kernel-Panic-Neustarts und kein echter RHEL-Test. Die VM-Laufzeittests oben liefen ebenfalls mit Ansible Core 2.21.5, auf einem lokalen Controller mit Python 3.12, gegen Debian 13. Die GitHub-Checks des Pull Requests sind davon unabhaengig und werden separat angezeigt.
