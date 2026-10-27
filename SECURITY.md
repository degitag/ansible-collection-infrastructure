# Sicherheit

Sicherheitsrelevante Befunde vertraulich an den in `galaxy.yml` genannten Maintainer melden. Bei aktivierter privater GitHub-Sicherheitsmeldung diese bevorzugen. Keine Zugangsdaten oder ausnutzbaren Details in oeffentliche Issues oder CI-Logs schreiben.

Die Meldung soll betroffene Collection-Version, Rolle, Plattform, Voraussetzungen, Auswirkung und einen bereinigten Reproduktionsfall enthalten. Produktive Zugangsdaten oder private Schluessel werden nicht benoetigt. Unterstuetzte Plattformen und Laufzeiten stehen in README und Rollenmetadaten; abgeschlossene Tests und offene Grenzen in `docs/validation/`. Es gibt keine gesonderte LTS-Zusage fuer alte Releases.

Secrets ueber Vault oder den Betreiber-Secret-Store bereitstellen. Lokale API-Credentials nie ins Repository kopieren; sensible Tasks verwenden restriktive Rechte und `no_log`. Zugriff, Firewall, SELinux und Dienststarts auf dedizierten Testsystemen pruefen. Ein Syntaxlauf ist keine Sicherheitsfreigabe.

CI verwendet minimale Berechtigungen und SHA-gepinnte Actions. Releases werden auf Identitaet, Version, Dateihashes und ausgeschlossene Entwicklungsdateien/Secrets geprueft. Die Artefaktkontrolle prueft bekannte Dateigrenzen; sie ersetzt keine inhaltliche Secret-Pruefung im Review.
