# Allen of Many

Vault Obsidian per il multiverso **Allen**, con pubblicazione automatica su **GitHub Pages** tramite MkDocs Material.

**Sito pubblico:** [https://dexrand.github.io/Allen-of-many/](https://dexrand.github.io/Allen-of-many/)

**Repository:** [github.com/dexRand/Allen-of-many](https://github.com/dexRand/Allen-of-many)

---

## Struttura del vault

| Cartella / file | Contenuto |
|-----------------|-----------|
| `Canon/` | Allen “canonici” |
| `404/` | Varianti non trovate / altri mondi |
| `zz_CIcli/` | Cicli temporali (`Primo`, `Presente`, …) |
| `zzz_Attachments/` | Immagini e allegati Obsidian |
| `ALLEN.md` | Nota indice (opzionale) |
| `.obsidian/` | Configurazione Obsidian (tema, plugin, esclusioni) |

Le note usano **wikilink** Obsidian (`[[Nota]]`, `![[immagine.png|300]]`, tag `[[+canon]]`).

---

## Uso con Obsidian

1. Apri questa cartella come vault in Obsidian.
2. Scrivi e collega le note come al solito; **non serve** convertire i link in Markdown standard.
3. Gli allegati vanno in `zzz_Attachments/` (impostazione predefinita del vault).

File di build e tooling **nascosti** nell’albero file (ma presenti su Git): `scripts/`, `hooks/`, `.github/`, `mkdocs.yml`, `content/`, `site/`, ecc. — vedi `userIgnoreFilters` in `.obsidian/app.json`.

---

## Pubblicazione sul web

### Cosa succede al push su `main`

Il workflow [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml):

1. Installa MkDocs e i plugin
2. Crea la cartella temporanea `content/` con symlink alle cartelle del vault
3. Esegue `mkdocs gh-deploy` sul branch **`gh-pages`**

### Impostazione GitHub Pages (importante)

In **Settings → Pages**:

| Campo | Valore |
|--------|--------|
| **Source** | Deploy from a branch |
| **Branch** | `gh-pages` |
| **Folder** | `/ (root)` |

Non usare **“GitHub Actions”** come sorgente Pages con questo setup: il deploy passa dal branch `gh-pages`, non dall’artifact Actions.

Dopo un push su `main`, controlla la tab **Actions** (workflow verde) e attendi 1–2 minuti.

---

## Build locale (anteprima)

**Requisiti:** Python 3.10+

```powershell
pip install -r requirements.txt
.\scripts\prepare-mkdocs.ps1
mkdocs serve
```

Apri l’URL indicato nel terminale (di solito `http://127.0.0.1:8000`).

Solo build statico:

```powershell
.\scripts\prepare-mkdocs.ps1
mkdocs build
```

Output in `site/` (ignorato da Git).

---

## Aggiungere contenuti

### Nuove note in `Canon/`, `404/`, `zz_CIcli/`

- Committa e pusha: compaiono sul sito al prossimo deploy.
- I `[[wikilink]]` tra note già pubblicate diventano link cliccabili.
- In fondo alle pagine, le **menzioni** (backlink) elencano chi linka quella nota — senza titolo di sezione.

### Immagini

- Salva in `zzz_Attachments/` (o lascia che Obsidian le metta lì).
- **Committa** le immagini su Git, altrimenti sul sito restano rotte.
- Sintassi supportata: `![[nome.png]]` e `![[nome.png|larghezza]]`.

### Nuova cartella in root (es. `NPC/`)

Al momento **non** è inclusa nel deploy automatico. Per pubblicarla, aggiungi una riga in `.github/workflows/deploy.yml` e in `scripts/prepare-mkdocs.ps1` (stesso elenco di `Canon`, `404`, `zz_CIcli`).

### Tag `[[+nome]]`

Sul sito vengono mostrati come testo (`+nome`), non come link — anche se esiste un file omonimo.

---

## Stack tecnico

| Componente | Ruolo |
|------------|--------|
| [MkDocs](https://www.mkdocs.org/) + [Material](https://squidfunk.github.io/mkdocs-material/) | Sito statico |
| `mkdocs-awesome-pages-plugin` | Navigazione dalle cartelle |
| `mkdocs-section-index` | Sezioni cliccabili nel menu |
| `hooks/obsidian_links.py` | Wikilink, embed immagini, tag |
| `hooks/backlinks.py` | Elenco menzioni in fondo pagina |
| GitHub Actions | Build e push su `gh-pages` |

Configurazione principale: [`mkdocs.yml`](mkdocs.yml).

---

## Licenza e crediti

Contenuto del vault: uso personale / di campagna.  
Tema Obsidian: ITS Theme (in `.obsidian/themes/`).
