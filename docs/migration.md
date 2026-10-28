# Migration zum neuen Collection-Vertrag

Die Host-Collection wurde vor ihrer Veroeffentlichung von `degit.default_server` ueber `degit.infrastructure` in `degitag.infrastructure` umbenannt. Rollenreferenzen, Filter-FQCNs und Collection-Abhaengigkeiten im Inventory bzw. in requirements-Dateien entsprechend umstellen. Das GitHub-Repository liegt nach dem freigegebenen Transfer unter `degitag/ansible-collection-infrastructure`; der Ansible-Namespace ist unabhaengig davon `degitag`. Die K3s-Collection behaelt `degitag.k3s`.

Die neue API ist bewusst inkompatibel. Produktive Playbooks muessen vor dem ersten Rollout aktualisiert werden; diese Vorbereitung fuehrt keine bestehenden Inventories oder Server automatisch um.

## Namespace und Collections

Bestehende Verweise auf `degit.infrastructure` in Playbooks, `collections:`-Listen, Filteraufrufen und requirements-Dateien auf `degitag.infrastructure` umstellen. Das Build-Artefakt heisst jetzt `degitag-infrastructure-2.0.0.tar.gz`. Es gibt keinen automatischen Alias fuer den alten Namespace. Abhaengige Collections muessen ihre Infrastructure-Abhaengigkeit und Firewall-Delegationen vor gemeinsamer Verwendung ebenfalls aktualisieren. Hostseitige Besitzkennungen (zum Beispiel `degit-*`-Netzwerkprofile und Audit-Schluessel) bleiben erhalten.

Allgemeine Linux-Rollen verwenden `degitag.infrastructure.<rolle>`. Die sieben `k3s_*`-Rollen liegen unter `degitag.k3s.<rolle>` im separaten Repository `ansible-collection-k3s`. Beide Collections muessen bei gemeinsamer Verwendung installiert werden. Zuerst die Host-Collection bauen und installieren, danach die K3s-Collection.

## Netzwerk und Firewall

Die einzelnen Rollen `ufw`, `firewalld`, `netplan`, `interfaces`, `ifcfg` und `nmcli` entfallen. Ihre Variablen werden nicht implizit uebernommen. Regeln nach `firewall_rules` und Interfaces nach `network_interfaces` uebertragen; die Backendauswahl erfolgt anhand der Facts. Vollstaendige Beispiele und Feldvertraege stehen in den Rollen-READMEs.

Bei Netzwerk zuerst mit `network_apply: false` pruefen: Netplan/ifupdown rendern ihre Fragmente, nmcli bleibt im nativen Check-Modus und schreibt wegen moeglicher Autoaktivierung noch keine Profile. Profile und Fragmente werden unter einem eigenen Besitznamen verwaltet. Eine Migration bestehender Backends erfordert die bewusste Bereinigung alter Definitionen und einen Konsolenzugang. Die Rolle deaktiviert keine konkurrierenden Manager automatisch.

K3s-Zusatzinterfaces verwenden jetzt `k3s_network_interfaces` mit demselben Schema. Die bisherige ifupdown-spezifische Struktur `k3s_extra_interfaces` und `k3s_network_config_path` entfallen.

## Facts und Betriebssysteme

Beispiele sammeln Facts auf Play-Ebene. Rollen sammeln fehlende benoetigte Facts nach. Globale `ansible_*`-Fact-Aliase sind nicht erforderlich; Tasks und Templates verwenden `ansible_facts`. Debian 12, EL8 und sonstige nicht aufgefuehrte Betriebssysteme werden abgewiesen.

## Defaults und Versionen

Die Paket-Baseline ist bewusst klein und uebersteuerbar. Die allgemeine Paket-Baseline aktiviert EPEL nicht und entfernt ohne Opt-in keine Pakete. EPEL-abhaengige Dienstrollen verwalten ihre dokumentierte Quelle ueber den jeweiligen `*_manage_epel`-Schalter. Anwendungsversionen sind in Defaults festgelegt; ein Versionswechsel ist separat in der Testumgebung abzunehmen. Insbesondere Traefik 2→3 braucht eine Pruefung eigener Router- und Provider-Konfigurationen. K3s-Versionswechsel sind explizite Clusterupgrades, keine unbeabsichtigte Folge eines allgemeinen Host-Rollouts.

## Weitere bewusste API-Aenderungen

- BorgBackup initialisiert und plant nur mit `borgbackup_manage_repository: true` bzw. `borgbackup_manage_cron: true`. Verschluesselte Repositories brauchen eine echte Passphrase aus dem Secret-Store.
- Statische DNS-Dateien werden nur mit `resolvconf_manage_config: true` und expliziten Resolveradressen verwaltet. DHCP/systemd-resolved bleibt ansonsten zustaendig.
- SMTP-Konten und das SSSD-Verzeichnisziel muessen explizit gesetzt werden. Platzhalter-Zugangsdaten und fremde Relay-Ziele entfallen.
- Die MOTD-Eingaben heissen `motd_description` und `motd_responsible`; Vendor-Meldungen bleiben ohne expliziten Schalter erhalten.
- EPEL-abhaengige Rollen dokumentieren ihre Paketquelle und bieten einen `*_manage_epel`-Schalter. RHEL benoetigt passende abonnierte Basis-Repositories.

Dante wird auf Debian 13 vor Aenderungen abgewiesen, weil die Distribution kein Server-Paket bereitstellt. Fuer diesen Dienst ein unterstuetztes Ubuntu-/EL9-Ziel verwenden; die Collection fuegt kein fremdes Debian-Release als Paketquelle hinzu.

Certbot beantragt mit `certbot_certs: []` im Standard keine Zertifikate. Zertifikatsnamen, ACME-Mail und DNS-Provider-Credentials explizit konfigurieren. Die GUI-Rolle bleibt deaktiviert; Distributionspakete werden intern gewaehlt und ueber `gui_extra_packages` ergaenzt, statt die bisherigen Debian-/RedHat-Paketlisten aus Defaults zu verwenden.

## Monitoring agents

`alloy` and `node_exporter` are owned by `degitag.monitoring`. Install that collection and use its fully qualified role names. The baseline collection does not depend on monitoring. Retired Grafana Agent and Promtail installations are not migrated.


## Uebernahme allgemeiner UKHD-Funktionen

- `conditional_reboot` ersetzt das alte Shellskript durch einen Python-Controller und verwendet in Skriptinstallation und Unit denselben Pfad. `conditional_reboot_enabled: true` aktiviert den Timer ausdruecklich. Debian/Ubuntu pruefen `reboot-required`, EL9 nutzt `needs-restarting -r`. Das Zeitfenster gilt in lokaler Hostzeit; verspaetete Laeufe werden nicht nachgeholt. Auf einer dedizierten Test-VM zuerst den installierten Controller mit `--config /etc/conditional-reboot.json --dry-run` pruefen. Ein echter Neustart ist separat abzunehmen.
- `prompt` deckt Git-Prompt und optionale SSH-Agent-/Root-Helfer ab. yq braucht eine explizite Version und SHA256-Pruefsumme; Architektur-Binaries werden nicht im Repository verdoppelt. `users` und `prompt` duerfen nicht gleichzeitig dieselben Root-Dotfiles verwalten.
- `proxy_env` akzeptiert auch Grossschreibung. Backslashes in URL-Anmeldedaten werden einmalig percent-codiert. `proxy_environment` ist das normalisierte Dictionary fuer `environment:` bei Ansible-Tasks. Eine geschriebene `/etc/environment` veraendert den laufenden Ansible-Prozess nicht. pip erhaelt standardmaessig nur den Schluessel `global.proxy` in `/etc/pip.conf`; fremde Einstellungen bleiben erhalten. Proxy-Credentials gehoeren weiterhin ins Vault.
- Docker nutzt `docker_proxy_env` (standardmaessig `proxy_env`) fuer Repository-Zugriffe und den systemd-Daemon. Der geschuetzte Drop-in wird vor nachfolgenden Image-Pulls angewendet. `daemon.json`-Proxies und den Drop-in nicht gleichzeitig verwalten. Die UKHD-spezifische `/opt/gitlab/proxyserver/environment` wird nicht uebernommen.
- `auditd_shell_commands_enabled: false` deaktiviert die Command-Regeln, waehrend `auditd_session_logging_enabled` separat steuerbar bleibt. Fuer die alte UKHD-Datei `logging.rules` und deren `shell_history`-Regeln `auditd_remove_legacy_shell_rules: true` bei der Migration setzen. Unveraenderliche Kernel-Regeln werden als Fehler sichtbar; keine automatische Aufweichung und kein Neustart durch diese Rolle.
- Die SSH-Ausnahmen fuer Benutzer und Gruppen werden ueber `sshd_server_match_blocks` konfiguriert. Die alte Gruppe `AllowPasswordAuth` kann ueber `users_groups` deklariert werden; sie ist keine globale Collection-Vorgabe. AES-GCM und ChaCha20 werden gegenueber AES-CTR bevorzugt; EL9 nutzt eine AES-Liste. Site-spezifische Crypto-Policies und echte Logins separat abnehmen.
- `sssd_ad_group_allowed_ssh` erlaubt zusaetzliche Login-Gruppen ohne sudo. Das ersetzt die alte falsch geschriebene `sssd_ad_group_allowd_ssh`-Eingabe.
- NGINX kann `nginx_stream_upstreams`, `nginx_stream_maps`, `nginx_stream_servers` und das bisherige `nginx_streams`-Schema rendern. `nginx_stream_servers[].listen` ist eine Liste, Map-Eintraege verwenden `match` und `value`. Die Rolle installiert das native Stream-Modul bei Bedarf; Drittanbieter-Pakete brauchen gegebenenfalls eine eigene Modulquelle.

Quellen fuer die Implementierungsentscheidungen: [OpenSSH Cipher-Vertrag](https://man.openbsd.org/sshd_config#Ciphers), [Docker Daemon Proxy](https://docs.docker.com/engine/daemon/proxy/), [pip-Konfiguration](https://pip.pypa.io/en/stable/topics/configuration/).


## Gemeinsamer Repository-Standard

Struktur und Entwicklungsablaeufe folgen jetzt [degitag-collections-v1](repository-standard.md). Der vollstaendige lokale und CI-Aufruf ist `bash tests/run_checks.sh`; `make ci` und `make test` sind Wrapper. Artefaktnamen werden aus `galaxy.yml` abgeleitet. Entwicklungsdateien und Caches sind aus dem Release-Paket ausgeschlossen. Die gemeinsame CI-Basis ist Python 3.12 mit Core 2.20/2.21; diese Umstellung veraendert keine Host-Besitzkennungen und fuehrt keinen produktiven Rollout aus.
