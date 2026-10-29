# Enterprise AI Evals & Governance

Een reproduceerbare releasecontrole voor AI-toepassingen: voer een versiegebonden dataset uit, controleer antwoorden en toolcontracten, vergelijk met een baseline en bewaar controleerbare JSON- en HTML-resultaten. Een afzonderlijke beleids-API maakt zichtbaar wanneer een toepassing privacybeoordeling en menselijke goedkeuring nodig heeft.

## Portfolio update — 29 October 2026

An executed-run dashboard at `/console`, actual portfolio API evaluation adapters, a versioned RAG dataset and request security controls.

[Integration and limitations](docs/portfolio-integration.md) · [Current evidence matrix](evidence/FEATURES.md)

![Actual implemented workspace](evidence/screenshots/desktop.png)

**Status: werkende lokale portfolio-referentie.** De meegeleverde positieve en negatieve antwoorden zijn handgeschreven synthetische fixtures. Hun scores bewijzen dat de testcontrole werkt; ze zeggen niets over de kwaliteit van Azure OpenAI of een ander model. De HTTP-adapter werkt voor expliciet geconfigureerde systemen met het [targetcontract](docs/target-contract.md). Er is geen Azure-account aangemaakt of live model geëvalueerd.

## Snel uitvoeren

Python 3.13 is de geteste omgeving; Python 3.11+ is toegestaan door het pakket.

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -m pytest -q
.venv/bin/evalgov --fixture good --out reports/good
.venv/bin/evalgov --fixture unsafe --baseline reports/good/report.json --out reports/unsafe
```

Het laatste commando hoort exitcode **1** te geven: de negatieve controle bevat bewust verkeerde antwoorden, datalekken en onveilige toolaanroepen. Exitcode 0 betekent alle ingestelde gates gehaald; 2 betekent configuratie- of uitvoeringsfout. Open `reports/good/report.html` en `reports/unsafe/report.html` om de verschillen te bekijken. [Vastgelegde voorbeeldresultaten](evidence/README.md) bevatten uitsluitend synthetische runs.

## Wat werkt

| Onderdeel | Concreet gedrag |
|---|---|
| Dataset | 16 versiegebonden gevallen, zes categorieën, SHA-256 in elk rapport |
| Contractcontrole | Strikte antwoordvorm, eindige niet-negatieve tokens, geen extra velden |
| Kwaliteit | Vereiste antwoordtermen en bron-ID's; foutieve of niet-toegestane citaties falen |
| Veiligheid | Verwachte weigering, verboden canaries, eenvoudige PII-patronen, exacte toegestane toolargumenten |
| Kosten en snelheid | Gemeten wall-clock latency; kostenraming op basis van gerapporteerde tokens en configureerbare tarieven |
| Regressie | Baseline moet dezelfde datasethash en geordende case-ID's hebben |
| Hard gates | Schema-, privacy-, weigering-, tool-, citatie- en budgetfouten blokkeren altijd |
| Bewijs | JSON/HTML per run; SQLite-opslag van runs en gestructureerde auditregels |
| Autorisatie | Servergebonden reader/evaluator/governor-rollen; geen rollen vanuit requestheaders of body |
| Beleid | Advies met blokkades en benodigde controles; verleent nooit uitvoeringsrechten |

De kwaliteitstests zijn **heuristieken**. Een antwoord kan de juiste trefwoorden bevatten en toch inhoudelijk verkeerd zijn. Het systeem bewijst geen volledige groundedness, juridische conformiteit, robuuste PII-detectie of algemene prompt-injectionbestendigheid. Lees de [meetdefinities](docs/evaluation-design.md) en [grenzen](docs/security.md).

## API starten

Maak lokaal sterke willekeurige tokens. Configureer alle rollen op de server; zet ze niet in de repository.

```bash
export EVALGOV_PRINCIPALS='{"replace-with-a-long-random-token":{"name":"demo-owner","role":"governor"}}'
.venv/bin/uvicorn evalgov.api:create_app --factory --host 127.0.0.1 --port 8083
```

Open `http://127.0.0.1:8083/docs`, kies **Authorize** en gebruik je token. Zonder configuratie weigert elke beschermde route toegang. `/health`, `/docs` en `/openapi.json` zijn publiek; ze bevatten geen runinhoud. De JSON OpenAPI-specificatie staat ook in [docs/openapi.json](docs/openapi.json).

| Route | Rol | Doel |
|---|---|---|
| `POST /runs` | evaluator/governor | Dataset uitvoeren met `good`, `unsafe` of geconfigureerd `http` target |
| `GET /runs`, `GET /runs/{id}` | alle geconfigureerde rollen | Resultaten terugvinden |
| `GET /runs/{id}/report` | alle geconfigureerde rollen | HTML-rapport |
| `POST /policy/decide` | governor | Beleidsadvies, geen uitvoeringsgoedkeuring |
| `GET /audit` | governor | Laatste 100 auditregels |

API-clients moeten `X-API-Key` meesturen. Deze demo ondersteunt één organisatie; rollen zijn geen tenantisolatie. De API gebruikt één procesgebonden evaluatieslot. Een run is synchroon, niet een gedistribueerde job.

## Docker en integratie

```bash
cp .env.example .env
# Vervang de voorbeeldtokens in .env voordat je start.
docker compose up --build
```

De container draait als niet-root; de gepubliceerde poort bindt aan localhost en SQLite gebruikt een persistent volume. De Dockerbestanden zijn aangeleverd; zie [verificatie](evidence/README.md) voor wat werkelijk is getest.

Voor een live target:

```bash
export EVALGOV_TARGET_TOKEN='your-locally-stored-target-token'
.venv/bin/evalgov --http https://your-approved-service.example/evaluate --out reports/live
```

Het target moet het beschreven contract implementeren en zelf het model aanroepen. De afzonderlijke portfolio-adapter evalueert inmiddels de werkelijke RAG- en workflow-API's; zie [portfolio-integratie](docs/portfolio-integration.md). Het generieke HTTP-target gebruikt nog steeds zijn eigen contract. Er worden geen antwoorden of verwachte labels naar het target gestuurd; uitsluitend vraag, case-ID en toegestane contextdocumenten.

## Lezen en demonstreren

- [Architectuur en keuzes](docs/architecture.md)
- [Evaluatieontwerp en beperkingen](docs/evaluation-design.md)
- [Threat model en gegevensbescherming](docs/security.md)
- [Operationeel draaiboek](docs/runbook.md)
- [Risk register en governance](docs/governance.md)
- [Businesscase met aannames](docs/business-case.md)
- [Leerboek, oefeningen en interview](docs/learning.md)
- [Demonstratie van twee minuten](docs/demo.md)

De implementatie en documentatie zijn met AI-assistentie gemaakt. Het bestaan van deze repository is geen bewijs van persoonlijke beheersing of professionele productie-ervaring. De oefeningen laten de kandidaat zelf uitleggen, aanpassen en diagnosticeren voordat deze kennis op een cv wordt geclaimd.
