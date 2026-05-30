# Rete genealogica di Sardagna

**Sito live:** https://ttraveler01.github.io/sardagna-genealogy/

Un archivio visuale curato della diaspora trentino-tirolese: gli abitanti di Sardagna (Trentino) che emigrarono negli Stati Uniti tra il 1860 e il 1920, con fonti documentali e mappe interattive.

## Vision

Non è un albero generico dove "ognuno aggiunge il suo". È un archivio specifico di una comunità migratoria, con:
- **Curatela**: ogni fatto (nascita, emigrazione, paternità) deve citare la fonte
- **Qualità delle fonti**: registri parrocchiali, manifesti di navi, atti civili americani, archivi locali
- **Focus stretto**: Sardagna → Dubois PA e comunità italiane del Nord Est USA
- **Visualizzazione**: quello che WikiTree, FamilySearch e Geni non fanno bene

## Struttura

```
.
├── README.md                          # Questo file
├── CONTRIBUTING.md                    # Come contribuire
├── schema.json                        # Validazione dati
├── .github/workflows/
│   └── validate.yml                   # CI: valida ogni PR
├── data/
│   ├── README.md                      # Guida al formato dati
│   └── sardagna.json                  # Dati (JSON strutturato)
└── viewer/
    └── index.html                     # Visualizzatore (carica da data/)
```

## Per iniziare

### Come contribuire

Leggi [CONTRIBUTING.md](CONTRIBUTING.md). In sintesi:
1. Clona il repo
2. Aggiungi/modifica persone e relazioni in `data/sardagna.json`
3. Cita le fonti (registro, manifesto, atto civile)
4. Apri una Pull Request

La CI valida automaticamente il formato. Niente dati su persone potenzialmente viventi.

### Correre il viewer localmente

```bash
# Serve il repo su http://localhost:8000
python3 -m http.server 8000
# Apri viewer/index.html nel browser
```

## Formato dati

I dati sono in `data/sardagna.json`, un formato strutturato con:
- **Persone**: id, nome, cognome, data di nascita, coniuge, emigrazione
- **Relazioni**: filiazione, paternità probabile, matrimonio, stessa persona
- **Fonti**: strutturate con tipo (parrocchia, manifesto, civile, archivio), data, riferimento

Ogni fatto deve avere almeno una fonte.

Vedi `data/README.md` per la specifica completa.

## Privacy

Convenzione genealogica ristretta:
- **Soglia di 100 anni**: nato da meno di ~100 anni e non provato deceduto → escluso
- **Nessun dato di persone viventi** (o presumibilmente viventi)
- **Cittadinanza rispettata**: dati americani sono fonti pubbliche (manifesti, censimenti); dati italiani richiedono consenso

Vedi `CONTRIBUTING.md` "Privacy & GDPR" per i dettagli.

## Tecnologia

- **Viewer**: Canvas 2D con force-directed graph (Sardagna.js)
- **Dati**: JSON strutturato + JSON Schema per la validazione
- **CI**: GitHub Actions — valida schema, sourcing, privacy su ogni PR

## Licenza

CC BY-SA 4.0 — attributo obbligatorio, condivisione con stessi termini.

---

**Fatto da**: [crediti qui]  
**Ultima validazione**: [data]  
**Prossimi step**: ricerca per nome, deep-link per persona, GEDCOM export
