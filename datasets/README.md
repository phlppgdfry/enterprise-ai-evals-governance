# Datasetlocatie

De versiegebonden dataset en handgeschreven antwoorden staan in `evalgov/datasets/`, zodat ze ook in een geïnstalleerd Python-wheel beschikbaar zijn. De CLI gebruikt deze pakketdata standaard. `scripts/build_synthetic_dataset.py` bouwt ze opnieuw uit expliciet geschreven synthetische cases.

De 16 cases vallen onder grounding (3), weigering (2), privacy (3), injection (3), access (2) en tools (3). De goede fixture is een positieve controle; de onveilige fixture verandert doelgericht acht antwoorden/toolcalls en moet de release blokkeren. Geen van beide fixtures roept een model aan.
