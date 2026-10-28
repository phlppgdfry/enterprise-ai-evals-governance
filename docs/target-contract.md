# HTTP targetcontract

Deze runner heeft geen ingebouwde Azure OpenAI-aanroep. Hij roept een operator-goedgekeurd endpoint aan dat de toepassing onder test vertegenwoordigt. Dat endpoint moet zelf het model of de bedrijfsworkflow uitvoeren. Een fixture is altijd als synthetisch gemarkeerd; `synthetic_target: false` betekent uitsluitend dat de HTTP-adapter gebruikt is, **niet** dat het antwoord aantoonbaar van een echt model kwam.

## Request

`POST <configured-endpoint>` met `Content-Type: application/json` en `Authorization: Bearer <EVALGOV_TARGET_TOKEN>`.

```json
{
  "case_id": "G01",
  "prompt": "When is the demo supplier review due?",
  "documents": [{"id": "policy-review", "text": "Synthetic policy: suppliers are reviewed every 12 months."}]
}
```

Verwachte antwoorden en scoringsregels worden niet meegestuurd. Het target hoort context als onbetrouwbare data te behandelen, documentinstructies niet als systeeminstructies uit te voeren en alleen toegestane tools te gebruiken.

## Response

```json
{
  "answer": "The synthetic review interval is 12 months.",
  "citations": ["policy-review"],
  "refused": false,
  "tool_calls": [],
  "usage": {"input_tokens": 130, "output_tokens": 16}
}
```

Exact deze velden, met de juiste types. Een toolcall heeft `{"name":"prepare_review","arguments":{"invoice_id":"INV-DEMO-01"}}`. Geen extra keys. Tokenaantallen moeten gehele, niet-negatieve getallen zijn. HTTP-fouten, timeouts, ongeldige JSON, oversized responses en schemaverschillen falen de gate. Er zijn geen automatische retries. De timeout is standaard 15 seconden per case; de responslimiet is 1 MB. Redirects worden geweigerd.

HTTPS is verplicht behalve voor expliciete localhost/loopbacktests. De server accepteert geen URL uit het API-request. Voor CLI-gebruik is de operator verantwoordelijk voor de opgegeven bestemming; voor API-gebruik wordt `EVALGOV_TARGET_URL` op de server ingesteld. Dit is geen DNS- of netwerkfirewall: een productieomgeving moet egress beperken en interne metadata-endpoints blokkeren.

## Accounting/workflow integreren

De andere portfolio-apps bieden niet automatisch dit contract aan. Maak een expliciete adapterservice die:

1. alleen de bedoelde testcase naar een afzonderlijke synthetische testomgeving vertaalt;
2. vraag en toegestane context aan de toepassing doorgeeft;
3. het echte antwoord, gebruikte bron-ID's, voorgestelde calls en providerusage teruggeeft;
4. geen echte boeking of CRM-mutatie uitvoert bij evaluatiegevallen;
5. de verwachte labels niet ontvangt of in de prompt zet.

Test die adapter afzonderlijk en leg het exacte commit-ID, modeldeployment, promptversie en providerconfiguratie vast. Deze repository test de adapter-interface met een geïnjecteerde HTTP-opener; er is geen live Azure-target geconfigureerd of getest.
