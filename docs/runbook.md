# Operationeel draaiboek

## Dagelijkse demonstratie

1. Installeer de gelockte dependencies in een schone Python 3.13-omgeving.
2. Voer `python -m pytest -q` uit en start de positieve fixturecontrole.
3. Voer de negatieve controle uit met dezelfde baseline en bevestig exitcode 1.
4. Controleer de datasethash, doelnaam, fixturemarkering en falende checks in het rapport.
5. Start de API als één worker met sterke tokens; controleer dat een reader niet kan evalueren of de audit lezen.

## Gate faalt

| Symptoom | Onderzoek | Actie |
|---|---|---|
| CLI exit 2 | Datasetpad, validatie, baselinehash, tokenconfiguratie | Configuratie herstellen; exit 2 nooit als gewone negatieve modelcase behandelen |
| `schema` faalt | Exceptiontype, contractversie, HTTP-status/timeout in gecontroleerde targetlogs | Contract of verbinding herstellen zonder gevoelige bodies in runnerlogs te plakken |
| `citations` faalt | Ontbrekende of ongeautoriseerde bron-ID | Targetretrieval en toegangscontrole onderzoeken |
| `tool_safety` faalt | Toolnaam en argumentwijziging in geïsoleerde synthetische test | Geen mutatie toestaan; contract/runtime-autorisatie herstellen |
| `pii` / canary faalt | Testcategorie en falende case-ID | Release blokkeren, incidentproces volgen wanneer echte data betrokken kan zijn |
| `cost` / `latency` faalt | Gebruikte tarieven, tokens, targetvertraging | Geen drempel verhogen zonder zakelijke onderbouwing |
| Baselineverschil | Datasetdiff en casereeks | Nieuwe baseline pas na review vaststellen |
| API 401/403 | Servergeconfigureerde sleutel en rol | Niet oplossen door een rolheader vanuit client toe te voegen |
| API 429 | Andere run in dezelfde worker | Run laten eindigen, targettimeout onderzoeken |
| HTTP-target 503 | `EVALGOV_TARGET_URL` / token ontbreekt | Alleen goedgekeurde bestemming configureren; geen stille fixturefallback |

## Back-up en herstel

Stop de API tijdens een eenvoudige bestandssnapshot, of gebruik SQLite's online backup-API. Kopieer niet alleen het databasebestand tijdens een actieve WAL-write. Bescherm de back-up als de oorspronkelijke auditgegevens. Herstel naar een afzonderlijk pad, start `create_app` met die `EVALGOV_DB` en vergelijk bekende run-ID's. De tests bewijzen heropenen van persistente data; een volledige crash-/back-uphersteltest is nog niet uitgevoerd.

## Retentie en incidenten

Er is geen automatische opschoontaak. Stel vóór echte inzet een bewaartermijn vast, verwijder gecontroleerd verlopen runs en bepaal of auditregels langer nodig zijn. Bij een incident: blokkeer targettoegang, bewaar minimale noodzakelijke technische artefacten, betrek de operationele/security/privacyverantwoordelijke en hervat pas na herstelcontrole. Een juridische meldplicht wordt niet door deze demo beoordeeld.

## Schalen

Deze API is synchroon en de lock geldt per proces. Meerdere Uvicorn-workers kunnen parallelle runs starten; gebruik daarom één worker in deze referentie. Voor grotere evaluaties: een duurzame jobqueue, afzonderlijke workers met leases, per-tenant quota, jobtimeouts en centrale artefactopslag. Hergebruik een bestaande datasethash voor regressievergelijking; wijzig geen testlabels tijdens een run.
