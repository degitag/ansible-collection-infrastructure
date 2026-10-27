# Rollen-Schema: Zielzustand 2.0.0

Stand: 2026-10-18. Der historische Audit vom April wurde durch diesen Umsetzungsstand ersetzt.

Die 47 Host-Rollen und die sieben ausgelagerten K3s-Rollen verwenden `tasks/main.yml` als festen Einstieg: Preflight, danach `configuration.yml`. Defaults, Argumentvertrag, Meta, README und Syntax-Playbook werden durch den Scaffold konsistent gehalten. Familie, Distribution und Release liegen getrennt unter `vars/platform/`.

Der Preflight sammelt fehlende benoetigte Facts; Playbooks sammeln normalerweise mit `gather_facts: true`. Die genaue Plattformmatrix wird vor Systemaenderungen validiert. Die gemeinsame Firewall-Rolle kapselt UFW/firewalld, die Netzwerkrolle Netplan/ifupdown/NetworkManager. Leere Netzwerkkonfiguration bleibt ohne Seiteneffekt; Aktivierung und Backend-Wechsel sind bewusste Operatorentscheidungen.

Die oeffentliche Variablen-API ist zwischen Defaults und `argument_specs` gespiegelt. Fachlich zwingende Werte wie SSSD-Domain, Relay-Konten und K3s-Token werden vor Installation bzw. Konfiguration geprueft. Die Typisierung ersetzt keine semantische Validierung; komplexe Netzwerk- und Firewall-Eingaben durchlaufen zusaetzliche Filterpruefungen.

`generate_role_scaffold.py --check`, Unit-Tests, YAML-Lint, Ansible-Lint im Profil `production`, Syntax-Checks auf Core 2.20/2.21 und Artefaktpruefungen sichern die Struktur. Die Container-Matrix und VM-Tests pruefen ausgewaehlte reale Funktionen. Der vorhandene Rollenvertrag ist kein Nachweis, dass jede Kombination aller Rollen und Parameter auf allen Systemen funktional getestet wurde. [Testumfang und Grenzen](validation/README.md) sind Bestandteil der Freigabeentscheidung.
