# Businesscase — aannames, geen gerealiseerde winst

Een accountancyteam wil weten of een gewijzigde AI-assistent nog correct weigert, juiste bronnen gebruikt en geen ongeoorloofde acties voorstelt. Handmatige spotchecks zijn nuttig maar moeilijk herhaalbaar. Deze case maakt een deel van die controle reproduceerbaar en bewaart testbewijs per versie.

## Illustratieve berekening

| Invoer | Aanname |
|---|---:|
| Kandidatenreleases per maand | 8 |
| Handmatige technische contractcontrole per release | 90 minuten |
| Resterende analyse na automatische controle | 30 minuten |
| Interne rekenkost | €65/uur |
| Onderhoud evaluaties per maand | 3 uur |

Bruto besparing = `8 × (90 − 30) / 60 = 8 uur/maand`. Na de aangenomen drie uur onderhoud: vijf uur, of €325 per maand volgens deze rekenkost. Bij 24 uur initiële engineering is de illustratieve terugverdientijd `24 / 5 = 4,8 maanden`. Provider-, infrastructuur-, licentie- en reviewkosten zijn niet meegerekend. Als onderhoud of menselijke analyse groter blijkt, verslechtert dit resultaat.

De opbrengst van vermeden incidenten is bewust niet in euro's geschat: zonder betrouwbare historische frequentie en schade zou dat schijnprecisie zijn. Deze kleine fixturecase heeft geen productiegebruikers en bewijst geen gerealiseerde tijdswinst.

## Te meten bij een echte pilot

| KPI | Definitie | Meetplan |
|---|---|---|
| Releasecontroleduur | Tijd van kandidaatversie tot beoordeeld evaluatiebewijs | Start/eind-tijd per release met dezelfde scope |
| Ontdekte regressies | Door test aangetoonde fout die baselineversie niet had | Review door domeinexpert; vals alarm apart tellen |
| False positives/negatives | Onterecht geblokkeerde / gemiste fouten | Blind gelabelde holdout en incidentterugkoppeling |
| Correct gebruik | Teamleden die rapport juist interpreteren en handelen | Scenario-oefeningen met L&D |
| Kosten per beoordeelde release | Provider, infrastructuur en menselijke review | Facturatie combineren met runnerusage |

De eerste pilotbeslissing is niet "alle tests groen", maar "de controle vindt relevante fouten, het team begrijpt de grenzen en de onderhoudslast is aanvaardbaar".
