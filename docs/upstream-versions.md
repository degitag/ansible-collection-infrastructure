# Versionsstand und Bezugsquellen

Geprueft am 2026-10-18. Paketverwaltete Dienste verwenden die Sicherheitsupdates ihrer Distribution; externe Binaries und Images sind gezielt fixiert. Ein neues Upstream-Release loest keinen unbeaufsichtigten Major-Wechsel aus.

| Komponente | Default | Quelle |
| --- | --- | --- |
| Ansible Core | 2.20/2.21 | [Supportmatrix](https://docs.ansible.com/ansible-core/devel/reference_appendices/release_and_maintenance.html) |
| Node Exporter | 1.12.1 | [Releases](https://github.com/prometheus/node_exporter/releases) |
| Traefik | 3.7.15 | [Releases](https://github.com/traefik/traefik/releases) |
| Borgmatic | 2.1.10 | [PyPI](https://pypi.org/project/borgmatic/) |
| uv | 0.13.1, Installer mit SHA256 | [Releases](https://github.com/astral-sh/uv/releases) |
| K3s | v1.36.5+k3s1, Stable zum Pruefzeitpunkt | [Release-Kanaele](https://update.k3s.io/v1-release/channels) |
| Authentik | 2026.8.4, Server und LDAP gemeinsam | [Release](https://github.com/goauthentik/authentik/releases/tag/version/2026.8.4) |

Image-Digests und Download-Pruefsummen muessen bei Updates gemeinsam mit Konfiguration, Datenformaten und Upgrade-Pfad geprueft werden. Bestehende Datenbanken behalten ihre vorgegebenen Major-Versionen. Alle optionalen Anwendungspfade benoetigen eigene Integrationstests; ein eingefrorenes Image allein beweist keine Kompatibilitaet.
