# Guida: creare i segni LIS (codici FSW) per il dizionario

Questa guida serve al linguista/interprete LIS per generare i codici SignWriting
(FSW) da inserire nel dizionario dell'app.

## Lo strumento principale: SignMaker

**SignMaker** è l'editor online (gratuito) per disegnare i segni in SignWriting.

- **URL:** https://www.sutton-signwriting.io/signmaker/

Si usa "point-and-click": scegli la configurazione della mano, il movimento,
l'orientamento, ecc., e l'editor genera automaticamente il **codice FSW**
(una stringa tipo `M518x533S1870a489x515...`).

### Passi per creare un segno

1. Apri SignMaker
2. Disegna il segno selezionando i simboli (mani, movimento, espressioni)
3. Il codice **FSW** compare in alto (o nell'URL con parametro `fsw=...`)
4. Copia quel codice

### Alternative

- **SignPuddle 2.0** (https://www.signbank.org/signpuddle) — dizionario/editor
  con più lingue dei segni, incluso italiano. Ogni raccolta è esportabile in FSW.
- **SignPuddle 3 beta** (https://signpuddle.com) — versione più recente
- **Delegs Editor** (https://www.signbank.org/delegs.html) — altro editor SignWriting
- **SignWriter Studio** — programma desktop con dizionario

## Come inserire il codice nell'app

1. Apri la pagina di amministrazione dell'app: `/admin`
2. Nel campo "Glossa" scrivi la parola in MAIUSCOLO (es. `CASA`)
3. Nel campo "FSW" incolla il codice copiato da SignMaker
4. Spunta "Validato da linguista"
5. Clicca "Salva segno" — vedi subito l'anteprima del simbolo

## Fonti di riferimento per i segni LIS esistenti

Prima di disegnare un segno da zero, controlla se esiste già:

- **SpreadTheSign** (https://spreadthesign.com) — video-dizionario con segni LIS
  reali (video di segnanti). Utile come riferimento visivo del segno corretto.
- **SignPuddle** — raccolte SignWriting esistenti per la LIS e altre lingue
- Manuale CNR "Scrivere la LIS con il Sign Writing" (PDF gratuito) — la guida
  ufficiale italiana all'adattamento del SignWriting alla LIS

## Nota importante

- I segni vanno disegnati seguendo la **grammatica SignWriting adattata alla LIS**
  (vedi manuale CNR). Non copiare segni ASL: la LIS ha segni propri.
- Un segno può avere più varianti regionali: segnare nel campo "nota" quale
  variante è stata scelta.

## Esempio di codice FSW

`M518x533S1870a489x515S18701482x490S20500508x496S2e734500x468`

Questa è solo una stringa di esempio (dalla documentazione ufficiale SignWriting)
e NON corrisponde a un segno LIS specifico: serve solo a testare il rendering.
