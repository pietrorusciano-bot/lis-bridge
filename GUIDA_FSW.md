# Guida: aggiungere i segni LIS (video o simboli) al dizionario

Questa guida serve al linguista/interprete LIS per aggiungere i segni all'app.

## Metodo 1 — VIDEO (consigliato)

Il video è il metodo più chiaro e preciso, perché mostra il segno LIS reale.

### Cosa serve

Un file video del segno (formato `mp4`, `webm` o `mov`), breve (2-4 secondi),
con il segnante inquadrato bene, mani e viso visibili.

### Come caricarlo

1. Apri la pagina di amministrazione dell'app: `/admin`
2. Nella sezione "Carica video del segno":
   - scrivi la glossa in MAIUSCOLO (es. `CASA`)
   - seleziona il file video
3. Clicca "Carica video"
4. Il video viene associato alla glossa e mostrato nell'app al posto del simbolo

### Da dove prendere i video

- **Registrare un segnante/interprete** (il metodo migliore e senza problemi di licenza)
- **SpreadTheSign** (https://spreadthesign.com) ha video di segni LIS reali,
  ma sono **proprietari**: NON si possono scaricare/ridistribuire senza
  autorizzazione del European Sign Language Centre. Usali solo come riferimento
  visivo per verificare il segno corretto.

## Metodo 2 — SIMBOLO SignWriting (alternativa)

Se non hai un video, puoi usare il simbolo disegnato in SignWriting.

### Strumento

**SignMaker** (https://www.sutton-signwriting.io/signmaker/) — editor online
gratuito: disegni il segno e ottieni il codice **FSW**.

### Come inserirlo

1. Apri `/admin`
2. Inserisci la glossa e il codice FSW
3. Vedi l'anteprima del simbolo
4. Clicca "Salva segno"

## Fonti di riferimento per il segno corretto

- **SpreadTheSign** (https://spreadthesign.com) — video-dizionario (solo consultazione)
- Manuale CNR "Scrivere la LIS con il Sign Writing" (PDF gratuito)

## Note importanti

- I segni LIS sono propri: non copiare segni ASL.
- Un segno può avere più varianti regionali: indica nella nota quale variante hai usato.
- I video caricati NON vanno nel codice sorgente (sono grandi): restano sul server.
