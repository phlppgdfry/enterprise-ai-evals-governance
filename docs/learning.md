# Leerboek en eigenaarschapstoets

Deze repo is met AI-assistentie gemaakt. Beheersing wordt niet automatisch afgeleid van een commit, testscore of bestand. Noteer je eigen antwoorden en wijzigingen vóór je voorbeeldoplossingen raadpleegt.

## Begrippen uit de implementatie

**Evaluatie versus unit test.** Een unit test controleert de software die de eval uitvoert. Een evaluatie beoordeelt een target op een dataset. De groene fixturecontrole bewijst dat bekende juiste antwoorden door de runner worden geaccepteerd. Ze meet geen modelkwaliteit.

**Groundedness versus bron-ID.** Een juiste bron-ID voorkomt geen verzonnen claim. Deze runner controleert alleen bronlidmaatschap en trefwoorden. Een domeinexpert moet controleren of de bron de claim ondersteunt; een semantic judge heeft ook kalibratie nodig.

**Regressiegate.** Een lagere pass rate is alleen vergelijkbaar wanneer de cases hetzelfde zijn. Daarom moeten datasethash en geordende case-ID's overeenkomen. Een aangepaste dataset vereist een nieuwe, beoordeelde baseline.

**Fail closed.** Een timeout, kapotte JSON of onverwachte toolcall geeft geen groen resultaat. De runner bewaart het fouttype en blokkeert de release. Een overkoepelende configuratiefout geeft CLI exit 2, een geëvalueerde slechte respons exit 1.

**Policy versus autorisatie.** Het policy-endpoint beschrijft nodige controles. Een antwoord met menselijke goedkeuring nodig is zelf geen menselijke goedkeuring. Het mag geen boeking of externe actie vrijgeven.

**Observability versus opslag.** De run-ID, checks, latency en geschatte kosten helpen verklaren waarom een gate faalt. De SQLite-auditlog is niet onveranderlijk, geen volledig distributed tracing-systeem en geen vervanging voor providerfacturatie.

## Oefeningen: uitleggen

1. Teken zonder hulp de weg van `POST /runs` tot database en HTML-rapport.
2. Toon waar API-key en rol worden gecontroleerd. Waarom verandert `X-Role: governor` niets?
3. Leg uit hoe een antwoord met de woorden "12 months" toch onjuist kan zijn en slagen.
4. Bereken zelf het kostenresultaat voor 100 inputtokens en 20 outputtokens met de defaulttarieven.
5. Verklaar waarom een fixture-pass-rate van 100% geen cv-claim "100% nauwkeurig AI-systeem" rechtvaardigt.

## Oefeningen: aanpassen

1. Voeg een case toe met een juist antwoord en een vervalste, niet-toegestane bron-ID. Schrijf de falende regressietest eerst.
2. Voeg een nieuwe tool met strikte argumenten toe. Bewijs dat een gewijzigde `invoice_id` blokkeert.
3. Maak een Nederlandse datasetvariant. Bepaal of dezelfde substringchecks eerlijk werken voor synoniemen.
4. Schrijf een targetadapter die een lokale testtoepassing aanspreekt, zonder `expected`-velden door te geven.
5. Voeg een bewaarbeleid toe met tests voor verlopen en nog geldige runs. Houd rekening met auditretentie.

## Oefeningen: diagnosticeren

1. Laat het target timeouten. Toon welke exitcode ontstaat, wat in het rapport staat en wat bewust niet wordt gelogd.
2. Verander één byte in de dataset en vergelijk met de oude baseline. Leg de fout uit zonder de hashcontrole te verwijderen.
3. Stel `min_pass_rate` in op 0 en voer de onveilige fixture uit. Toon waarom de release nog steeds wordt geblokkeerd.
4. Start twee evaluaties tegelijkertijd. Leg de beperkingen van de proceslock uit, ook met twee Uvicorn-workers.
5. Maak een HTML-case-ID met `<script>` en toon dat het rapport de tekst escape't.

## Gespreksantwoord dat bij de bewijsstand past

"Ik heb een lokale evaluatiereferentie gebouwd met synthetische cases, expliciete negatieve controles, strikte toolcontracten, autorisatie en reproduceerbare rapporten. De checks zijn bewust beperkt: bron-ID's en trefwoorden bewijzen geen semantische waarheid. Voor een productiepilot zou ik domeinexperts een onafhankelijke dataset laten labelen, de echte toepassing via de HTTP-adapter testen en reviews plus operationele controles toevoegen."

Claim alleen dat je dit zelf begrijpt wanneer je de uitleg-, aanpas- en diagnosetoets zelfstandig kunt uitvoeren. Productie-ervaring, Azure-deployment en wettelijke conformiteit zijn hier niet aangetoond.
