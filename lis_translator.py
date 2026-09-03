import json
import os

import requests

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = (
    "Sei un interprete professionista di LIS (Lingua dei Segni Italiana). "
    "Ricevi una trascrizione in italiano e devi produrre due risultati, "
    "ENTRAMBI esclusivamente in lingua ITALIANA: "
    "1) 'italiano': una versione semplificata del testo, in frasi brevi e chiare, in italiano. "
    "2) 'lis': la traduzione in glosse LIS, scritte in MAIUSCOLO, una per ogni segno, "
    "separate da un singolo spazio. Le glosse devono essere PAROLE ITALIANE "
    "(es. CASA, ANDARE, SCUOLA, FIGLIO, MEDICO). "
    "È ASSOLUTAMENTE VIETATO usare parole inglesi: traduci sempre in italiano. "
    "Usa la grammatica LIS: ordine Soggetto-Oggetto-Verbo, "
    "senza articoli, senza preposizioni, senza coniugazioni verbali, verbi all'infinito. "
    "Non inventare segni: se un concetto non ha un segno noto, usa una perifrasi semplice. "
    "La risposta deve essere esclusivamente un oggetto JSON con due campi, "
    '"italiano" e "lis", senza testo aggiuntivo, senza commenti, senza markdown.\n'
    "Esempio:\n"
    'Input: "Domani devo portare mio figlio a scuola"\n'
    'Output: {"italiano": "Domani porto mio figlio a scuola.", '
    '"lis": "DOMANI IO FIGLIO SCUOLA PORTARE"}'
)


import re


class LisTranslator:
    def __init__(self, api_key=None, model="openai/gpt-oss-120b"):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "GROQ_API_KEY mancante. Imposta la variabile d'ambiente GROQ_API_KEY."
            )
        self.model = model

    def translate(self, text):
        if not text.strip():
            return {"italiano": "", "lis": ""}

        response = requests.post(
            GROQ_CHAT_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                "temperature": 0.2,
            },
            timeout=120,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return self._parse(content)

    @staticmethod
    def _parse(content):
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
        content = re.sub(r"```(?:json)?", "", content).strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(content[start : end + 1])
            except json.JSONDecodeError:
                pass

        italiano = re.search(r'"italiano"\s*:\s*"((?:[^"\\]|\\.)*)"', content, re.DOTALL)
        lis = re.search(r'"lis"\s*:\s*"((?:[^"\\]|\\.)*)"', content, re.DOTALL)
        if italiano or lis:
            return {
                "italiano": italiano.group(1) if italiano else "",
                "lis": lis.group(1) if lis else "",
            }

        return {"italiano": "", "lis": "", "errore_lis": "risposta non JSON"}
