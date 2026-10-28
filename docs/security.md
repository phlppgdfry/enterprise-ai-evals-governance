# Threat model en gegevensbescherming

Deze demo gebruikt synthetische gegevens. Het is een technische referentie en geen certificering van GDPR- of EU AI Act-conformiteit. De beleidsregels zijn fictieve organisatiekeuzes; laat echte juridische verplichtingen door bevoegde personen vaststellen.

| Dreiging | Maatregel in code | Restpunt |
|---|---|---|
| Aanvaller roept evaluaties aan | API-keycontrole, server-side rollen, lege configuratie weigert toegang | Geen Entra ID, MFA, rotatieservice of rate limiting |
| Reader doet zich voor als governor | Rol komt uit serverconfiguratie, extra requestvelden geweigerd | Wie het serverconfiguratiebestand beheert, beheert rollen |
| Prompt/document stuurt toolactie | Testcases checken exact toegestane tools en argumenten | Runner voert geen tools uit; target moet zelf afdwingen |
| Privédocument wordt geciteerd | Alleen opgegeven bron-ID's toegestaan | Geen echte SharePoint/tenant-ACL-integratie in runner |
| Target lekt persoonsgegevens | Canary- en patroonchecks; responses niet opgeslagen | Patroonherkenning mist veel persoonsgegevens en gecodeerde data |
| SSRF via evaluatie-URL | URL alleen uit operatorconfiguratie, geen redirects | Geen DNS-rebindingbescherming; egress-firewall blijft nodig |
| HTML-injectie in rapport | Alle targetafhankelijke tekst HTML-escaped; geen scripts | Rapport kan nog met externe tools onveilig worden verwerkt |
| Gevoelige providerfout in logs | Alleen exceptiontype in rapport | Hostinglaag en provider kunnen eigen logs bewaren |
| Onzichtbare kosten | Eindige tokenvalidatie en kostenbudget per case | Target kan usage verkeerd rapporteren; geen cloudbudgetlimiet |
| Evaluaties belasten server | Maximaal 1000 cases, dataset- en responslimieten, één lokale runslot | Geen reverse-proxy bodylimiet of gedistribueerde queue |

Bewaar sleutels in secretsmanagement. `.env`, databases en gewone runoutput staan in `.gitignore`. De voorbeeldtokens zijn bewust herkenbare placeholders; vervang ze voordat je het systeem gebruikt. Deel geen database met echte klantgegevens via GitHub. De publieke `/docs`-route toont alleen het interfaceschema, geen secretwaarden.

Rapporten bewaren case-ID's, checks, gebruiksaantallen, latency en fouttypes; geen prompts, modelantwoorden of documentinhoud. SQLite bewaart ook geconfigureerde actornamen. Gebruik daarom technische principalnamen en een passend bewaarbeleid. Bestanden zijn niet standaard versleuteld; gebruik schijfversleuteling en toegangsrechten. De API biedt geen automatische delete-/retentietaak en geen onveranderlijke auditlog.

Voor een organisatie-uitrol zijn centrale identiteit, tenantisolatie, bewaarbeleid, gegevensclassificatie, verwerkersafspraken, autorisatiematrix, incidentprocedure en onafhankelijke privacy- en securityreview nodig. Welke wettelijke verplichtingen precies gelden, hangt af van de toepassing en wordt hier niet vastgesteld.
