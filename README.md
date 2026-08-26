# LIS Bridge — Prototipo (trascrizione in tempo reale)

Prototipo per persone sorde con la LIS come prima lingua: ascolta una
discussione in italiano, mostra la trascrizione **in tempo reale** e
traduce ogni frase in glosse LIS.

## Come funziona

1. Il browser registra il microfono e invia l'audio **in streaming** (WebSocket)
   direttamente ad AssemblyAI, che trascrive in tempo reale con diarizzazione.
2. Ogni frase completata viene tradotta al volo in glosse LIS (LLM via Groq).
3. La pagina mostra la trascrizione live e, sotto ogni frase, italiano
   semplificato + glosse LIS.

## Chiavi API necessarie (entrambe gratuite)

1. **AssemblyAI** → https://www.assemblyai.com/app (streaming + speaker)
2. **Groq** → https://console.groq.com/keys (traduzione in LIS)

Imposta le variabili d'ambiente (permanenti):

```powershell
setx ASSEMBLYAI_API_KEY "la_tua_chiave_assemblyai"
setx GROQ_API_KEY "gsk_la_tua_chiave_groq"
```

Poi chiudi e riapri PowerShell.

## Installazione

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Richiede `ffmpeg` installato (per la conversione audio) e nel PATH.

## Avvio

```powershell
venv\Scripts\python.exe app.py
```

Apri http://localhost:5000, premi "Avvia" e parla. La trascrizione appare
in tempo reale; ogni frase viene tradotta in LIS automaticamente.

## Struttura

- `app.py` — server Flask (token streaming + traduzione LIS)
- `asr.py` — upload/trascrizione AssemblyAI (fallback, non usato in streaming)
- `lis_translator.py` — traduzione italiano → glosse LIS (Groq)
- `glossary.py` — glossario concetti → segni LIS
- `data/glossary.json` — glossario (da curare con un interprete)
- `templates/index.html` — interfaccia web in tempo reale

## Prossimi passi (da validare con un interprete LIS)

- Sostituire le glosse testuali con **video reali** (campo `video` nel glossario)
- Migliorare il prompt LIS (grammatica, spazio, componenti non manuali)
- Integrare un avatar/ATLAS per la traduzione piena
