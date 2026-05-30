# Formato dei dati

I dati genealogici vivono in questo directory, in formato JSON strutturato.

## Struttura generale

```
{
  "individuals": [...],      // Lista di persone
  "relationships": [...],    // Liste di relazioni tra persone
  "sources": [...]           // Catalogo di fonti documentali
}
```

## Individuals (Persone)

Ogni persona è un oggetto con questi campi:

| Campo | Tipo | Obbligatorio | Descrizione |
|-------|------|---|---|
| `id` | string | ✓ | Identificatore univoco: P001, P002, ... |
| `surname` | string | ✓ | Cognome (in maiuscole per coerenza) |
| `givenNames` | string | ✓ | Nome/i di battesimo |
| `birthYear` | integer \| null | | Anno di nascita (es. 1795) |
| `birthPlace` | string \| null | | Luogo di nascita (es. "Sardagna, Trentino") |
| `deathYear` | integer \| null | | Anno di morte (null se sconosciuto o viva) |
| `spouse` | string \| null | | Nome del coniuge (se non nel database come ID separato) |
| `emigration.destination` | string \| null | | Paese di emigrazione: "USA", "ARG", "BRA", "CAN" |
| `emigration.year` | integer \| null | | Anno di emigrazione |
| `notes` | string \| null | | Note libere (soprannomi, storie famigliari, ecc.) |

### Esempio

```json
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
```

## Relationships (Relazioni)

Ogni relazione descrive un legame tra due persone, con prova documentale.

| Campo | Tipo | Obbligatorio | Descrizione |
|-------|------|---|---|
| `from` | string | ✓ | ID della persona A |
| `to` | string | ✓ | ID della persona B |
| `type` | string | ✓ | Tipo di relazione (vedi sotto) |
| `sources` | array | ✓ | Array di fonti che provano il legame (almeno 1) |

### Tipi di relazione

- **`filial`** — genitore → figlio/a (provato)
- **`marriage`** — matrimonio/unione (provato)
- **`probable_father`** — paternità dubitativa/probabile
- **`probable_mother`** — maternità dubitativa/probabile
- **`same_person`** — deduplica (questa persona è la stessa di quella)

### Struttura di una fonte

Ogni relazione ha un array `sources` con almeno un elemento. Ogni fonte è:

```json
{
  "type": "parrocchiale|manifesto|civile|censimento|archivio|stampa|altro",
  "reference": "Battesimi Sardagna 1795, p. 42",
  "date": "1795-06-15",  // YYYY-MM-DD, opzionale
  "description": "Battesimo di Dominicus, figlio di Giacomo",
  "url": "https://...",  // link a immagine/archivio, opzionale
  "sourceId": "src_001"  // se la fonte è già nel catalogo, opzionale
}
```

### Esempio di relazione

```json
{
  "from": "P001",
  "to": "P003",
  "type": "filial",
  "sources": [
    {
      "type": "parrocchiale",
      "reference": "Battesimi Sardagna 1795, p. 42",
      "date": "1795-06-15",
      "description": "Battesimo di Dominicus, figlio legittimo di Giacomo e Margherita Anesi"
    }
  ]
}
```

### Deduplica (same_person)

Se scopri che due ID rappresentano la stessa persona:

```json
{
  "from": "P022",
  "to": "P404",
  "type": "same_person",
  "sources": [
    {
      "type": "archivio",
      "reference": "Comparazione battesimi + manifesti",
      "description": "Gioachino Demozzi (P022) = Eugenio Giovanni (P404). Stessi genitori (P008+P???), stessa data di nascita (1869). Manifesti Ellis Island confermano nome Gioachino."
    }
  ]
}
```

Il viewer userà queste per fare la "fusione" logica (visualizzare un solo nodo).

## Sources (Catalogo di fonti)

Opzionale, ma consigliato se una fonte viene citata più volte.

```json
{
  "id": "src_001",
  "title": "Battesimi Sardagna (1790-1810)",
  "type": "parrocchiale",
  "archive": "Archivio Parrocchiale di Sardagna",
  "url": "https://example.com/...",
  "notes": "Microfilm conservati presso l'Archivio di Stato di Trento, fondo xyz"
}
```

Poi nelle relazioni, puoi usare `sourceId: "src_001"` per evitare duplication.

## Convenzioni

### ID univoci

- Ogni persona ha un ID unico: `P###` (P001, P999, ecc.)
- Non riutilizzare mai un ID, anche se elimini una persona
- Usa deduplica (`same_person`) se scopri errori

### Nomi

- `surname`: **in maiuscole**, es. "DEMOZZI" (rende facile sorting e matching)
- `givenNames`: capitalized, es. "Giacomo Dominico" (più nomi vanno con spazio)
- Soprannomi, varianti, nomi italianizzati → campo `notes`

### Date

- Sempre `YYYY-MM-DD` (ISO 8601) quando complete
- Se solo anno: `YYYY` oppure `null` (non "1795?" o "ca. 1795")
- Incertezza → nota in `notes`, non nel campo data

### Privacy

- **Soglia 1926**: chiunque nato dopo il 1926 senza data di morte provata è escluso
- **Eccezione**: manifesti/censimenti pubblici americani nominano già gli emigrati
- **Dubbio**: escludi o anonimizza, e apri una issue per discussione

## Come contribuire

1. Modifica `sardagna.json` aggiungendo persone/relazioni
2. Cita sempre una fonte per ogni relazione
3. Esegui `python3 scripts/validate.py` per controllare il formato
4. Apri una Pull Request

Vedi [CONTRIBUTING.md](../CONTRIBUTING.md) per il flusso completo.

## Strumenti

### Validare localmente

```bash
python3 scripts/validate.py
```

### Visualizzare lo schema

- Copia `schema.json` e `sardagna.json` su https://www.jsonschemavalidator.net/
- Verifica validità del JSON

### Convertire a GEDCOM (futuro)

Quando avremo il parser,: `python3 scripts/to-gedcom.py data/sardagna.json > out.ged`

---

**Domande sul formato? Apri un'issue.**
