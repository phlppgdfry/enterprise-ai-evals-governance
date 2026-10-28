# Rondleiding van twee minuten

**0:00–0:20 — Het probleem.** "Hoe voorkom je dat een nieuwe AI-versie onveilig gedrag introduceert?" Toon de datasethash en leg uit dat alle gegevens synthetisch zijn.

**0:20–0:45 — Positieve controle.** Voer `.venv/bin/evalgov --fixture good --out reports/good` uit. Toon in het HTML-rapport de fixturemarkering, contractchecks en kostenraming. Benoem dat dit geen modelbenchmark is.

**0:45–1:10 — Negatieve controle.** Voer `.venv/bin/evalgov --fixture unsafe --baseline reports/good/report.json --out reports/unsafe` uit. Toon de exitcode 1, een gelekte canary, een verkeerde bron en een gewijzigde toolparameter via de case-ID's en falende checks. De rapporten slaan de werkelijke antwoordtekst bewust niet op.

**1:10–1:35 — Verantwoordelijkheid.** Open `/docs`, voer een beleidsvraag uit met persoonsgegevens en een financiële actie. Toon `human_approval_required` en `authorization_to_execute: false`. Leg uit dat een technische test geen businessgoedkeuring of juridische conformiteit verleent.

**1:35–2:00 — Eigen inzicht.** Toon één test die je zelf kunt uitleggen en aanpassen. Sluit af met de resterende stap: een representatieve, onafhankelijk gelabelde dataset op een echte toepassing uitvoeren. Een Azure-implementatie is een integratiestap en wordt in deze demo niet geclaimd.
