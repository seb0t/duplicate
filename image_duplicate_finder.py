#!/usr/bin/env python3
"""
Image Duplicate Finder

Un programma Python che scansiona una cartella e tutte le sue sottocartelle
per trovare immagini duplicate utilizzando diversi metodi di confronto:
- Hash del contenuto del file (MD5 e SHA256)
- Confronto pixel per pixel delle immagini
- Controllo dei metadati (data di creazione, dimensioni)

Autore: Assistant
Data: 25 Giugno 2025
"""

import os
import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import argparse
from datetime import datetime

try:
    from PIL import Image, ExifTags
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("ATTENZIONE: Pillow non è installato. Solo hash del file sarà disponibile.")
    print("Installa con: pip install Pillow")

# Supporto per file HEIC
HEIC_AVAILABLE = False
try:
    import pillow_heif
    # Registra i plugin HEIF/HEIC con Pillow
    pillow_heif.register_heif_opener()
    HEIC_AVAILABLE = True
except ImportError:
    pass


class ImageDuplicateFinder:
    """Classe principale per trovare immagini duplicate."""
    
    # Estensioni immagine supportate
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heic', '.heif'}
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.image_paths: List[Path] = []
        self.file_hashes: Dict[str, List[Path]] = defaultdict(list)
        self.duplicates: Dict[str, List[Path]] = {}
        
    def log(self, message: str):
        """Stampa messaggi se modalità verbose è attiva."""
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def scan_directory(self, directory: Path) -> None:
        """Scansiona ricorsivamente una directory per trovare immagini."""
        self.log(f"Scansionando directory: {directory}")
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory non trovata: {directory}")
        
        if not directory.is_dir():
            raise NotADirectoryError(f"Il percorso non è una directory: {directory}")
        
        # Scansiona ricorsivamente tutte le immagini
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                self.image_paths.append(file_path)
                self.log(f"Trovata immagine: {file_path}")
        
        print(f"Trovate {len(self.image_paths)} immagini da analizzare.")
    
    def calculate_file_hash(self, file_path: Path, algorithm: str = 'md5') -> str:
        """Calcola l'hash del contenuto di un file."""
        hash_algo = hashlib.new(algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                # Leggi il file a blocchi per gestire file grandi
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_algo.update(chunk)
            return hash_algo.hexdigest()
        except Exception as e:
            self.log(f"Errore nel calcolo hash per {file_path}: {e}")
            return ""
    
    def get_image_metadata(self, file_path: Path) -> Dict:
        """Estrae metadati dall'immagine."""
        metadata = {
            'size': 0,
            'creation_time': None,
            'modification_time': None,
            'dimensions': None,
            'exif_date': None
        }
        
        try:
            # Informazioni del file
            stat = file_path.stat()
            metadata['size'] = stat.st_size
            metadata['creation_time'] = datetime.fromtimestamp(stat.st_ctime)
            metadata['modification_time'] = datetime.fromtimestamp(stat.st_mtime)
            
            # Informazioni dell'immagine se Pillow è disponibile
            if PIL_AVAILABLE:
                with Image.open(file_path) as img:
                    metadata['dimensions'] = img.size
                    
                    # Estrai data EXIF se disponibile
                    if hasattr(img, '_getexif') and img._getexif():
                        exif = img._getexif()
                        for tag_id, value in exif.items():
                            tag = ExifTags.TAGS.get(tag_id, tag_id)
                            if tag == 'DateTime':
                                try:
                                    metadata['exif_date'] = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                                except:
                                    pass
                                break
        except Exception as e:
            self.log(f"Errore nell'estrazione metadati per {file_path}: {e}")
        
        return metadata
    
    def compare_images_pixel_by_pixel(self, img1_path: Path, img2_path: Path) -> bool:
        """Confronta due immagini pixel per pixel."""
        if not PIL_AVAILABLE:
            return False
        
        try:
            with Image.open(img1_path) as img1, Image.open(img2_path) as img2:
                # Controllo dimensioni
                if img1.size != img2.size:
                    return False
                
                # Converti entrambe le immagini in RGB per confronto uniforme
                # Questo è importante per HEIC che potrebbe avere canali alpha
                img1_rgb = img1.convert('RGB')
                img2_rgb = img2.convert('RGB')
                
                # Per immagini grandi, confronta un campione di pixel per velocità
                width, height = img1.width, img1.height
                total_pixels = width * height
                
                # Se l'immagine è molto grande (> 1MP), campiona ogni N pixel
                if total_pixels > 1000000:
                    step = max(1, int((total_pixels / 1000000) ** 0.5))
                    for x in range(0, width, step):
                        for y in range(0, height, step):
                            if img1_rgb.getpixel((x, y)) != img2_rgb.getpixel((x, y)):
                                return False
                else:
                    # Confronto pixel per pixel completo per immagini piccole
                    for x in range(width):
                        for y in range(height):
                            if img1_rgb.getpixel((x, y)) != img2_rgb.getpixel((x, y)):
                                return False
                
                return True
        except Exception as e:
            self.log(f"Errore nel confronto pixel per {img1_path} e {img2_path}: {e}")
            return False
    
    def find_duplicates_by_hash(self) -> None:
        """Trova duplicati basandosi sull'hash del file."""
        print("Calcolando hash dei file...")
        
        for i, img_path in enumerate(self.image_paths):
            if i % 10 == 0:  # Progress indicator
                print(f"Progresso: {i}/{len(self.image_paths)}")
            
            # Calcola hash MD5
            file_hash = self.calculate_file_hash(img_path, 'md5')
            if file_hash:
                self.file_hashes[file_hash].append(img_path)
        
        # Identifica duplicati (hash con più di un file)
        for file_hash, paths in self.file_hashes.items():
            if len(paths) > 1:
                self.duplicates[file_hash] = paths
        
        print(f"Trovati {len(self.duplicates)} gruppi di duplicati basati su hash.")
    
    def verify_duplicates_with_pixel_comparison(self) -> None:
        """Verifica i duplicati con confronto pixel per pixel."""
        if not PIL_AVAILABLE:
            self.log("Pillow non disponibile, salto verifica pixel.")
            return
        
        print("Verificando duplicati con confronto pixel...")
        verified_duplicates = {}
        
        for file_hash, paths in self.duplicates.items():
            if len(paths) < 2:
                continue
            
            # Confronta ogni coppia nel gruppo
            verified_group = []
            for i, path1 in enumerate(paths):
                is_duplicate = False
                for j, path2 in enumerate(paths):
                    if i != j and self.compare_images_pixel_by_pixel(path1, path2):
                        is_duplicate = True
                        break
                
                if is_duplicate and path1 not in verified_group:
                    verified_group.append(path1)
            
            if len(verified_group) > 1:
                verified_duplicates[file_hash] = verified_group
        
        self.duplicates = verified_duplicates
        print(f"Verificati {len(self.duplicates)} gruppi di duplicati reali.")
    
    def print_results(self) -> None:
        """Stampa i risultati della ricerca duplicati."""
        if not self.duplicates:
            print("\n🎉 Nessun duplicato trovato!")
            return
        
        print(f"\n📋 RISULTATI - Trovati {len(self.duplicates)} gruppi di immagini duplicate:")
        print("=" * 80)
        
        total_duplicates = 0
        total_wasted_space = 0
        
        for i, (file_hash, paths) in enumerate(self.duplicates.items(), 1):
            print(f"\n🔍 Gruppo {i} ({len(paths)} immagini duplicate):")
            print(f"   Hash: {file_hash}")
            
            # Calcola spazio sprecato (mantieni solo la prima, elimina le altre)
            if paths:
                first_file_size = paths[0].stat().st_size
                wasted_space = first_file_size * (len(paths) - 1)
                total_wasted_space += wasted_space
                
                print(f"   Dimensione file: {first_file_size:,} bytes")
                print(f"   Spazio sprecato: {wasted_space:,} bytes")
            
            total_duplicates += len(paths) - 1  # -1 perché uno lo teniamo
            
            for j, path in enumerate(paths):
                metadata = self.get_image_metadata(path)
                print(f"   {j+1}. {path}")
                if metadata['creation_time']:
                    print(f"      📅 Creato: {metadata['creation_time']}")
                if metadata['dimensions']:
                    print(f"      📐 Dimensioni: {metadata['dimensions']}")
        
        print("\n" + "=" * 80)
        print(f"📊 RIEPILOGO:")
        print(f"   • Immagini totali analizzate: {len(self.image_paths)}")
        print(f"   • Gruppi di duplicati: {len(self.duplicates)}")
        print(f"   • Immagini duplicate da rimuovere: {total_duplicates}")
        print(f"   • Spazio totale recuperabile: {total_wasted_space:,} bytes ({total_wasted_space/1024/1024:.2f} MB)")
        
    def save_results_to_file(self, output_file: Path) -> None:
        """Salva i risultati in un file di testo."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("REPORT IMMAGINI DUPLICATE\n")
            f.write("=" * 50 + "\n")
            f.write(f"Data analisi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Immagini analizzate: {len(self.image_paths)}\n")
            f.write(f"Gruppi duplicati trovati: {len(self.duplicates)}\n\n")
            
            for i, (file_hash, paths) in enumerate(self.duplicates.items(), 1):
                f.write(f"Gruppo {i} - Hash: {file_hash}\n")
                for path in paths:
                    f.write(f"  - {path}\n")
                f.write("\n")
        
        print(f"📄 Risultati salvati in: {output_file}")


def main():
    """Funzione principale del programma."""
    parser = argparse.ArgumentParser(
        description='Trova immagini duplicate in una cartella e sottocartelle',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi d'uso:
  python image_duplicate_finder.py C:\\MieImmagini
  python image_duplicate_finder.py C:\\MieImmagini --verbose
  python image_duplicate_finder.py C:\\MieImmagini --output report.txt
  python image_duplicate_finder.py C:\\MieImmagini --no-pixel-verify
        """
    )
    
    parser.add_argument(
        'directory',
        type=str,
        help='Percorso della cartella da scansionare'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Abilita output dettagliato'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='File di output per salvare i risultati'
    )
    
    parser.add_argument(
        '--no-pixel-verify',
        action='store_true',
        help='Salta la verifica pixel per pixel (più veloce ma meno preciso)'
    )
    
    args = parser.parse_args()
    
    # Verifica che la directory esista
    directory = Path(args.directory)
    if not directory.exists():
        print(f"❌ Errore: Directory non trovata: {directory}")
        sys.exit(1)
    
    print("🔍 IMAGE DUPLICATE FINDER")
    print("=" * 40)
    print(f"📁 Directory da scansionare: {directory}")
    print(f"🔧 Verifica pixel per pixel: {'No' if args.no_pixel_verify else 'Sì'}")
    if not PIL_AVAILABLE:
        print("⚠️  ATTENZIONE: Pillow non installato - funzionalità limitate")
    if HEIC_AVAILABLE:
        print("✅ Supporto HEIC/HEIF attivo")
    else:
        print("ℹ️  Supporto HEIC/HEIF non disponibile (installa pillow-heif)")
    print()
    
    try:
        # Inizializza il finder
        finder = ImageDuplicateFinder(verbose=args.verbose)
        
        # Scansiona directory
        finder.scan_directory(directory)
        
        if not finder.image_paths:
            print("❌ Nessuna immagine trovata nella directory specificata.")
            sys.exit(0)
        
        # Trova duplicati tramite hash
        finder.find_duplicates_by_hash()
        
        # Verifica con confronto pixel se richiesto
        if not args.no_pixel_verify and PIL_AVAILABLE:
            finder.verify_duplicates_with_pixel_comparison()
        
        # Mostra risultati
        finder.print_results()
        
        # Salva risultati se richiesto
        if args.output:
            output_path = Path(args.output)
            finder.save_results_to_file(output_path)
    
    except KeyboardInterrupt:
        print("\n❌ Operazione annullata dall'utente.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Errore durante l'esecuzione: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
