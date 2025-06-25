# Image Duplicate Finder - Version Info

__version__ = "2.3.0"
__author__ = "Image Duplicate Finder Team"
__description__ = "Potente tool per trovare e gestire immagini duplicate con interfaccia moderna"
__license__ = "MIT"

# Version History
VERSIONS = {
    "2.3.0": {
        "date": "2025-06-25",
        "features": [
            "Fix completo sistema temi - tutti i box si colorano correttamente",
            "Conversione frame TTK → TK per controllo totale colori",
            "Struttura themed_widgets ottimizzata",
            "Pulizia e organizzazione progetto",
            "README unificato e professionale"
        ],
        "fixes": [
            "Risolto problema box grigio chiaro",
            "Frame contenitori ora seguono i temi",
            "Coerenza visiva totale in tutti i temi"
        ]
    },
    "2.2.0": {
        "date": "2025-06-24", 
        "features": [
            "Sistema temi multipli (Chiaro, Notturno, Neon, Pro)",
            "Pulsanti tema dinamici nell'header",
            "Aggiornamento colori in tempo reale"
        ]
    },
    "2.1.0": {
        "date": "2025-06-23",
        "features": [
            "Sistema cestino temporaneo",
            "Progress bar avanzata per confronto pixel",
            "Anteprime immagini integrate"
        ]
    },
    "2.0.0": {
        "date": "2025-06-22",
        "features": [
            "Interfaccia grafica moderna",
            "Web interface con Flask",
            "Gestione interattiva duplicati"
        ]
    }
}

# Current stable version
STABLE_VERSION = "2.3.0"

# Requirements
PYTHON_MIN_VERSION = "3.7"
DEPENDENCIES = [
    "Pillow>=10.0.0",
    "pillow-heif>=0.10.0", 
    "Flask>=2.3.0"
]
