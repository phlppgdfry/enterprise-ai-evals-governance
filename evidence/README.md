# Uitgevoerd verificatiebewijs

Lokaal uitgevoerd op 28 oktober 2026 met Python 3.13 en de vastgelegde `requirements.lock`.

| Controle | Werkelijk resultaat |
|---|---|
| `python -m pytest -q --junitxml=evidence/tests.xml` | 23 geslaagde tests; één upstream waarschuwing over de huidige Starlette/httpx TestClient-combinatie |
| `evalgov --fixture good --out evidence/good` | Exit 0; 16/16 cases slagen |
| `evalgov --fixture unsafe --baseline evidence/good/report.json --out evidence/unsafe` | Exit 1; 8/16 cases slagen; regressie 0,5 |
| OpenAPI snapshot | Gegenereerd uit de werkelijke app in `docs/openapi.json` |

De vastgelegde JSON- en HTML-rapporten bevatten de daadwerkelijke lokale run-ID's, datasethash, latency en score-uitkomsten. Gebruik de bijbehorende JSON als machineleesbaar bewijs. Kleine latencyverschillen bij herhalen zijn normaal.

Alle tokenaantallen zijn synthetische fixturewaarden; de kostenraming van $0,00288 per fixture-run is berekend met illustratieve tarieven. Dit is geen modelbenchmark, geen providerfactuur en geen bewezen tijdswinst. De rapporten bewaren bewust geen prompt- of antwoordinhoud.

Tests controleren onder andere autorisatie en role-spoofing, persistente data na appherstart, negatieve veiligheidsgevallen, afwijkende baseline, kosten/latencygrenzen, ongeldige schema's, HTML-escaping, HTTP-requestcontract, redirectweigering en maximale responsomvang. HTTP is getest met een geïnjecteerde opener; er is geen echte Azure-verbinding of live model getest.

De Docker-image is daadwerkelijk gebouwd. De verpakte API is geïsoleerd met TestClient getest; de standaard Uvicorn-CMD is daarna in een tijdelijke container gestart en `/health` gaf 200. Zie `container-smoke.txt` en `container-runtime.txt`. De remote CI-resultaten staan afzonderlijk in GitHub Actions. Productie-loadtests, Azure-deployment, Entra ID, managed identity en een onafhankelijke juridische/securityreview zijn niet uitgevoerd.
