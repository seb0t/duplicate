# 🔍 Image Duplicate Finder

Un potente tool Python per trovare e gestire immagini duplicate con interfaccia grafica moderna e sistema di temi multipli.

![Version](https://img.shields.io/badge/version-2.3-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## ✨ Caratteristiche Principali

### 🎨 **Interfaccia Moderna con Temi Multipli**
- **4 temi professionali**: Chiaro, Notturno, Neon, Pro
- **Cambio istantaneo**: Tutti i widget si aggiornano dinamicamente
- **Design responsivo**: Layout moderno con box arrotondati e colori coerenti

### 🔍 **Algoritmi di Rilevamento Avanzati**
- **Hash MD5**: Confronto veloce del contenuto file
- **Pixel-per-pixel**: Verifica accurata delle immagini (con progress bar dettagliata)
- **Metadati EXIF**: Analisi data creazione, dimensioni, formato

### �️ **Gestione Sicura dei File**
- **Cestino temporaneo**: I duplicati vengono spostati (non eliminati)
- **Controlli di sicurezza**: Previene eliminazione accidentale
- **Ripristino facile**: Possibilità di recuperare file spostati

### 📊 **Anteprime e Analisi**
- **Thumbnail integrate**: Visualizzazione rapida delle immagini
- **Finestra di confronto**: Confronto visivo side-by-side
- **Report dettagliati**: Analisi completa con statistiche spazio

### 🚀 **Interfacce Multiple**
- **GUI Desktop**: Interfaccia principale con Tkinter
- **Web App**: Accesso tramite browser con Flask
- **CLI**: Utilizzo da riga di comando per automazione

## 📦 Installazione

### Prerequisiti
- Python 3.7 o superiore
- pip (gestore pacchetti Python)

### Setup Rapido

1. **Clona o scarica il progetto**
```bash
git clone <repository-url>
cd image-duplicate-finder
```

2. **Installa le dipendenze**
```bash
pip install -r requirements.txt
```

3. **Avvia l'applicazione**
```bash
python gui_interface.py
```

## 🎯 Utilizzo

### 🖥️ Interfaccia Grafica (Raccomandata)

```bash
python gui_interface.py
```

**Funzionalità principali:**
- Selezione directory con browser integrato
- Opzioni di scansione configurabili
- Progress bar in tempo reale
- Gestione interattiva dei duplicati con anteprime
- Sistema temi per personalizzazione

### 🌐 Interfaccia Web

```bash
python web_interface.py
```

Accedi tramite browser: `http://localhost:5000`

### � Riga di Comando

```bash
python image_duplicate_finder.py /path/to/directory [options]
```

**Opzioni disponibili:**
- `--pixel-verify`: Abilita verifica pixel-per-pixel
- `--verbose`: Output dettagliato
- `--help`: Mostra aiuto completo

## 🎨 Temi Disponibili

### 🌞 **Tema Chiaro**
- Design pulito e minimalista
- Perfetto per uso diurno
- Colori ad alto contrasto

### 🌙 **Tema Notturno**
- Riduce affaticamento visivo
- Ideale per sessioni lunghe
- Palette scura elegante

### ⚡ **Tema Neon**
- Stile cyberpunk futuristico
- Verde neon accattivante
- Per un look moderno

### 💼 **Tema Pro**
- Aspetto aziendale
- Colori sobri e professionali
- Perfetto per ambienti lavorativi

## 📋 Formati Supportati

✅ **Formati Standard**
- JPG/JPEG
- PNG
- GIF
- BMP
- TIFF/TIF

✅ **Formati Moderni**
- WebP
- HEIC (iPhone)
- HEIF

## 🛠️ Caratteristiche Tecniche

### Algoritmi di Confronto
- **Hash MD5**: Veloce e affidabile per file identici
- **Confronto pixel**: Precisione massima per immagini elaborate
- **Campionamento intelligente**: Ottimizzazione per immagini grandi (>1M pixel)

### Sicurezza
- **Cestino temporaneo**: Nessuna eliminazione diretta
- **Backup automatico**: File spostati in `garbage_duplicates/`
- **Controlli di integrità**: Verifica prima di ogni operazione

### Performance
- **Processing multithreaded**: Interfaccia reattiva durante l'analisi
- **Memory efficient**: Gestione ottimizzata della memoria
- **Progress tracking**: Monitoraggio dettagliato delle operazioni

## 📊 Output e Report

### Informazioni Fornite
- **Numero totale immagini** analizzate
- **Gruppi di duplicati** trovati
- **Spazio recuperabile** in MB/GB
- **Percorsi completi** di tutti i file
- **Metadati EXIF** (quando disponibili)
- **Suggerimenti** per eliminazione sicura

### Formati Export
- **Report testuale** (.txt)
- **Log dettagliato** (modalità verbose)
- **Statistiche riassuntive** nell'interfaccia

## 🔧 Configurazione

### Opzioni Avanzate
- **Verifica pixel-per-pixel**: Per massima precisione
- **Output verbose**: Per debugging e analisi dettagliate
- **Temi personalizzabili**: Sistema facilmente espandibile

### File di Configurazione
Il progetto include file batch per avvio rapido:
- `run_gui.bat` - Avvia interfaccia grafica
- `run_web.bat` - Avvia server web
- `run_duplicate_finder.bat` - Avvia con parametri predefiniti

## 🤝 Contribuzione

Il progetto è aperto a contribuzioni! Areas di interesse:
- Nuovi formati di immagine
- Algoritmi di confronto aggiuntivi
- Temi personalizzati
- Ottimizzazioni performance
- Traduzioni interfaccia

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi file `LICENSE` per dettagli.

## 🆘 Supporto

### Problemi Comuni
- **Errore moduli mancanti**: Esegui `pip install -r requirements.txt`
- **Immagini HEIC non supportate**: Installa `pillow-heif`
- **Performance lente**: Usa solo hash MD5 per directory grandi

### Segnalazione Bug
Crea una issue su GitHub con:
- Versione Python utilizzata
- Sistema operativo
- Log di errore completo
- Steps per riprodurre il problema

---

**Sviluppato con ❤️ per la gestione efficiente delle collezioni di immagini**

*Image Duplicate Finder v2.3 - Sistema Temi Avanzato*
```bash
python gui_interface.py
```
Apre una finestra grafica intuitiva con:
- **🎨 Sistema temi multipli**: 4 temi (Chiaro, Notturno, Neon, **Pro** di default) selezionabili
- **Layout a due pannelli** con design moderno e colorato
- **Selezione directory** tramite browser grafico
- **Barra di progresso** in tempo reale con status dettagliato
- **Visualizzazione risultati** raggruppata e ben organizzata
- **🎯 Controlli eliminazione sicuri**:
  - 📦 **Cestino temporaneo**: File spostati in `garbage_duplicates/` (recuperabili)
  - Thumbnail di anteprima per ogni immagine (60x45px)
  - Checkbox per ogni file duplicato
  - Selezione automatica di tutti i duplicati
  - Protezione anti-eliminazione totale
  - 🗂️ **Gestione cestino**: Apertura cartella, svuotamento, ripristino file
- **👁️ Finestra di preview avanzata**:
  - Confronto affiancato di tutte le immagini
  - Vista singola con navigazione e metadati completi
  - Apertura cartelle e eliminazione diretta
  - Supporto completo per tutti i formati immagine
- **Identificazione automatica** del file "originale" da mantenere
- **Calcolo spazio recuperabile** in tempo reale
- **Salvataggio report** completi con un click

### 🌐 Interfaccia Web (Avanzata v2.3)
```bash
python web_interface.py
```
Poi apri il browser su: `http://localhost:5000`

**Nuove funzionalità 2.3:**
- **📂 Browser directory integrato**: Esplora il filesystem senza digitare percorsi
- **🌙 Tema scuro**: Toggle istantaneo tra tema chiaro e scuro (memorizzato)
- **🗑️ Gestione eliminazione sicura completa**: 
  - Selezione granulare dei duplicati con checkbox per file
  - Cestino temporaneo `web_garbage_duplicates/` per recupero
  - Eliminazione definitiva controllata con conferme multiple
  - Statistiche spazio recuperato in tempo reale
- **⚡ Selezione automatica**: Un click per selezionare tutti i duplicati di ogni gruppo
- **🗂️ Gestione cestino avanzata**: Visualizzazione file, ripristino ed eliminazione definitiva
- **🛡️ Protezione anti-eliminazione**: Impossibile eliminare file "originali" marcati con ⭐

Interfaccia web con funzionalità identiche alla versione desktop:
- Design responsive con sistema di temi
- Browser directory point-and-click per Windows/Mac/Linux
- Controlli di eliminazione sicuri identici alla GUI
- Gestione completa cestino temporaneo con statistiche

### ⌨️ Riga di Comando (Avanzata)
```bash
python image_duplicate_finder.py "C:\MieImmagini"
```

### Con opzioni avanzate (riga di comando)
```bash
# Con output dettagliato
python image_duplicate_finder.py "C:\MieImmagini" --verbose

# Salva risultati in un file
python image_duplicate_finder.py "C:\MieImmagini" --output "report_duplicati.txt"

# Solo confronto hash (più veloce)
python image_duplicate_finder.py "C:\MieImmagini" --no-pixel-verify
```

### Parametri disponibili

- `directory` - Percorso della cartella da scansionare (obbligatorio)
- `--verbose, -v` - Abilita output dettagliato durante l'esecuzione
- `--output, -o` - File dove salvare il report dei risultati
- `--no-pixel-verify` - Salta verifica pixel per pixel (più veloce ma meno preciso)

## Come funziona

1. **Scansione**: Il programma scansiona ricorsivamente la directory specificata cercando file immagine
2. **Hash del contenuto**: Calcola l'hash MD5 del contenuto di ogni file per identificare duplicati identici
3. **Verifica pixel**: Opzionalmente confronta le immagini pixel per pixel per massima precisione  
4. **Metadati**: Estrae informazioni come data di creazione, dimensioni e dati EXIF
5. **Report**: Genera un report dettagliato con tutti i duplicati trovati

## Output esempio

```
🔍 IMAGE DUPLICATE FINDER
========================================
📁 Directory da scansionare: C:\MieImmagini

Trovate 150 immagini da analizzare.
Calcolando hash dei file...
Progresso: 100/150
Trovati 3 gruppi di duplicati basati su hash.
Verificando duplicati con confronto pixel...
Verificati 3 gruppi di duplicati reali.

📋 RISULTATI - Trovati 3 gruppi di immagini duplicate:
================================================================================

🔍 Gruppo 1 (2 immagini duplicate):
   Hash: a1b2c3d4e5f6...
   Dimensione file: 2,048,576 bytes
   Spazio sprecato: 2,048,576 bytes
   1. C:\MieImmagini\foto1.jpg
      📅 Creato: 2024-01-15 14:30:25
      📐 Dimensioni: (1920, 1080)
   2. C:\MieImmagini\Backup\foto1_copia.jpg
      📅 Creato: 2024-01-15 14:30:25
      📐 Dimensioni: (1920, 1080)

================================================================================
📊 RIEPILOGO:
   • Immagini totali analizzate: 150
   • Gruppi di duplicati: 3
   • Immagini duplicate da rimuovere: 5
   • Spazio totale recuperabile: 15,728,640 bytes (15.00 MB)
```

## 🗑️ Gestione Sicura dei Duplicati (Solo GUI Desktop)

La GUI desktop offre funzionalità avanzate per l'eliminazione controllata dei duplicati:

### Caratteristiche di Sicurezza
- **Identificazione automatica dell'originale**: Il programma suggerisce quale file mantenere
- **Selezione granulare**: Checkbox per ogni singolo file
- **Selezione automatica**: Un click per selezionare tutti i duplicati preservando gli originali
- **Protezione anti-eliminazione totale**: Impedisce di eliminare tutti i file di un gruppo
- **Conferma multipla**: Warning prima dell'eliminazione con dettagli dello spazio liberato
- **Aggiornamento automatico**: Dopo l'eliminazione, riavvia l'analisi per mostrare il nuovo stato

### Come Usare i Controlli di Eliminazione
1. **Avvia l'analisi** e attendi i risultati
2. **Controlla i gruppi** nella sidebar destra - ogni gruppo mostra:
   - File "originale" consigliato (⭐ verde)
   - File duplicati da eliminare (🗑️ rosso)
   - Spazio recuperabile per gruppo
3. **Seleziona i file** da eliminare:
   - Usa le checkbox individuali, oppure
   - Click su "⚡ Selezione Automatica Duplicati" per selezione intelligente
4. **Verifica la selezione** - Il pulsante mostra quanti file e MB verranno eliminati
5. **Elimina i file** - Click su "🗑️ Elimina File Selezionati" e conferma

### Esempio di Controlli
```
🎯 Gruppo 1 (3 file)                    💾 Spazio recuperabile: 4.2 MB
⚡ Seleziona tutti i duplicati

☐ ⭐ foto_originale.jpg (ORIGINALE - MANTIENI)
   📁 Directory principale
☑ 🗑️ foto_copia.jpg  
   📁 Backup_Foto
☑ 🗑️ IMG_20240115_143025.jpg
   📁 Screenshots
```

## Sicurezza

⚠️ **IMPORTANTE**: 
- **CLI e Web**: Identificano solo i duplicati, NON li eliminano automaticamente
- **GUI Desktop**: Offre eliminazione controllata con multiple conferme di sicurezza
- **Backup raccomandato**: Fai sempre un backup prima di eliminare file importanti

## Requisiti di sistema

- Python 3.7+
- Pillow (per elaborazione immagini)
- pillow-heif (per supporto HEIC/HEIF - opzionale)
- Spazio sufficiente per l'esecuzione (il programma non modifica i file originali)

## Note tecniche

- **Algoritmo hash**: Utilizza MD5 per velocità, ma è possibile modificare per SHA256
- **Memoria**: Carica una sola immagine alla volta per efficienza memoria  
- **Performance**: Su SSD, circa 100-200 immagini/secondo per hash, 5-10/secondo per confronto pixel
- **Precisione**: Hash identico = file identico al 100%. Confronto pixel aggiunge verifiche extra

## Risoluzione problemi

**"Pillow non è installato"**: Esegui `pip install Pillow`

**"Directory non trovata"**: Verifica che il percorso sia corretto e accessibile

**Performance lente**: Usa `--no-pixel-verify` per analisi più rapide

**Memoria insufficiente**: Il programma è ottimizzato, ma per dataset enormi considera di dividere l'analisi

## Licenza

Questo progetto è distribuito sotto licenza MIT.
