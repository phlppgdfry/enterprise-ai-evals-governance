# Governance en risk register

## Besluitvorming

De governor-rol kan een voorstel toetsen aan `demo-1`. Het antwoord is `blocked` of `conditional`; het wordt nooit een productiegoedkeuring. Een ongecontroleerde databron, bijzondere gegevenscategorie of bewaartermijn boven 90 dagen blokkeert het voorstel volgens deze fictieve demopolicy. Persoonsgegevens, financiële boekingen of externe acties vereisen expliciet menselijke controle. Deze grenzen zijn organisatieaannames, geen wettelijke normen.

Houd drie besluiten gescheiden: de technische evaluatie slaagt, de business accepteert de resterende risico's en een bevoegde reviewer geeft een concrete actie vrij. Een geslaagde eval mag de laatste twee besluiten niet vervangen. De beleids-API geeft daarom altijd `authorization_to_execute: false` terug.

## Verantwoordelijkheden

| Rol | Besluit / werk | Bewijs |
|---|---|---|
| Product owner | Doel, gebruikers, effect en acceptatiecriteria | Businesscase, prioriteiten, KPI-definities |
| Vakinhoudelijke expert | Juistheid van de verwachte antwoorden | Gelabelde dataset met reviewdatum |
| AI engineer | Targetversie, controles, deployment en diagnose | Commit, CI-artefacten, run-ID |
| Privacy/security | Datastromen, grondslag en passende maatregelen beoordelen | Review en voorwaarden buiten deze demo |
| Operationeel eigenaar | Monitoring, incidenten, terugvalprocedure | Runbook, hersteltest, escalatielijst |
| Bevoegde businessreviewer | Concrete uitvoeringsactie beoordelen | Actiespecifieke, versiegebonden goedkeuring in bronsysteem |

## Risk register

| ID | Risico | Kans / impact (demo-inschatting) | Eigenaar | Maatregel | Resterend risico / acceptatie |
|---|---|---|---|---|---|
| R01 | Onjuist antwoord bevat toevallig juiste trefwoorden | hoog / hoog | AI engineer + domeinexpert | Blind holdout, menselijke beoordeling, semantische checks | Niet met deze kleine suite af te sluiten |
| R02 | Gevoelige data verlaat target | middel / zeer hoog | Security | Canarytests, egressbeleid, bronautorisatie | Patroondetectie is beperkt; privacyreview vereist |
| R03 | Onveilige toolactie wordt uitgevoerd | middel / hoog | Applicatie-eigenaar | Gesloten toolcontract, runtime-autorisatie, menselijke goedkeuring | Eval alleen observeert; target moet afdwingen |
| R04 | Dataset wordt aangepast om score te verhogen | middel / hoog | Product owner | Hash, review, gescheiden holdout en immutable artefacten | Lokale baseline is niet ondertekend |
| R05 | Providerkosten of latency stijgen | middel / middel | Operations | Budgetgates, cloudalerts, loadtests | Deze runner meet geen productie-SLA |
| R06 | Auditdatabase raakt beschadigd of wordt gewijzigd | laag / hoog | Operations | Back-up/herstel, centrale append-only logging in productie | SQLite-demo heeft geen tamper evidence |
| R07 | AI-gegenereerd portfolio wordt als werkervaring gepresenteerd | middel / hoog | Kandidaat | Transparante herkomst, eigen uitleg/aanpas/diagnosetoets | Beheersing moet persoonlijk worden aangetoond |

## Releasechecklist met bewijs

- Exact dataset- en targetcommit, prompt- en modelversie vastleggen.
- Positieve controle slaagt en negatieve controle faalt met verwachte checks.
- Representatieve live holdoutresultaten en menselijke beoordeling beschikbaar.
- Alle harde safety- en budgetfouten opgelost; regressies afzonderlijk verklaard.
- Verantwoordelijke eigenaar, terugvalprocedure en noodzakelijke reviews akkoord.
- Gebruikerstraining, menselijke bevoegdheden en monitoring getest.

Deze checklist is documentatie voor een toekomstige uitrol. De items worden niet als uitgevoerd gepresenteerd door het bestaan van dit bestand.
