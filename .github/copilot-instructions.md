<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Image Duplicate Finder - Copilot Instructions

Questo è un progetto Python per trovare immagini duplicate utilizzando algoritmi di hash e confronto pixel per pixel.

## Contesto del progetto

- **Linguaggio**: Python 3.7+
- **Librerie principali**: Pillow, pillow-heif, hashlib, pathlib, Flask, tkinter
- **Tipo progetto**: Script a riga di comando + GUI desktop + Web interface
- **Obiettivo**: Identificare immagini duplicate in cartelle e sottocartelle
- **Formati supportati**: JPG, PNG, GIF, BMP, TIFF, WebP, HEIC, HEIF
- **Interfacce**: CLI, GUI desktop (tkinter), Web app (Flask)

## Linee guida per il codice

1. **Gestione errori**: Sempre utilizzare try-except per operazioni su file e immagini
2. **Performance**: Ottimizzare per grandi quantità di file (leggere a blocchi, progressi)
3. **Memoria**: Non caricare tutte le immagini in memoria contemporaneamente
4. **Compatibilità**: Supportare Windows, macOS e Linux
5. **Logging**: Utilizzare la modalità verbose per debugging

## Standard di codifica

- Utilizzare type hints per tutte le funzioni
- Documentare le classi e metodi con docstring
- Seguire PEP 8 per la formattazione
- Utilizzare Path objects invece di stringhe per i percorsi
- Gestire gracefully i casi in cui Pillow o pillow-heif non sono installati
- Ottimizzare confronto pixel per immagini di grandi dimensioni (campionamento)

## Algoritmi implementati

1. **Hash MD5**: Per confronto veloce del contenuto file
2. **Confronto pixel**: Per verifica accurata delle immagini  
3. **Metadati**: Data creazione, dimensioni, EXIF per informazioni aggiuntive

## Testing

- Testare con diversi formati immagine
- Verificare comportamento con file corrotti
- Testare performance su cartelle con molti file
- Verificare gestione di percorsi con caratteri speciali
