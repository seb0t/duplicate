#!/usr/bin/env python3
"""
Image Duplicate Finder - Web Interface

Interfaccia web per il programma di ricerca duplicati immagini.
Utilizza Flask per fornire un'interfaccia utente semplice e intuitiva.
"""

import os
import json
import shutil
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import threading
import uuid
from datetime import datetime

# Importa la classe principale
from image_duplicate_finder import ImageDuplicateFinder

app = Flask(__name__)
app.secret_key = 'duplicate_finder_secret_key'

# Directory per risultati temporanei
RESULTS_DIR = Path('web_results')
RESULTS_DIR.mkdir(exist_ok=True)

# Directory per cestino temporaneo
GARBAGE_DIR = Path('web_garbage_duplicates')
GARBAGE_DIR.mkdir(exist_ok=True)

# Storage per i task in corso
active_tasks = {}

class WebDuplicateFinder:
    """Wrapper per l'interfaccia web."""
    
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.finder = ImageDuplicateFinder(verbose=True)
        self.status = "Inizializzazione..."
        self.progress = 0
        self.results = None
        self.error = None
        
    def run_analysis(self, directory_path: str, pixel_verify: bool = True):
        """Esegue l'analisi in background."""
        try:
            self.status = "Scansionando directory..."
            self.progress = 10
            
            directory = Path(directory_path)
            self.finder.scan_directory(directory)
            
            if not self.finder.image_paths:
                self.error = "Nessuna immagine trovata nella directory"
                return
            
            self.status = f"Calcolando hash per {len(self.finder.image_paths)} immagini..."
            self.progress = 30
            
            self.finder.find_duplicates_by_hash()
            self.progress = 70
            
            if pixel_verify:
                self.status = "Verificando con confronto pixel..."
                self.finder.verify_duplicates_with_pixel_comparison()
            
            self.progress = 100
            self.status = "Completato"
            
            # Prepara risultati per JSON
            self.results = self._prepare_results()
            
        except Exception as e:
            self.error = str(e)
            self.status = "Errore"
    
    def _prepare_results(self):
        """Prepara i risultati per la visualizzazione web."""
        if not self.finder.duplicates:
            return {"groups": [], "summary": {"total_images": len(self.finder.image_paths), "duplicate_groups": 0, "duplicates_to_remove": 0, "space_saved": 0}}
        
        groups = []
        total_duplicates = 0
        total_space_saved = 0
        
        for i, (file_hash, paths) in enumerate(self.finder.duplicates.items(), 1):
            if paths:
                file_size = paths[0].stat().st_size
                space_saved = file_size * (len(paths) - 1)
                total_space_saved += space_saved
                total_duplicates += len(paths) - 1
                
                # Trova il file "originale" (quello nella directory principale o con nome più semplice)
                original_idx = 0
                for idx, path in enumerate(paths):
                    # Preferisci file con percorso più corto (directory principale)
                    if len(str(path.parent)) < len(str(paths[original_idx].parent)):
                        original_idx = idx
                    # O quello con il nome più semplice
                    elif len(str(path.name)) < len(str(paths[original_idx].name)):
                        original_idx = idx
                
                # Riordina: originale per primo
                if original_idx != 0:
                    paths[0], paths[original_idx] = paths[original_idx], paths[0]
                
                group_data = {
                    "id": i,
                    "hash": file_hash,
                    "count": len(paths),
                    "file_size": file_size,
                    "space_saved": space_saved,
                    "files": []
                }
                
                for j, path in enumerate(paths):
                    metadata = self.finder.get_image_metadata(path)
                    
                    # Determina il tipo (originale o duplicato)
                    file_type = "original" if j == 0 else "duplicate"
                    
                    # Calcola cartella relativa
                    try:
                        folder = str(path.parent.relative_to(path.parents[len(path.parents)-2]))
                        if folder == ".":
                            folder = "Directory principale"
                    except:
                        folder = str(path.parent)
                    
                    group_data["files"].append({
                        "path": str(path),
                        "filename": path.name,
                        "folder": folder,
                        "type": file_type,
                        "size": metadata["size"],
                        "created": metadata["creation_time"].strftime("%Y-%m-%d %H:%M:%S") if metadata["creation_time"] else "N/A",
                        "dimensions": f"{metadata['dimensions'][0]}x{metadata['dimensions'][1]}" if metadata["dimensions"] else "N/A"
                    })
                
                groups.append(group_data)
        
        return {
            "groups": groups,
            "summary": {
                "total_images": len(self.finder.image_paths),
                "duplicate_groups": len(self.finder.duplicates),
                "duplicates_to_remove": total_duplicates,
                "space_saved": total_space_saved
            }
        }

@app.route('/')
def index():
    """Pagina principale."""
    return render_template('index.html')

@app.route('/start_analysis', methods=['POST'])
def start_analysis():
    """Avvia l'analisi in background."""
    data = request.get_json()
    directory = data.get('directory', '')
    pixel_verify = data.get('pixel_verify', True)
    
    if not directory or not Path(directory).exists():
        return jsonify({"error": "Directory non valida o inesistente"}), 400
    
    # Crea nuovo task
    task_id = str(uuid.uuid4())
    web_finder = WebDuplicateFinder(task_id)
    active_tasks[task_id] = web_finder
    
    # Avvia analisi in background
    thread = threading.Thread(target=web_finder.run_analysis, args=(directory, pixel_verify))
    thread.daemon = True
    thread.start()
    
    return jsonify({"task_id": task_id})

@app.route('/status/<task_id>')
def get_status(task_id):
    """Ottiene lo status di un task."""
    if task_id not in active_tasks:
        return jsonify({"error": "Task non trovato"}), 404
    
    task = active_tasks[task_id]
    response = {
        "status": task.status,
        "progress": task.progress,
        "error": task.error,
        "results": task.results
    }
    
    return jsonify(response)

@app.route('/download_report/<task_id>')
def download_report(task_id):
    """Scarica il report dei risultati."""
    if task_id not in active_tasks:
        return jsonify({"error": "Task non trovato"}), 404
    
    task = active_tasks[task_id]
    if not task.results:
        return jsonify({"error": "Nessun risultato disponibile"}), 400
    
    # Crea file report
    report_path = RESULTS_DIR / f"report_{task_id}.txt"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("REPORT IMMAGINI DUPLICATE - WEB INTERFACE\n")
        f.write("=" * 50 + "\n")
        f.write(f"Data analisi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Immagini analizzate: {task.results['summary']['total_images']}\n")
        f.write(f"Gruppi duplicati: {task.results['summary']['duplicate_groups']}\n\n")
        
        for group in task.results['groups']:
            f.write(f"Gruppo {group['id']} - Hash: {group['hash']}\n")
            f.write(f"Dimensione file: {group['file_size']:,} bytes\n")
            f.write(f"Spazio recuperabile: {group['space_saved']:,} bytes\n")
            for file_info in group['files']:
                f.write(f"  - {file_info['path']}\n")
                f.write(f"    Creato: {file_info['created']}, Dimensioni: {file_info['dimensions']}\n")
            f.write("\n")
    
    return send_from_directory(RESULTS_DIR, f"report_{task_id}.txt", as_attachment=True)

@app.route('/browse_directories', methods=['POST'])
def browse_directories():
    """API per esplorare le directory del sistema."""
    data = request.get_json()
    current_path = data.get('path', '')
    
    # Se nessun path specificato, mostra i drive del sistema (Windows) o root (Unix)
    if not current_path:
        import platform
        if platform.system() == 'Windows':
            import string
            drives = []
            for letter in string.ascii_uppercase:
                drive_path = f"{letter}:\\"
                if Path(drive_path).exists():
                    drives.append({
                        'name': f"Drive {letter}:",
                        'path': drive_path,
                        'type': 'drive'
                    })
            return jsonify({'items': drives, 'current_path': ''})
        else:
            current_path = '/'
    
    try:
        path_obj = Path(current_path)
        if not path_obj.exists() or not path_obj.is_dir():
            return jsonify({'error': 'Directory non valida'}), 400
        
        items = []
        
        # Aggiungi cartella parent se non siamo alla radice
        if path_obj.parent != path_obj:
            items.append({
                'name': '.. (cartella superiore)',
                'path': str(path_obj.parent),
                'type': 'parent'
            })
        
        # Aggiungi tutte le sottodirectory
        try:
            for item in sorted(path_obj.iterdir()):
                if item.is_dir():
                    items.append({
                        'name': item.name,
                        'path': str(item),
                        'type': 'folder'
                    })
        except PermissionError:
            return jsonify({'error': 'Accesso negato alla directory'}), 403
        
        return jsonify({
            'items': items,
            'current_path': str(path_obj)
        })
        
    except Exception as e:
        return jsonify({'error': f'Errore durante la navigazione: {str(e)}'}), 500

@app.route('/delete_files', methods=['POST'])
def delete_files():
    """API per spostare file nel cestino temporaneo."""
    data = request.get_json()
    task_id = data.get('task_id')
    file_paths = data.get('file_paths', [])
    
    if not task_id or task_id not in active_tasks:
        return jsonify({'error': 'Task non trovato'}), 404
    
    if not file_paths:
        return jsonify({'error': 'Nessun file specificato'}), 400
    
    try:
        moved_files = []
        total_size = 0
        
        # Crea cartella specifica per questo task
        task_garbage_dir = GARBAGE_DIR / task_id
        task_garbage_dir.mkdir(exist_ok=True)
        
        for file_path in file_paths:
            source_path = Path(file_path)
            if not source_path.exists():
                continue
            
            # Calcola dimensione
            file_size = source_path.stat().st_size
            total_size += file_size
            
            # Crea struttura directory nel cestino mantenendo il percorso relativo
            relative_path = source_path.name  # Per semplicità, solo il nome file
            counter = 1
            dest_name = relative_path
            
            # Gestisci conflitti di nome
            while (task_garbage_dir / dest_name).exists():
                name_parts = relative_path.rsplit('.', 1)
                if len(name_parts) == 2:
                    dest_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                else:
                    dest_name = f"{relative_path}_{counter}"
                counter += 1
            
            dest_path = task_garbage_dir / dest_name
            
            # Sposta il file
            shutil.move(str(source_path), str(dest_path))
            moved_files.append({
                'original_path': str(source_path),
                'garbage_path': str(dest_path),
                'size': file_size
            })
        
        return jsonify({
            'success': True,
            'moved_files': len(moved_files),
            'total_size': total_size,
            'garbage_folder': str(task_garbage_dir),
            'files': moved_files
        })
        
    except Exception as e:
        return jsonify({'error': f'Errore durante lo spostamento dei file: {str(e)}'}), 500

@app.route('/manage_garbage/<task_id>')
def manage_garbage(task_id):
    """API per gestire il cestino temporaneo."""
    if task_id not in active_tasks:
        return jsonify({'error': 'Task non trovato'}), 404
    
    task_garbage_dir = GARBAGE_DIR / task_id
    
    if not task_garbage_dir.exists():
        return jsonify({
            'exists': False,
            'files': [],
            'total_size': 0
        })
    
    try:
        files = []
        total_size = 0
        
        for file_path in task_garbage_dir.iterdir():
            if file_path.is_file():
                file_size = file_path.stat().st_size
                total_size += file_size
                files.append({
                    'name': file_path.name,
                    'path': str(file_path),
                    'size': file_size,
                    'modified': file_path.stat().st_mtime
                })
        
        return jsonify({
            'exists': True,
            'folder_path': str(task_garbage_dir),
            'files': files,
            'total_size': total_size,
            'file_count': len(files)
        })
        
    except Exception as e:
        return jsonify({'error': f'Errore durante la lettura del cestino: {str(e)}'}), 500

@app.route('/empty_garbage/<task_id>', methods=['POST'])
def empty_garbage(task_id):
    """API per svuotare definitivamente il cestino."""
    if task_id not in active_tasks:
        return jsonify({'error': 'Task non trovato'}), 404
    
    task_garbage_dir = GARBAGE_DIR / task_id
    
    if not task_garbage_dir.exists():
        return jsonify({'success': True, 'message': 'Cestino già vuoto'})
    
    try:
        # Conta file e dimensione totale prima dell'eliminazione
        file_count = 0
        total_size = 0
        
        for file_path in task_garbage_dir.iterdir():
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1
        
        # Elimina definitivamente la cartella e tutto il contenuto
        shutil.rmtree(task_garbage_dir)
        
        return jsonify({
            'success': True,
            'deleted_files': file_count,
            'freed_space': total_size,
            'message': f'Eliminati definitivamente {file_count} file ({total_size / (1024*1024):.1f} MB)'
        })
        
    except Exception as e:
        return jsonify({'error': f'Errore durante lo svuotamento del cestino: {str(e)}'}), 500

if __name__ == '__main__':
    print("🌐 Avvio Image Duplicate Finder - Web Interface")
    print("=" * 50)
    print("📍 URL: http://localhost:5000")
    print("📍 URL alternativo: http://127.0.0.1:5000")
    print("🔄 Premi Ctrl+C per fermare il server")
    print("=" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server fermato dall'utente")
    except Exception as e:
        print(f"\n❌ Errore durante l'avvio del server: {e}")
        input("Premi Invio per chiudere...")
