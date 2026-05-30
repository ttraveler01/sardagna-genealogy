# Guida alla Contribuzione

Benvenuto. Questa guida spiega come aggiungere dati genealogici a questo archivio.

## I tre princìpi

1. **Una fonte per ogni fatto** — niente affermazioni senza documentazione
2. **Deduplica accurata** — se una persona è già nel database, linkala piuttosto che replicarla
3. **Privacy by design** — niente dati su persone potenzialmente viventi

## Step 1: Capire il formato dati

I dati vivono in `data/sardagna.json`. È strutturato così:

```json
{
  "individuals": [
    {
      "id": "P001",
      "surname": "DEMOZZI",
      "givenNames": "Giacomo",
      "birthYear": 1764,
      "birthPlace": "Sardagna",
      "deathYear": null,
      "spouse": "Anesi Margherita",
      "emigration": {
        "destination": null,
        "year": null
      },
      "notes": "soprannome: Rizòti→Gèchi"
    }
  ],
  "relationships": [
    {
      "from": "P001",
      "to": "P003",
      "type": "filial",
      "sources": [
        {
          "type": "parrocchiale",
          "reference": "Battesimi Sardagna 1795, p. 42",
          "date": "1795-06-15",
          "description": "Battesimo di Dominicus, figlio di Giacomo"
        }
      ]
    }
  ],
  "sources": [
    {
      "id": "src_001",
      "title": "Battesimi Sardagna (1790-1810)",
      "type": "parrocchiale",
      "archive": "Archivio Parrocchiale di Sardagna",
      "url": "https://...",
      "notes": "Microfilm, conservati presso..."
    }
  ]
}
```

## Step 2: Aggiungi o modifica dati

### Aggiungere una nuova persona

1. Crea un nuovo oggetto in `individuals`
2. Usa un `id` unico (P###, es. P426)
3. Compila i campi: surname, givenNames, birthYear, birthPlace
4. Se conosci la morte: deathYear
5. Se emigrata: aggiungi `emigration.destination` e `emigration.year`

Esempio:

```json
{
  "id": "P426",
  "surname": "BERLOFFA",
  "givenNames": "Rosa Antonia",
  "birthYear": 1895,
  "birthPlace": "Sardagna",
  "deathYear": 1975,
  "spouse": null,
  "emigration": {
    "destination": "USA",
    "year": 1920
  },
  "notes": null
}
```

### Aggiungere una relazione

Crea un oggetto in `relationships`:

```json
{
  "from": "P001",
  "to": "P426",
  "type": "parent",
  "sources": [
    {
      "type": "parrocchiale",
      "reference": "Battesimi Sardagna 1895, p. 73",
      "date": "1895-03-22",
      "description": "Rosa Antonia, figlia di Giacomo e Anna"
    }
  ]
}
```

**Tipi di relazione ammessi:**
- `filial` — genitore → figlio/a
- `marriage` — marito ↔ moglie
- `probable_father` — paternità dubitativa
- `probable_mother` — maternità dubitativa
- `same_person` — deduplica esplicita (quando scopri che P022 = P404)

### Citare una fonte

Ogni `relationship` deve avere un array `sources` con almeno un elemento. Ogni fonte ha:

- `type` — `parrocchiale`, `manifesto`, `civile`, `censimento`, `archivio`, `stampa`, `altro`
- `reference` — descrizione breve, es. "Battesimi Sardagna 1795, p. 42"
- `date` — data del documento (YYYY-MM-DD se noto)
- `description` — una frase che spiega cosa dice il documento

Opzionale:
- `url` — link a immagine/archivio digitale
- `sourceId` — id da `sources[]` se la fonte è già catalogata

Esempi di fonti:

```json
{
  "type": "manifesto",
  "reference": "SS Vaderland, 15-05-1906, pagina manifest",
  "date": "1906-05-15",
  "description": "Silvio Berloffa, da Sardagna, destinazione Dubois PA",
  "url": "https://www.libertyellisfoundation.org/..."
}
```

```json
{
  "type": "parrocchiale",
  "reference": "Matrimoni Sardagna 1862, vol. 5, p. 18",
  "date": "1862-09-10",
  "description": "Matrimonio tra Luigia Degasperi e Fortunato Demozzi"
}
```

## Step 3: Privacy & GDPR

**Regola dura**: non aggiungere persone nate da meno di ~100 anni se non provato decedute.

Eccezione: dati pubblici americani (manifesti, censimenti) che già nominano persone immigrate sono OK se decedute o nate prima di ~1926.

Casi dubbi:
- Figlio/a di emigrati: se nato dopo 1930 negli USA → escludi o anonimizza (non mettere nome)
- Dati italiani attuali: niente nomi di persone viventi da registri contemporanei
- Quando in dubbio: togli il dato e discuti in PR

Vedi anche: GDPR Art. 6 (lawfulness), Art. 9 (sensitive data).

## Step 4: Validazione locale

Prima di fare la PR, valida localmente:

```bash
# Hai Python? Usa il validatore
python3 validate.py data/sardagna.json

# Oppure, nel browser, carica il JSON in uno schema validator online:
# https://www.jsonschemavalidator.net/
# Copia schema.json e sardagna.json
```

Se passa, sei pronto.

## Step 5: Apri una Pull Request

1. Clona il repo
2. Crea un branch: `git checkout -b add-rossi-family`
3. Modifica `data/sardagna.json`
4. Commit: `git commit -m "Add Rosa Berloffa (P426) and marriage to Giacomo"`
5. Push: `git push origin add-rossi-family`
6. Apri PR su GitHub

**Messaggio di PR**: spiega brevemente chi hai aggiunto e da dove vengono i dati.

Esempio:

```
Add Rosa Antonia Berloffa (P426)

- Nata 1895 a Sardagna, emigrata 1920 negli USA
- Fonte: battesimo parrocchiale (Sardagna, 1895); manifesto SS Vaderland (1920)
- Link marriage a Giacomo Demozzi via matrimonio 1915
```

La CI validerà automaticamente:
- Schema JSON ✓
- Sourcing (ogni fatto ha una fonte) ✓
- Privacy (no persone nate post-1920 senza morte provata) ✓

Se passa, un moderatore farà review (verifica fonti, deduplica, logica genealogica) e merge.

## Step 6: Deduplica (il caso difficile)

Se scopri che P022 e P404 sono la stessa persona:

1. **Non eliminarli**
2. Aggiungi una relazione `same_person` tra loro
3. Nella PR, spiega perché credi siano la stessa persona

```json
{
  "from": "P022",
  "to": "P404",
  "type": "same_person",
  "sources": [
    {
      "type": "archivio",
      "reference": "Comparazione manifesti + battesimi",
      "description": "Gioachino Demozzi (P022) = Eugenio Giovanni (P404), stessi genitori, stessa data di nascita (1869), stesso nome paterno (Gioachino/Eugenio sono varianti). Manifesti Ellis Island confermano nome Gioachino per l'immigrato."
    }
  ]
}
```

Poi, in una fase successiva, il viewer/builder farà la "fusione" canonica e userà un ID solo.

## FAQ

**Q: E se non ho una fonte precisa?**  
A: Non aggiungere il dato. O aggiungi con `sources: [{type: "oral", description: "Tradizione familiare..."}]` e chiaramente marked, ma per fatti rilevanti (nascita, emigrazione) è meglio documentazione solida.

**Q: Posso aggiungere fonti che non sono online?**  
A: Sì. Compila `reference` con dettagli (archivio, fondo, data) e `description` con cosa dice. Se in futuro la fonte è digitalizzata, aggiungi `url`.

**Q: Come gestisco nomi con varianti?**  
A: Campo `givenNames` è il nome "canonico". Soprannomi/varianti vanno in `notes`. Se è una deduplica di persone con nomi molto diversi, usa `same_person` + spiega in `sources`.

**Q: Cosa faccio con le date incerte?**  
A: Se sai solo l'anno, metti `birthYear: 1895` e `birthDate: null`. Se è davvero incerta, nota in `notes: "circa 1895"`.

**Q: Posso aggiungere altre famiglie (non Sardagna)?**  
A: No, per ora. Il progetto è specifico su Sardagna → diaspora USA. Se c'è un ramo collaterale da un'altra regione, apri una issue prima.

---

**Domande? Apri un'issue su GitHub o scrivi ai moderatori.**

Grazie per contribuire all'archivio.
