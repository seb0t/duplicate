#!/usr/bin/env python3
"""
Image Duplicate Finder - GUI Desktop

Interfaccia grafica desktop utilizzando tkinter per il programma di ricerca duplicati.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import queue
from datetime import datetime
import os
import shutil
from PIL import Image, ImageTk
import io

# Importa la classe principale
from image_duplicate_finder import ImageDuplicateFinder

class DuplicateFinderGUI:
    """Interfaccia grafica per Image Duplicate Finder."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Image Duplicate Finder")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Variabili
        self.directory_var = tk.StringVar()
        self.pixel_verify_var = tk.BooleanVar(value=True)
        self.verbose_var = tk.BooleanVar(value=False)
        
        # Tema corrente
        self.current_theme = "Pro"
        self.themes = {
            "Chiaro": {
                "bg": "#F5F5F5",
                "fg": "#333333",
                "primary": "#2E7D32",
                "secondary": "#1976D2",
                "success": "#4CAF50",
                "warning": "#FF9800",
                "danger": "#F44336",
                "frame_bg": "#FFFFFF",
                "frame_border": "#E0E0E0",
                "text_bg": "#FAFAFA",
                "button_bg": "#E3F2FD",
                "accent": "#81C784"
            },
            "Notturno": {
                "bg": "#1E1E1E",
                "fg": "#E0E0E0",
                "primary": "#66BB6A",
                "secondary": "#42A5F5",
                "success": "#66BB6A",
                "warning": "#FFB74D",
                "danger": "#EF5350",
                "frame_bg": "#2D2D2D",
                "frame_border": "#404040",
                "text_bg": "#1A1A1A",
                "button_bg": "#383838",
                "accent": "#81C784"
            },
            "Neon": {
                "bg": "#0A0A0A",
                "fg": "#00FF41",
                "primary": "#00FF41",
                "secondary": "#FF0080",
                "success": "#00FF41",
                "warning": "#FFFF00",
                "danger": "#FF0040",
                "frame_bg": "#1A1A1A",
                "frame_border": "#00FF41",
                "text_bg": "#000000",
                "button_bg": "#001122",
                "accent": "#FF0080"
            },
            "Pro": {
                "bg": "#263238",
                "fg": "#ECEFF1",
                "primary": "#00BCD4",
                "secondary": "#FF9800",
                "success": "#4CAF50",
                "warning": "#FFC107",
                "danger": "#F44336",
                "frame_bg": "#37474F",
                "frame_border": "#546E7A",
                "text_bg": "#1C2833",
                "button_bg": "#455A64",
                "accent": "#26C6DA"
            }
        }
        
        # Queue per comunicazione tra thread
        self.progress_queue = queue.Queue()
        self.results_queue = queue.Queue()
        
        # Riferimenti
        self.finder = None
        self.analysis_thread = None
        self.is_running = False
        
        # Variabili per controllo eliminazione
        self.duplicate_groups = []
        self.group_checkboxes = {}  # {group_id: {file_path: checkbox_var}}
        self.group_select_all_vars = {}  # {group_id: select_all_var}
        self.garbage_folder = None  # Cartella cestino temporaneo
        
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Avvia check periodico delle queue
        self.check_queues()
    
    def setup_ui(self):
        """Configura l'interfaccia utente."""
        # Style personalizzato
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurazione colori personalizzati
        style.configure('Title.TLabel', 
                       foreground='#2E7D32',
                       font=('Arial', 20, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       foreground='#555555',
                       font=('Arial', 11))
        
        style.configure('Success.TButton',
                       background='#4CAF50',
                       foreground='white',
                       font=('Arial', 10, 'bold'))
        
        style.configure('Danger.TButton',
                       background='#F44336',
                       foreground='white',
                       font=('Arial', 10, 'bold'))
        
        style.configure('Warning.TButton',
                       background='#FF9800',
                       foreground='white',
                       font=('Arial', 10, 'bold'))
        
        # Configura colori per progress bar
        style.configure('Custom.Horizontal.TProgressbar',
                       background='#4CAF50',
                       troughcolor='#E0E0E0')
        
        # Paned Window principale (layout orizzontale)
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame sinistro - Controlli principali
        self.left_frame = tk.Frame(main_paned, bg=self.themes[self.current_theme]["bg"])
        main_paned.add(self.left_frame, weight=2)
        
        # Frame destro - Controlli eliminazione
        self.right_frame = tk.Frame(main_paned, bg=self.themes[self.current_theme]["bg"])
        main_paned.add(self.right_frame, weight=1)
        
        # === FRAME SINISTRO - CONTROLLI PRINCIPALI ===
        
        # Header con titolo e pulsanti tema
        header_frame = tk.Frame(self.left_frame, bg=self.themes[self.current_theme]["bg"])
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10), padx=10)
        header_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(header_frame, text="🔍 Image Duplicate Finder", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky="w")
        
        # Pulsanti tema
        theme_frame = tk.Frame(header_frame, bg=self.themes[self.current_theme]["bg"])
        theme_frame.grid(row=0, column=1, sticky="e")
        
        theme_label = ttk.Label(theme_frame, text="Tema:", font=("Arial", 9))
        theme_label.grid(row=0, column=0, padx=(0, 5))
        
        # Pulsanti per ogni tema
        self.theme_buttons = {}
        for i, theme_name in enumerate(self.themes.keys()):
            btn = tk.Button(theme_frame, 
                           text=theme_name,
                           font=("Arial", 8, "bold"),
                           relief="raised",
                           bd=2,
                           padx=8,
                           pady=2,
                           command=lambda t=theme_name: self.apply_theme(t))
            btn.grid(row=0, column=i+1, padx=2)
            self.theme_buttons[theme_name] = btn
        
        # Results text area con frame personalizzato
        results_outer_frame = tk.Frame(self.left_frame, bg=self.themes[self.current_theme]["bg"])
        results_outer_frame.grid(row=7, column=0, sticky="nsew", pady=(0, 10), padx=10)
        results_outer_frame.rowconfigure(1, weight=1)
        results_outer_frame.columnconfigure(0, weight=1)
        self.left_frame.rowconfigure(7, weight=1)
        
        results_label = tk.Label(results_outer_frame, 
                                text="📄 Risultati Dettagliati",
                                bg=self.themes[self.current_theme]["bg"],
                                fg=self.themes[self.current_theme]["primary"],
                                font=('Arial', 10, 'bold'))
        results_label.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
        
        results_frame = tk.Frame(results_outer_frame, 
                                bg=self.themes[self.current_theme]["frame_bg"],
                                relief='solid',
                                bd=2,
                                highlightbackground=self.themes[self.current_theme]["frame_border"],
                                highlightthickness=1)
        results_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, 
                                                     height=15, 
                                                     wrap=tk.WORD,
                                                     font=("Consolas", 9),
                                                     bg=self.themes[self.current_theme]["text_bg"],
                                                     fg=self.themes[self.current_theme]["fg"],
                                                     relief='flat',
                                                     bd=0)
        self.results_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        subtitle_label = ttk.Label(self.left_frame, 
                                 text="Trova e gestisci immagini duplicate con controlli avanzati",
                                 style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, pady=(0, 20), sticky="w", padx=10)
        
        # Directory selection con frame personalizzato
        dir_outer_frame = tk.Frame(self.left_frame, bg=self.themes[self.current_theme]["bg"])
        dir_outer_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15), padx=10)
        self.left_frame.columnconfigure(0, weight=1)
        dir_outer_frame.columnconfigure(0, weight=1)
        
        dir_label = tk.Label(dir_outer_frame,
                            text="📁 Selezione Directory",
                            bg=self.themes[self.current_theme]["bg"],
                            fg=self.themes[self.current_theme]["primary"],
                            font=('Arial', 10, 'bold'))
        dir_label.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
        
        dir_frame = tk.Frame(dir_outer_frame,
                            bg=self.themes[self.current_theme]["frame_bg"],
                            relief='solid',
                            bd=2,
                            highlightbackground=self.themes[self.current_theme]["frame_border"],
                            highlightthickness=1)
        dir_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        dir_frame.columnconfigure(0, weight=1)
        
        dir_entry_frame = tk.Frame(dir_frame, bg=self.themes[self.current_theme]["frame_bg"])
        dir_entry_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        dir_entry_frame.columnconfigure(0, weight=1)
        
        self.dir_entry = tk.Entry(dir_entry_frame, 
                                 textvariable=self.directory_var,
                                 font=("Arial", 10),
                                 bg=self.themes[self.current_theme]["text_bg"],
                                 fg=self.themes[self.current_theme]["fg"],
                                 relief='solid',
                                 bd=1,
                                 highlightbackground=self.themes[self.current_theme]["frame_border"])
        self.dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        browse_btn = tk.Button(dir_entry_frame, 
                              text="📂 Sfoglia", 
                              command=self.browse_directory,
                              bg=self.themes[self.current_theme]["button_bg"],
                              fg=self.themes[self.current_theme]["fg"],
                              font=('Arial', 9, 'bold'),
                              relief='solid',
                              bd=1,
                              activebackground=self.themes[self.current_theme]["accent"])
        browse_btn.grid(row=0, column=1)
        
        # Options con frame personalizzato
        options_outer_frame = tk.Frame(self.left_frame, bg=self.themes[self.current_theme]["bg"])
        options_outer_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15), padx=10)
        
        options_label = tk.Label(options_outer_frame,
                                text="⚙️ Opzioni di Scansione",
                                bg=self.themes[self.current_theme]["bg"],
                                fg=self.themes[self.current_theme]["primary"],
                                font=('Arial', 10, 'bold'))
        options_label.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
        
        options_frame = tk.Frame(options_outer_frame,
                                bg=self.themes[self.current_theme]["frame_bg"],
                                relief='solid',
                                bd=2,
                                highlightbackground=self.themes[self.current_theme]["frame_border"],
                                highlightthickness=1)
        options_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        pixel_check = tk.Checkbutton(options_frame, 
                                    text="🔬 Verifica pixel per pixel (più preciso ma più lento)",
                                    variable=self.pixel_verify_var,
                                    bg=self.themes[self.current_theme]["frame_bg"],
                                    fg=self.themes[self.current_theme]["fg"],
                                    selectcolor=self.themes[self.current_theme]["accent"],
                                    activebackground=self.themes[self.current_theme]["button_bg"],
                                    relief='flat')
        pixel_check.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 8))
        
        verbose_check = tk.Checkbutton(options_frame,
                                      text="📝 Output dettagliato (verbose)",
                                      variable=self.verbose_var,
                                      bg=self.themes[self.current_theme]["frame_bg"],
                                      fg=self.themes[self.current_theme]["fg"],
                                      selectcolor=self.themes[self.current_theme]["accent"],
                                      activebackground=self.themes[self.current_theme]["button_bg"],
                                      relief='flat')
        verbose_check.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 15))
        
        # Control buttons
        button_frame = tk.Frame(self.left_frame, bg=self.themes[self.current_theme]["bg"])
        button_frame.grid(row=4, column=0, pady=(0, 15), padx=10)
        
        self.start_btn = ttk.Button(button_frame, text="🚀 Avvia Ricerca", 
                                   command=self.start_analysis,
                                   style="Success.TButton")
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Interrompi", 
                                  command=self.stop_analysis, 
                                  style="Warning.TButton",
                                  state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.save_btn = ttk.Button(button_frame, text="💾 Salva Report", 
                                  command=self.save_report,
                                  state="disabled")
        self.save_btn.grid(row=0, column=2)
        
        # Progress con frame personalizzato
        progress_outer_frame = tk.Frame(self.left_frame, bg=self.themes[self.current_theme]["bg"])
        progress_outer_frame.grid(row=5, column=0, sticky="ew", pady=(0, 15), padx=10)
        progress_outer_frame.columnconfigure(0, weight=1)
        
        progress_label = tk.Label(progress_outer_frame,
                                 text="📊 Progresso",
                                 bg=self.themes[self.current_theme]["bg"],
                                 fg=self.themes[self.current_theme]["primary"],
                                 font=('Arial', 10, 'bold'))
        progress_label.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
        
        progress_frame = tk.Frame(progress_outer_frame,
                                 bg=self.themes[self.current_theme]["frame_bg"],
                                 relief='solid',
                                 bd=2,
                                 highlightbackground=self.themes[self.current_theme]["frame_border"],
                                 highlightthickness=1)
        progress_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        progress_frame.columnconfigure(0, weight=1)
        
        self.status_label = tk.Label(progress_frame, 
                                    text="Pronto per iniziare",
                                    bg=self.themes[self.current_theme]["frame_bg"],
                                    fg=self.themes[self.current_theme]["success"],
                                    font=('Arial', 9))
        self.status_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           maximum=100, mode='determinate',
                                           style='Custom.Horizontal.TProgressbar')
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=15, pady=(5, 15))
        
        # Results summary con frame personalizzato
        summary_outer_frame = tk.Frame(self.left_frame, bg=self.themes[self.current_theme]["bg"])
        summary_outer_frame.grid(row=6, column=0, sticky="ew", pady=(0, 10), padx=10)
        
        summary_label_title = tk.Label(summary_outer_frame,
                                      text="📋 Riepilogo Risultati",
                                      bg=self.themes[self.current_theme]["bg"],
                                      fg=self.themes[self.current_theme]["primary"],
                                      font=('Arial', 10, 'bold'))
        summary_label_title.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
        
        summary_frame = tk.Frame(summary_outer_frame,
                                bg=self.themes[self.current_theme]["frame_bg"],
                                relief='solid',
                                bd=2,
                                highlightbackground=self.themes[self.current_theme]["frame_border"],
                                highlightthickness=1)
        summary_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        self.summary_label = tk.Label(summary_frame, 
                                     text="",
                                     font=("Arial", 10, "bold"),
                                     bg=self.themes[self.current_theme]["frame_bg"],
                                     fg=self.themes[self.current_theme]["secondary"],
                                     wraplength=500,
                                     justify='left')
        self.summary_label.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        # === FRAME DESTRO - CONTROLLI ELIMINAZIONE ===
        
        # Titolo controlli
        control_title = ttk.Label(self.right_frame, text="🗑️ Controlli Eliminazione", 
                                 style='Title.TLabel')
        control_title.grid(row=0, column=0, pady=(0, 15), sticky="w", padx=10)
        
        # Scrollable frame per i controlli dei duplicati
        self.controls_canvas = tk.Canvas(self.right_frame, bg=self.themes[self.current_theme]["bg"], 
                                        highlightthickness=0)
        controls_scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", 
                                         command=self.controls_canvas.yview)
        self.scrollable_controls = tk.Frame(self.controls_canvas, 
                                          bg=self.themes[self.current_theme]["bg"])
        
        self.scrollable_controls.bind(
            "<Configure>",
            lambda e: self.controls_canvas.configure(scrollregion=self.controls_canvas.bbox("all"))
        )
        
        self.controls_canvas.create_window((0, 0), window=self.scrollable_controls, anchor="nw")
        self.controls_canvas.configure(yscrollcommand=controls_scrollbar.set)
        
        self.controls_canvas.grid(row=1, column=0, sticky="nsew", pady=(0, 15), padx=10)
        controls_scrollbar.grid(row=1, column=1, sticky="ns")
        
        self.right_frame.rowconfigure(1, weight=1)
        self.right_frame.columnconfigure(0, weight=1)
        
        # Pulsanti azione globale con frame personalizzato
        global_actions_outer = tk.Frame(self.right_frame, bg=self.themes[self.current_theme]["bg"])
        global_actions_outer.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10), padx=10)
        
        global_actions_label = tk.Label(global_actions_outer,
                                       text="🎯 Azioni Globali",
                                       bg=self.themes[self.current_theme]["bg"],
                                       fg=self.themes[self.current_theme]["primary"],
                                       font=('Arial', 10, 'bold'))
        global_actions_label.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
        
        global_actions_frame = tk.Frame(global_actions_outer,
                                       bg=self.themes[self.current_theme]["frame_bg"],
                                       relief='solid',
                                       bd=2,
                                       highlightbackground=self.themes[self.current_theme]["frame_border"],
                                       highlightthickness=1)
        global_actions_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        self.delete_selected_btn = tk.Button(global_actions_frame, 
                                           text="🗑️ Sposta File Selezionati nel Cestino", 
                                           command=self.delete_selected_files,
                                           bg=self.themes[self.current_theme]["warning"],
                                           fg="white",
                                           font=('Arial', 9, 'bold'),
                                           relief='flat',
                                           state="disabled",
                                           activebackground=self.themes[self.current_theme]["danger"])
        self.delete_selected_btn.pack(fill="x", padx=15, pady=(15, 5))
        
        self.auto_select_btn = tk.Button(global_actions_frame, 
                                        text="⚡ Selezione Automatica Duplicati", 
                                        command=self.auto_select_duplicates,
                                        bg=self.themes[self.current_theme]["button_bg"],
                                        fg=self.themes[self.current_theme]["fg"],
                                        font=('Arial', 9, 'bold'),
                                        relief='flat',
                                        state="disabled",
                                        activebackground=self.themes[self.current_theme]["accent"])
        self.auto_select_btn.pack(fill="x", padx=15, pady=5)
        
        # Pulsante per gestire cartella garbage
        self.manage_garbage_btn = tk.Button(global_actions_frame, 
                                          text="🗂️ Gestisci Cestino", 
                                          command=self.manage_garbage_folder,
                                          bg=self.themes[self.current_theme]["button_bg"],
                                          fg=self.themes[self.current_theme]["fg"],
                                          font=('Arial', 9, 'bold'),
                                          relief='flat',
                                          state="disabled",
                                          activebackground=self.themes[self.current_theme]["accent"])
        self.manage_garbage_btn.pack(fill="x", padx=15, pady=(5, 15))
        
        # Info panel con frame personalizzato
        info_outer_frame = tk.Frame(self.right_frame, bg=self.themes[self.current_theme]["bg"])
        info_outer_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10)
        
        info_label = tk.Label(info_outer_frame,
                             text="ℹ️ Informazioni",
                             bg=self.themes[self.current_theme]["bg"],
                             fg=self.themes[self.current_theme]["primary"],
                             font=('Arial', 10, 'bold'))
        info_label.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
        
        info_frame = tk.Frame(info_outer_frame,
                             bg=self.themes[self.current_theme]["frame_bg"],
                             relief='solid',
                             bd=2,
                             highlightbackground=self.themes[self.current_theme]["frame_border"],
                             highlightthickness=1)
        info_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        info_text = tk.Text(info_frame, 
                           height=4, 
                           wrap=tk.WORD, 
                           bg=self.themes[self.current_theme]["text_bg"], 
                           fg=self.themes[self.current_theme]["fg"],
                           font=('Arial', 9), 
                           relief='flat',
                           bd=0)
        info_text.insert('1.0', 
                        "💡 SUGGERIMENTI:\n"
                        "• Usa 'Selezione Automatica' per selezionare tutti i duplicati\n"
                        "• I file vengono spostati in un cestino temporaneo (sicuro)\n"
                        "• Usa 'Gestisci Cestino' per eliminazione definitiva o ripristino\n"
                        "• Mantieni sempre almeno un file per gruppo")
        info_text.config(state='disabled')
        info_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            self.controls_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.controls_canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Salva riferimenti ai widget per l'aggiornamento temi
        self.themed_widgets = {
            'main_frames': [self.left_frame, self.right_frame],
            'container_frames': [header_frame, theme_frame, button_frame],
            'frames': [results_frame, dir_frame, options_frame, progress_frame, 
                      summary_frame, global_actions_frame, info_frame],
            'outer_frames': [results_outer_frame, dir_outer_frame, options_outer_frame,
                           progress_outer_frame, summary_outer_frame, global_actions_outer,
                           info_outer_frame],
            'labels': [results_label, dir_label, options_label, progress_label,
                      summary_label_title, global_actions_label, info_label],
            'entry': self.dir_entry,
            'buttons': [browse_btn],
            'checkboxes': [pixel_check, verbose_check],
            'text_widgets': [info_text],
            'entry_frame': dir_entry_frame
        }
        
        # Applica il tema iniziale
        self.apply_theme(self.current_theme)
    
    def apply_theme(self, theme_name):
        """Applica un tema specifico a tutti i widget dell'interfaccia."""
        if theme_name not in self.themes:
            return
        
        self.current_theme = theme_name
        theme = self.themes[theme_name]
        
        # Aggiorna i pulsanti tema
        for name, btn in self.theme_buttons.items():
            if name == theme_name:
                btn.config(bg=theme["primary"], fg="white", relief="sunken")
            else:
                btn.config(bg=theme["button_bg"], fg=theme["fg"], relief="raised")
        
        # Applica colori di sfondo principale
        self.root.config(bg=theme["bg"])
        
        # Aggiorna gli stili ttk
        style = ttk.Style()
        
        # Configura gli stili con i colori del tema
        style.configure('Title.TLabel', 
                       foreground=theme["primary"],
                       background=theme["bg"],
                       font=('Arial', 20, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       foreground=theme["fg"],
                       background=theme["bg"],
                       font=('Arial', 11))
        
        style.configure('Success.TButton',
                       background=theme["success"],
                       foreground='white',
                       font=('Arial', 10, 'bold'))
        
        style.configure('Danger.TButton',
                       background=theme["danger"],
                       foreground='white',
                       font=('Arial', 10, 'bold'))
        
        style.configure('Warning.TButton',
                       background=theme["warning"],
                       foreground='white',
                       font=('Arial', 10, 'bold'))
        
        # Progress bar
        style.configure('Custom.Horizontal.TProgressbar',
                       background=theme["success"],
                       troughcolor=theme["frame_bg"],
                       bordercolor=theme["frame_border"],
                       lightcolor=theme["accent"],
                       darkcolor=theme["accent"])
        
        # Frames e labels generici
        style.configure('TFrame',
                       background=theme["bg"],
                       relief='flat')
        
        style.configure('TLabelFrame',
                       background=theme["bg"],
                       foreground=theme["fg"],
                       bordercolor=theme["frame_border"],
                       relief='solid',
                       borderwidth=2)
        
        style.configure('TLabelFrame.Label',
                       background=theme["bg"],
                       foreground=theme["primary"],
                       font=('Arial', 10, 'bold'))
        
        style.configure('TLabel',
                       background=theme["bg"],
                       foreground=theme["fg"])
        
        style.configure('TEntry',
                       fieldbackground=theme["text_bg"],
                       foreground=theme["fg"],
                       bordercolor=theme["frame_border"],
                       lightcolor=theme["accent"],
                       darkcolor=theme["accent"])
        
        style.configure('TButton',
                       background=theme["button_bg"],
                       foreground=theme["fg"],
                       bordercolor=theme["frame_border"],
                       focuscolor=theme["accent"])
        
        style.configure('TCheckbutton',
                       background=theme["bg"],
                       foreground=theme["fg"],
                       focuscolor=theme["accent"])
        
        # Applica colori ai widget tk nativi
        if hasattr(self, 'results_text'):
            self.results_text.config(
                bg=theme["text_bg"],
                fg=theme["fg"],
                insertbackground=theme["primary"],
                selectbackground=theme["accent"],
                selectforeground="white"
            )
        
        if hasattr(self, 'controls_canvas'):
            self.controls_canvas.config(bg=theme["bg"], highlightbackground=theme["frame_border"])
        
        # Aggiorna i widget personalizzati
        if hasattr(self, 'themed_widgets'):
            # Aggiorna frame principali
            for frame in self.themed_widgets['main_frames']:
                frame.config(bg=theme["bg"])
            
            # Aggiorna frame contenitori
            for frame in self.themed_widgets['container_frames']:
                frame.config(bg=theme["bg"])
            
            # Aggiorna frame esterni
            for frame in self.themed_widgets['outer_frames']:
                frame.config(bg=theme["bg"])
            
            # Aggiorna frame interni
            for frame in self.themed_widgets['frames']:
                frame.config(bg=theme["frame_bg"], 
                           highlightbackground=theme["frame_border"])
            
            # Aggiorna etichette
            for label in self.themed_widgets['labels']:
                if 'title' in str(label):  # Etichette titolo
                    label.config(bg=theme["bg"], fg=theme["primary"])
                else:  # Altre etichette
                    label.config(bg=theme["bg"], fg=theme["primary"])
            
            # Aggiorna entry
            if hasattr(self, 'themed_widgets') and 'entry' in self.themed_widgets:
                self.themed_widgets['entry'].config(
                    bg=theme["text_bg"], 
                    fg=theme["fg"],
                    highlightbackground=theme["frame_border"]
                )
            
            # Aggiorna pulsanti
            for btn in self.themed_widgets['buttons']:
                btn.config(bg=theme["button_bg"], fg=theme["fg"],
                          activebackground=theme["accent"])
            
            # Aggiorna checkbox
            for cb in self.themed_widgets['checkboxes']:
                cb.config(bg=theme["frame_bg"], fg=theme["fg"],
                         selectcolor=theme["accent"],
                         activebackground=theme["button_bg"])
            
            # Aggiorna widget di testo
            for text_widget in self.themed_widgets['text_widgets']:
                text_widget.config(bg=theme["text_bg"], fg=theme["fg"])
        
        # Aggiorna specifici widget con riferimenti diretti
        if hasattr(self, 'status_label'):
            self.status_label.config(bg=theme["frame_bg"], fg=theme["success"])
        
        if hasattr(self, 'summary_label'):
            self.summary_label.config(bg=theme["frame_bg"], fg=theme["secondary"])
        
        if hasattr(self, 'delete_selected_btn'):
            self.delete_selected_btn.config(bg=theme["warning"], fg="white",
                                          activebackground=theme["danger"])
        
        if hasattr(self, 'auto_select_btn'):
            self.auto_select_btn.config(bg=theme["button_bg"], fg=theme["fg"],
                                      activebackground=theme["accent"])
        
        if hasattr(self, 'manage_garbage_btn'):
            self.manage_garbage_btn.config(bg=theme["button_bg"], fg=theme["fg"],
                                         activebackground=theme["accent"])
        
        # Aggiorna scrollable_controls se esiste
        if hasattr(self, 'scrollable_controls'):
            self.scrollable_controls.config(bg=theme["bg"])
        
        # Aggiorna widget dei controlli duplicati se presenti
        self.update_duplicate_controls_theme(theme)
    
    def update_duplicate_controls_theme(self, theme):
        """Aggiorna i colori dei controlli duplicati con il tema corrente."""
        # Aggiorna tutti i widget nel frame scrollabile
        for widget in self.scrollable_controls.winfo_children():
            if isinstance(widget, tk.Frame):
                # Frame gruppo
                widget.config(bg=theme["frame_bg"], relief='solid', bd=2,
                             highlightbackground=theme["frame_border"], highlightthickness=1)
                
                # Aggiorna tutti i figli del frame
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=theme["frame_bg"], fg=theme["fg"])
                    elif isinstance(child, tk.Checkbutton):
                        child.config(bg=theme["frame_bg"], fg=theme["fg"],
                                   selectcolor=theme["accent"], activebackground=theme["button_bg"])
                    elif isinstance(child, tk.Button):
                        # Determina il tipo di pulsante dal testo
                        button_text = child.cget('text')
                        if 'Anteprima' in button_text:
                            child.config(bg=theme["secondary"], fg="white",
                                       activebackground=theme["accent"])
                        elif 'Elimina' in button_text or 'Sposta' in button_text:
                            child.config(bg=theme["danger"], fg="white",
                                       activebackground=theme["warning"])
                        else:
                            child.config(bg=theme["button_bg"], fg=theme["fg"],
                                       activebackground=theme["accent"])
                    elif isinstance(child, tk.Frame):
                        # Frame interni (per il layout)
                        child.config(bg=theme["frame_bg"])
                        # Aggiorna anche i loro figli
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, (tk.Label, tk.Checkbutton, tk.Button)):
                                if isinstance(grandchild, tk.Label):
                                    grandchild.config(bg=theme["frame_bg"], fg=theme["fg"])
                                elif isinstance(grandchild, tk.Checkbutton):
                                    grandchild.config(bg=theme["frame_bg"], fg=theme["fg"],
                                                    selectcolor=theme["accent"])
                                elif isinstance(grandchild, tk.Button):
                                    button_text = grandchild.cget('text')
                                    if 'Anteprima' in button_text:
                                        grandchild.config(bg=theme["secondary"], fg="white")
                                    elif 'Elimina' in button_text or 'Sposta' in button_text:
                                        grandchild.config(bg=theme["danger"], fg="white")
                                    else:
                                        grandchild.config(bg=theme["button_bg"], fg=theme["fg"])
    
    def browse_directory(self):
        """Apre dialog per selezione directory."""
        directory = filedialog.askdirectory(title="Seleziona directory da scansionare")
        if directory:
            self.directory_var.set(directory)
    
    def start_analysis(self):
        """Avvia l'analisi in un thread separato."""
        directory = self.directory_var.get().strip()
        
        if not directory:
            messagebox.showerror("Errore", "Seleziona una directory da scansionare")
            return
        
        if not Path(directory).exists():
            messagebox.showerror("Errore", "La directory selezionata non esiste")
            return
        
        # Reset UI
        self.clear_results()
        self.is_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.save_btn.config(state="disabled")
        
        # Avvia thread analisi
        self.analysis_thread = threading.Thread(target=self.run_analysis, 
                                               args=(directory,))
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
    
    def stop_analysis(self):
        """Interrompe l'analisi."""
        self.is_running = False
        self.progress_queue.put(("status", "Interruzione in corso..."))
        
        # Reset UI
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
    
    def run_analysis(self, directory):
        """Esegue l'analisi (da eseguire in thread separato)."""
        try:
            self.finder = ImageDuplicateFinder(verbose=self.verbose_var.get())
            
            # Scansione directory
            self.progress_queue.put(("status", "Scansionando directory..."))
            self.progress_queue.put(("progress", 10))
            
            if not self.is_running:
                return
            
            self.finder.scan_directory(Path(directory))
            
            if not self.finder.image_paths:
                self.progress_queue.put(("error", "Nessuna immagine trovata nella directory"))
                return
            
            total_images = len(self.finder.image_paths)
            self.progress_queue.put(("status", f"Calcolando hash per {total_images} immagini..."))
            self.progress_queue.put(("progress", 30))
            
            if not self.is_running:
                return
            
            # Calcolo hash
            self.finder.find_duplicates_by_hash()
            self.progress_queue.put(("progress", 70))
            
            if not self.is_running:
                return
            
            # Verifica pixel se richiesta
            if self.pixel_verify_var.get():
                self.progress_queue.put(("status", "Verificando con confronto pixel..."))
                self.verify_duplicates_with_progress()
            
            self.progress_queue.put(("progress", 100))
            self.progress_queue.put(("status", "Analisi completata"))
            
            # Prepara risultati
            results = self.prepare_results()
            self.results_queue.put(results)
            
        except Exception as e:
            self.progress_queue.put(("error", f"Errore durante l'analisi: {str(e)}"))
        finally:
            self.is_running = False
    
    def verify_duplicates_with_progress(self):
        """Verifica duplicati con confronto pixel mostrando il progresso."""
        if not self.finder.duplicates:
            return
        
        # Calcola il numero totale di confronti da fare
        total_comparisons = 0
        for group_paths in self.finder.duplicates.values():
            if len(group_paths) > 1:
                # Per ogni gruppo, confrontiamo ogni file con il primo
                total_comparisons += len(group_paths) - 1
        
        if total_comparisons == 0:
            return
        
        # Lista per tenere traccia dei gruppi verificati
        verified_groups = {}
        current_comparison = 0
        
        for file_hash, group_paths in list(self.finder.duplicates.items()):
            if len(group_paths) <= 1:
                continue
            
            if not self.is_running:
                break
            
            # Aggiorna status per questo gruppo
            self.progress_queue.put(("status", f"Confronto pixel gruppo {len(verified_groups)+1}..."))
            
            # Confronta ogni file con il primo del gruppo
            reference_path = group_paths[0]
            verified_paths = [reference_path]  # Il primo è sempre incluso
            
            try:
                with Image.open(reference_path) as ref_img:
                    ref_pixels = list(ref_img.getdata())
                    
                    for i, compare_path in enumerate(group_paths[1:], 1):
                        if not self.is_running:
                            break
                        
                        current_comparison += 1
                        
                        # Aggiorna progresso
                        progress = 70 + (current_comparison / total_comparisons) * 25  # 70-95%
                        self.progress_queue.put(("progress", progress))
                        
                        # Aggiorna status dettagliato
                        self.progress_queue.put(("status", 
                            f"Confronto pixel {current_comparison}/{total_comparisons}: {compare_path.name}"))
                        
                        try:
                            with Image.open(compare_path) as comp_img:
                                # Confronta dimensioni
                                if ref_img.size != comp_img.size:
                                    continue  # Dimensioni diverse = non duplicati
                                
                                comp_pixels = list(comp_img.getdata())
                                
                                # Confronta pixel (campionamento per immagini grandi)
                                if len(ref_pixels) > 1000000:  # > 1M pixel
                                    # Campiona ogni 100° pixel per performance
                                    sample_indices = range(0, len(ref_pixels), 100)
                                    pixels_match = all(ref_pixels[idx] == comp_pixels[idx] 
                                                     for idx in sample_indices)
                                else:
                                    # Confronto completo per immagini piccole
                                    pixels_match = ref_pixels == comp_pixels
                                
                                if pixels_match:
                                    verified_paths.append(compare_path)
                        
                        except Exception as e:
                            if self.verbose_var.get():
                                print(f"Errore confronto pixel {compare_path}: {e}")
                            continue
            
            except Exception as e:
                if self.verbose_var.get():
                    print(f"Errore apertura immagine di riferimento {reference_path}: {e}")
                continue
            
            # Aggiorna il gruppo con solo i file verificati come identici
            if len(verified_paths) > 1:
                verified_groups[file_hash] = verified_paths
        
        # Sostituisci i duplicati con quelli verificati
        self.finder.duplicates = verified_groups
        
        # Aggiorna progresso finale
        self.progress_queue.put(("progress", 95))
        self.progress_queue.put(("status", "Verifica pixel completata"))
    
    def prepare_results(self):
        """Prepara i risultati per la visualizzazione."""
        if not self.finder.duplicates:
            return {
                "summary": f"Analizzate {len(self.finder.image_paths)} immagini - Nessun duplicato trovato! 🎉",
                "details": "Tutte le immagini nella directory sono uniche."
            }
        
        total_duplicates = sum(len(paths) - 1 for paths in self.finder.duplicates.values())
        total_space = sum(paths[0].stat().st_size * (len(paths) - 1) 
                         for paths in self.finder.duplicates.values() if paths)
        
        summary = (f"Analizzate {len(self.finder.image_paths)} immagini - "
                  f"Trovati {len(self.finder.duplicates)} gruppi di duplicati - "
                  f"{total_duplicates} file da rimuovere - "
                  f"Spazio recuperabile: {total_space/1024/1024:.1f} MB")
        
        details = []
        details.append("📋 REPORT DUPLICATI TROVATI")
        details.append("=" * 80)
        details.append("")
        details.append(f"📊 RIEPILOGO:")
        details.append(f"   • Immagini totali scansionate: {len(self.finder.image_paths)}")
        details.append(f"   • Gruppi di duplicati trovati: {len(self.finder.duplicates)}")
        details.append(f"   • File duplicati da rimuovere: {total_duplicates}")
        details.append(f"   • Spazio totale recuperabile: {total_space:,} bytes ({total_space/1024/1024:.2f} MB)")
        details.append("")
        details.append("💡 SUGGERIMENTO: Mantieni UN file per gruppo, elimina gli altri")
        details.append("=" * 80)
        details.append("")
        
        for i, (file_hash, paths) in enumerate(self.finder.duplicates.items(), 1):
            if not paths:
                continue
                
            file_size = paths[0].stat().st_size
            space_saved = file_size * (len(paths) - 1)
            
            # Header del gruppo con box
            details.append("┌" + "─" * 78 + "┐")
            details.append(f"│ 🎯 GRUPPO {i:2d} - {len(paths)} FILE IDENTICI" + " " * (78 - len(f"GRUPPO {i:2d} - {len(paths)} FILE IDENTICI") - 6) + "│")
            details.append("├" + "─" * 78 + "┤")
            details.append(f"│ 📏 Dimensione file: {file_size:,} bytes" + " " * (78 - len(f"Dimensione file: {file_size:,} bytes") - 4) + "│")
            details.append(f"│ 💾 Spazio recuperabile: {space_saved:,} bytes ({space_saved/1024/1024:.2f} MB)" + " " * max(0, 78 - len(f"Spazio recuperabile: {space_saved:,} bytes ({space_saved/1024/1024:.2f} MB)") - 4) + "│")
            details.append(f"│ 🔑 Hash: {file_hash[:32]}..." + " " * (78 - len(f"Hash: {file_hash[:32]}...") - 4) + "│")
            details.append("└" + "─" * 78 + "┘")
            details.append("")
            
            # Trova il file "originale" (quello nella directory principale o con nome più semplice)
            original_idx = 0
            main_dir = Path(self.finder.image_paths[0]).parents[-2] if self.finder.image_paths else None
            
            for idx, path in enumerate(paths):
                # Preferisci file nella directory principale
                if main_dir and str(path).startswith(str(main_dir)):
                    original_idx = idx
                    break
                # O quello con il nome più corto/semplice
                if len(str(path)) < len(str(paths[original_idx])):
                    original_idx = idx
            
            # Mostra il file "originale" per primo
            if original_idx != 0:
                paths[0], paths[original_idx] = paths[original_idx], paths[0]
            
            for j, path in enumerate(paths):
                metadata = self.finder.get_image_metadata(path)
                
                if j == 0:
                    details.append(f"    ⭐ ORIGINALE CONSIGLIATO:")
                    prefix = "    📄 "
                else:
                    if j == 1:
                        details.append(f"    🗑️  DUPLICATI DA RIMUOVERE:")
                    prefix = "    📄 "
                
                # Nome file e percorso
                filename = path.name
                folder = str(path.parent.relative_to(Path(self.directory_var.get()))) if hasattr(self, 'directory_var') else str(path.parent)
                if folder == ".":
                    folder = "(Directory principale)"
                
                details.append(f"{prefix}{filename}")
                details.append(f"        📁 Cartella: {folder}")
                
                if metadata['creation_time']:
                    details.append(f"        📅 Creato: {metadata['creation_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                if metadata['dimensions']:
                    details.append(f"        📐 Dimensioni: {metadata['dimensions'][0]}x{metadata['dimensions'][1]} pixel")
                
                details.append("")
            
            details.append("💡 AZIONE CONSIGLIATA:")
            details.append("   • Mantieni il file ORIGINALE (⭐)")
            details.append("   • Elimina tutti i DUPLICATI (🗑️)")
            details.append("")
            details.append("─" * 80)
            details.append("")
        
        details.append("🚨 IMPORTANTE: Questo programma NON elimina automaticamente i file!")
        details.append("   Dovrai eliminare manualmente i duplicati che non desideri mantenere.")
        details.append("")
        details.append("✅ Analisi completata con successo!")
        
        return {
            "summary": summary,
            "details": "\n".join(details)
        }
    
    def check_queues(self):
        """Controlla periodicamente le queue per aggiornamenti."""
        # Check progress queue
        try:
            while True:
                msg_type, data = self.progress_queue.get_nowait()
                
                if msg_type == "status":
                    self.status_label.config(text=data)
                elif msg_type == "progress":
                    self.progress_var.set(data)
                elif msg_type == "error":
                    messagebox.showerror("Errore", data)
                    self.reset_ui()
        except queue.Empty:
            pass
        
        # Check results queue
        try:
            results = self.results_queue.get_nowait()
            self.show_results(results)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_queues)
    
    def show_results(self, results):
        """Mostra i risultati nell'interfaccia."""
        self.summary_label.config(text=results["summary"])
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, results["details"])
        
        # Aggiorna i controlli per la gestione dei duplicati
        self.update_duplicate_controls()
        
        self.reset_ui()
        self.save_btn.config(state="normal")
    
    def clear_results(self):
        """Pulisce i risultati."""
        self.summary_label.config(text="")
        self.results_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_label.config(text="Avvio analisi...")
        
        # Pulisci controlli duplicati
        for widget in self.scrollable_controls.winfo_children():
            widget.destroy()
        self.group_checkboxes.clear()
        self.group_select_all_vars.clear()
        self.duplicate_groups.clear()
        
        # Disabilita pulsanti di eliminazione
        self.delete_selected_btn.config(state="disabled", text="� Sposta File Selezionati nel Cestino")
        self.auto_select_btn.config(state="disabled")
        self.manage_garbage_btn.config(state="disabled")
    
    def reset_ui(self):
        """Ripristina l'interfaccia utente."""
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.is_running = False
    
    def save_report(self):
        """Salva il report su file."""
        if not self.finder:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("File di testo", "*.txt"), ("Tutti i file", "*.*")],
            title="Salva report duplicati"
        )
        
        if filename:
            try:
                content = f"REPORT IMMAGINI DUPLICATE - GUI\n"
                content += f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                content += f"Directory: {self.directory_var.get()}\n\n"
                content += self.results_text.get(1.0, tk.END)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                messagebox.showinfo("Successo", f"Report salvato in:\n{filename}")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel salvataggio:\n{str(e)}")
    
    def on_closing(self):
        """Gestisce la chiusura dell'applicazione."""
        if self.is_running:
            if messagebox.askokcancel("Chiudi", "Analisi in corso. Vuoi davvero chiudere?"):
                self.is_running = False
                self.root.destroy()
        else:
            self.root.destroy()
    
    def update_duplicate_controls(self):
        """Aggiorna i controlli per la gestione dei duplicati."""
        # Pulisci controlli esistenti
        for widget in self.scrollable_controls.winfo_children():
            widget.destroy()
        
        self.group_checkboxes.clear()
        self.group_select_all_vars.clear()
        
        if not self.finder or not self.finder.duplicates:
            no_duplicates_label = ttk.Label(self.scrollable_controls, 
                                           text="Nessun duplicato trovato",
                                           font=('Arial', 10, 'italic'),
                                           foreground='#666666')
            no_duplicates_label.pack(pady=20)
            return
        
        # Prepara i gruppi di duplicati
        self.duplicate_groups = []
        for i, (file_hash, paths) in enumerate(self.finder.duplicates.items()):
            if len(paths) > 1:
                self.duplicate_groups.append({
                    'id': i,
                    'hash': file_hash,
                    'paths': paths.copy()
                })
        
        # Crea controlli per ogni gruppo
        for group in self.duplicate_groups:
            self.create_group_controls(group)
        
        # Abilita pulsanti
        self.delete_selected_btn.config(state="normal")
        self.auto_select_btn.config(state="normal")
        self.manage_garbage_btn.config(state="normal")
    
    def create_group_controls(self, group):
        """Crea i controlli per un singolo gruppo di duplicati."""
        group_id = group['id']
        paths = group['paths']
        theme = self.themes[self.current_theme]
        
        # Frame per il gruppo con stile personalizzato
        group_frame = tk.Frame(self.scrollable_controls, 
                              bg=theme["frame_bg"],
                              relief='solid',
                              bd=2,
                              highlightbackground=theme["frame_border"],
                              highlightthickness=1)
        group_frame.pack(fill="x", padx=5, pady=5)
        
        # Etichetta del gruppo
        group_label = tk.Label(group_frame,
                              text=f"🎯 Gruppo {group_id + 1} ({len(paths)} file)",
                              bg=theme["frame_bg"],
                              fg=theme["primary"],
                              font=('Arial', 10, 'bold'))
        group_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Header con controlli principali
        header_frame = tk.Frame(group_frame, bg=theme["frame_bg"])
        header_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Checkbox "seleziona tutti i duplicati"
        select_all_var = tk.BooleanVar()
        self.group_select_all_vars[group_id] = select_all_var
        
        select_all_check = tk.Checkbutton(header_frame,
                                         text="⚡ Seleziona tutti i duplicati",
                                         variable=select_all_var,
                                         command=lambda gid=group_id: self.toggle_group_selection(gid),
                                         bg=theme["frame_bg"],
                                         fg=theme["fg"],
                                         selectcolor=theme["accent"],
                                         activebackground=theme["button_bg"])
        select_all_check.pack(side="left")
        
        # Info gruppo
        file_size = paths[0].stat().st_size if paths else 0
        space_saved = file_size * (len(paths) - 1)
        info_label = tk.Label(header_frame,
                              text=f"💾 Spazio recuperabile: {space_saved/1024/1024:.1f} MB",
                              font=('Arial', 9),
                              bg=theme["frame_bg"],
                              fg=theme["secondary"])
        info_label.pack(side="right", padx=(0, 10))
        
        # Pulsante preview
        preview_btn = tk.Button(header_frame, 
                               text="👁️ Anteprima",
                               command=lambda: self.open_image_preview(group),
                               bg=theme["secondary"],
                               fg="white",
                               activebackground=theme["accent"],
                               font=('Arial', 9, 'bold'),
                               relief='flat',
                               padx=10,
                               pady=3)
        preview_btn.pack(side="right", padx=(10, 0))
        
        # Determina il file "originale" (quello da mantenere)
        original_idx = self.find_original_file_index(paths)
        
        # Checkbox per ogni file nel gruppo
        self.group_checkboxes[group_id] = {}
        
        # Layout migliorato con thumbnails
        for i, path in enumerate(paths):
            file_container = tk.Frame(group_frame, bg=theme["frame_bg"])
            file_container.pack(fill="x", pady=3, padx=10)
            
            # Frame sinistro per checkbox e thumbnail
            left_frame = tk.Frame(file_container, bg=theme["frame_bg"])
            left_frame.pack(side="left", padx=(0, 10))
            
            # Variabile per checkbox del file
            file_var = tk.BooleanVar()
            self.group_checkboxes[group_id][str(path)] = file_var
            
            # Determina se è l'originale
            is_original = (i == original_idx)
            
            # Checkbox file
            checkbox = tk.Checkbutton(left_frame,
                                     variable=file_var,
                                     command=self.update_selection_counts,
                                     bg=theme["frame_bg"],
                                     fg=theme["fg"],
                                     selectcolor=theme["accent"],
                                     activebackground=theme["button_bg"])
            checkbox.pack(side="top", pady=(0, 5))
            
            # Thumbnail
            try:
                thumbnail = self.create_thumbnail(left_frame, path, size=(60, 45))
                thumbnail.pack(side="top")
            except Exception:
                placeholder = tk.Label(left_frame, 
                                     text="🖼️", 
                                     font=('Arial', 12),
                                     bg=theme["frame_bg"],
                                     fg=theme["fg"])
                placeholder.pack(side="top")
            
            # Frame destro per info file
            right_frame = tk.Frame(file_container, bg=theme["frame_bg"])
            right_frame.pack(side="left", fill="x", expand=True)
            
            # Nome file e status
            if is_original:
                icon = "⭐"
                style_color = theme["success"]
                file_text = f"{icon} {path.name} (ORIGINALE - MANTIENI)"
                font_weight = 'bold'
            else:
                icon = "🗑️"
                style_color = theme["danger"]
                file_text = f"{icon} {path.name}"
                font_weight = 'normal'
            
            file_label = tk.Label(right_frame,
                                 text=file_text,
                                 font=('Arial', 10, font_weight),
                                 bg=theme["frame_bg"],
                                 fg=style_color)
            file_label.pack(anchor="w")
            
            # Percorso relativo
            try:
                rel_path = path.relative_to(Path(self.directory_var.get()))
                path_text = str(rel_path.parent) if rel_path.parent != Path('.') else "(Directory principale)"
            except:
                path_text = str(path.parent)
            
            path_label = tk.Label(right_frame,
                                 text=f"📁 {path_text}",
                                 font=('Arial', 8),
                                 bg=theme["frame_bg"],
                                 fg=theme["fg"])
            path_label.pack(anchor="w")
            
            # Info aggiuntive
            try:
                stat_info = path.stat()
                size_mb = stat_info.st_size / 1024 / 1024
                
                # Prova a leggere dimensioni immagine
                try:
                    with Image.open(path) as img:
                        dimensions = f"{img.size[0]}x{img.size[1]}"
                except:
                    dimensions = "N/A"
                
                extra_info = f"📏 {size_mb:.1f} MB • 📐 {dimensions} px"
                extra_label = tk.Label(right_frame,
                                       text=extra_info,
                                       font=('Arial', 8),
                                       bg=theme["frame_bg"],
                                       fg=theme["fg"])
                extra_label.pack(anchor="w")
            except:
                pass
    
    def find_original_file_index(self, paths):
        """Trova l'indice del file "originale" (quello consigliato da mantenere)."""
        if not paths:
            return 0
        
        # Strategia: preferisci file nella directory principale o con nome più semplice
        original_idx = 0
        base_dir = Path(self.directory_var.get()) if hasattr(self, 'directory_var') else None
        
        for idx, path in enumerate(paths):
            # Preferisci file nella directory principale
            if base_dir and path.parent == base_dir:
                return idx
            
            # O quello con il percorso più corto
            if len(str(path)) < len(str(paths[original_idx])):
                original_idx = idx
        
        return original_idx
    
    def toggle_group_selection(self, group_id):
        """Toggle selezione di tutti i duplicati in un gruppo (escluso l'originale)."""
        if group_id not in self.group_select_all_vars:
            return
        
        select_all = self.group_select_all_vars[group_id].get()
        group = next((g for g in self.duplicate_groups if g['id'] == group_id), None)
        
        if not group:
            return
        
        # Trova l'originale
        original_idx = self.find_original_file_index(group['paths'])
        
        # Seleziona/deseleziona tutti i duplicati (non l'originale)
        for i, path in enumerate(group['paths']):
            if i != original_idx:  # Non l'originale
                path_str = str(path)
                if path_str in self.group_checkboxes[group_id]:
                    self.group_checkboxes[group_id][path_str].set(select_all)
        
        self.update_selection_counts()
    
    def auto_select_duplicates(self):
        """Selezione automatica di tutti i duplicati (preservando gli originali)."""
        for group in self.duplicate_groups:
            group_id = group['id']
            original_idx = self.find_original_file_index(group['paths'])
            
            # Seleziona tutti i duplicati del gruppo
            for i, path in enumerate(group['paths']):
                if i != original_idx:  # Non l'originale
                    path_str = str(path)
                    if path_str in self.group_checkboxes[group_id]:
                        self.group_checkboxes[group_id][path_str].set(True)
            
            # Aggiorna il checkbox "seleziona tutti" del gruppo
            if group_id in self.group_select_all_vars:
                self.group_select_all_vars[group_id].set(True)
        
        self.update_selection_counts()
        messagebox.showinfo("Selezione Automatica", 
                          "Tutti i duplicati sono stati selezionati!\n"
                          "I file originali sono stati preservati.")
    
    def update_selection_counts(self):
        """Aggiorna il conteggio dei file selezionati."""
        total_selected = 0
        total_space = 0
        
        for group in self.duplicate_groups:
            group_id = group['id']
            if group_id in self.group_checkboxes:
                for path_str, var in self.group_checkboxes[group_id].items():
                    if var.get():
                        total_selected += 1
                        try:
                            file_size = Path(path_str).stat().st_size
                            total_space += file_size
                        except:
                            pass
        
        # Aggiorna il testo del pulsante
        if total_selected > 0:
            self.delete_selected_btn.config(
                text=f"� Sposta {total_selected} File nel Cestino ({total_space/1024/1024:.1f} MB)"
            )
        else:
            self.delete_selected_btn.config(text="� Sposta File Selezionati nel Cestino")
    
    def delete_selected_files(self):
        """Sposta i file selezionati nella cartella garbage con conferma."""
        # Raccogli file selezionati
        files_to_move = []
        groups_affected = []
        
        for group in self.duplicate_groups:
            group_id = group['id']
            selected_in_group = []
            
            if group_id in self.group_checkboxes:
                for path_str, var in self.group_checkboxes[group_id].items():
                    if var.get():
                        files_to_move.append(Path(path_str))
                        selected_in_group.append(path_str)
            
            if selected_in_group:
                groups_affected.append({
                    'group_id': group_id,
                    'total_files': len(group['paths']),
                    'selected_files': len(selected_in_group),
                    'remaining_files': len(group['paths']) - len(selected_in_group)
                })
        
        if not files_to_move:
            messagebox.showwarning("Attenzione", "Nessun file selezionato per lo spostamento.")
            return
        
        # Verifica di sicurezza: almeno un file per gruppo deve rimanere
        for group_info in groups_affected:
            if group_info['remaining_files'] == 0:
                messagebox.showerror("Errore di Sicurezza", 
                                   f"Impossibile spostare tutti i file del Gruppo {group_info['group_id'] + 1}!\n"
                                   "Almeno un file per gruppo deve rimanere.")
                return
        
        # Calcola spazio totale
        total_space = sum(f.stat().st_size for f in files_to_move if f.exists())
        
        # Crea cartella garbage se non esiste
        if not self.garbage_folder:
            self.create_garbage_folder()
        
        # Conferma spostamento
        message = (f"� SPOSTA NEL CESTINO TEMPORANEO\n\n"
                  f"File da spostare: {len(files_to_move)}\n"
                  f"Dimensione totale: {total_space/1024/1024:.1f} MB\n"
                  f"Destinazione: {self.garbage_folder.name}/\n"
                  f"Gruppi interessati: {len(groups_affected)}\n\n"
                  f"💡 I file verranno spostati in una cartella temporanea.\n"
                  f"Potrai eliminarli definitivamente o ripristinarli in seguito.\n\n"
                  f"Procedere con lo spostamento?")
        
        if not messagebox.askyesno("Conferma Spostamento", message):
            return
        
        # Procedi con lo spostamento
        moved_count = 0
        failed_moves = []
        
        for file_path in files_to_move:
            try:
                if file_path.exists():
                    if self.move_to_garbage(file_path):
                        moved_count += 1
                    else:
                        failed_moves.append(f"{file_path.name}: Errore nello spostamento")
            except Exception as e:
                failed_moves.append(f"{file_path.name}: {str(e)}")
        
        # Mostra risultato
        if failed_moves:
            error_msg = f"Spostati {moved_count}/{len(files_to_move)} file.\n\n"
            error_msg += "Errori:\n" + "\n".join(failed_moves[:5])
            if len(failed_moves) > 5:
                error_msg += f"\n... e altri {len(failed_moves) - 5} errori"
            messagebox.showerror("Spostamento Parziale", error_msg)
        else:
            messagebox.showinfo("Successo", 
                              f"✅ Spostati con successo {moved_count} file nel cestino!\n"
                              f"Dimensione spostata: {total_space/1024/1024:.1f} MB\n\n"
                              f"📁 Cartella cestino: {self.garbage_folder.name}/\n"
                              f"💡 Usa 'Gestisci Cestino' per eliminare definitivamente o ripristinare.")
        
        # Aggiorna la visualizzazione
        if moved_count > 0:
            self.refresh_analysis()
    
    def create_garbage_folder(self):
        """Crea la cartella garbage nella directory di scansione."""
        if not self.directory_var.get():
            return None
        
        try:
            base_dir = Path(self.directory_var.get())
            garbage_path = base_dir / "garbage_duplicates"
            
            if not garbage_path.exists():
                garbage_path.mkdir(exist_ok=True)
                # Crea un file README nella cartella garbage
                readme_content = f"""# Cartella Cestino Duplicati

Questa cartella contiene i file duplicati spostati temporaneamente.

Data creazione: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Directory scansionata: {base_dir}

ISTRUZIONI:
- I file qui dentro sono duplicati che sono stati rimossi dalla scansione
- Puoi controllare manualmente i file prima di eliminarli definitivamente
- Per eliminare definitivamente: seleziona tutti i file e cancellali
- Per ripristinare un file: spostalo nella posizione originale

ATTENZIONE: Questa cartella viene ricreata ad ogni nuova scansione!
"""
                with open(garbage_path / "README.txt", 'w', encoding='utf-8') as f:
                    f.write(readme_content)
            
            self.garbage_folder = garbage_path
            return garbage_path
            
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile creare la cartella cestino:\n{str(e)}")
            return None
    
    def manage_garbage_folder(self):
        """Gestisce la cartella garbage (apri, svuota, info)."""
        if not self.garbage_folder or not self.garbage_folder.exists():
            messagebox.showinfo("Info", "La cartella cestino non esiste ancora.\n"
                               "Verrà creata automaticamente quando sposti i primi file.")
            return
        
        # Conta i file nella cartella garbage
        files_in_garbage = list(self.garbage_folder.glob("*"))
        files_count = len([f for f in files_in_garbage if f.is_file() and f.name != "README.txt"])
        
        if files_count == 0:
            message = "🗂️ La cartella cestino è vuota.\n\nVuoi aprirla comunque?"
        else:
            total_size = sum(f.stat().st_size for f in files_in_garbage 
                           if f.is_file() and f.name != "README.txt")
            message = (f"🗂️ CARTELLA CESTINO\n\n"
                      f"📁 Percorso: {self.garbage_folder}\n"
                      f"📄 File presenti: {files_count}\n"
                      f"💾 Spazio occupato: {total_size/1024/1024:.1f} MB\n\n"
                      f"Cosa vuoi fare?")
        
        # Dialog personalizzato con più opzioni
        result = self.show_garbage_options_dialog(message, files_count > 0)
        
        if result == "open":
            self.open_garbage_folder()
        elif result == "empty":
            self.empty_garbage_folder()
    
    def show_garbage_options_dialog(self, message, has_files):
        """Mostra dialog con opzioni per gestire la cartella garbage."""
        dialog = tk.Toplevel(self.root)
        dialog.title("🗂️ Gestisci Cestino")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centra il dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        result = None
        
        def set_result(value):
            nonlocal result
            result = value
            dialog.destroy()
        
        # Frame principale
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Messaggio
        ttk.Label(main_frame, text=message, font=('Arial', 10), justify="left").pack(pady=(0, 20))
        
        # Pulsanti
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="📁 Apri Cartella", 
                  command=lambda: set_result("open")).pack(fill="x", pady=(0, 10))
        
        if has_files:
            ttk.Button(button_frame, text="🗑️ Svuota Cestino", 
                      command=lambda: set_result("empty")).pack(fill="x", pady=(0, 10))
        
        ttk.Button(button_frame, text="❌ Annulla", 
                  command=lambda: set_result("cancel")).pack(fill="x")
        
        dialog.wait_window()
        return result
    
    def open_garbage_folder(self):
        """Apre la cartella garbage nell'explorer."""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(self.garbage_folder))
            elif os.name == 'posix':  # macOS/Linux
                os.system(f'open "{self.garbage_folder}"')
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aprire la cartella:\n{str(e)}")
    
    def empty_garbage_folder(self):
        """Svuota completamente la cartella garbage."""
        if not self.garbage_folder or not self.garbage_folder.exists():
            return
        
        files_to_delete = [f for f in self.garbage_folder.glob("*") 
                          if f.is_file() and f.name != "README.txt"]
        
        if not files_to_delete:
            messagebox.showinfo("Info", "La cartella cestino è già vuota.")
            return
        
        total_size = sum(f.stat().st_size for f in files_to_delete)
        
        message = (f"🚨 SVUOTA CESTINO\n\n"
                  f"File da eliminare definitivamente: {len(files_to_delete)}\n"
                  f"Spazio da liberare: {total_size/1024/1024:.1f} MB\n\n"
                  f"⚠️ ATTENZIONE: Questa operazione è IRREVERSIBILE!\n"
                  f"I file verranno eliminati definitivamente dal disco.\n\n"
                  f"Sei sicuro di voler continuare?")
        
        if messagebox.askyesno("Conferma Eliminazione Definitiva", message):
            deleted = 0
            errors = []
            
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    deleted += 1
                except Exception as e:
                    errors.append(f"{file_path.name}: {str(e)}")
            
            if errors:
                messagebox.showerror("Eliminazione Parziale",
                                   f"Eliminati definitivamente {deleted}/{len(files_to_delete)} file.\n\n"
                                   f"Errori:\n" + "\n".join(errors[:3]))
            else:
                messagebox.showinfo("Successo", 
                                   f"✅ Eliminati definitivamente {deleted} file!\n"
                                   f"Spazio liberato: {total_size/1024/1024:.1f} MB")
    
    def move_to_garbage(self, file_path):
        """Sposta un file nella cartella garbage invece di eliminarlo."""
        if not self.garbage_folder:
            self.create_garbage_folder()
        
        if not self.garbage_folder:
            return False
        
        try:
            source = Path(file_path)
            
            # Crea nome univoco per evitare conflitti
            base_name = source.stem
            extension = source.suffix
            counter = 1
            
            destination = self.garbage_folder / source.name
            while destination.exists():
                destination = self.garbage_folder / f"{base_name}_{counter}{extension}"
                counter += 1
            
            # Sposta il file
            shutil.move(str(source), str(destination))
            return True
            
        except Exception as e:
            print(f"Errore spostando {file_path} nel cestino: {str(e)}")
            return False
    
    def refresh_analysis(self):
        """Riavvia l'analisi per aggiornare i risultati dopo l'eliminazione."""
        directory = self.directory_var.get().strip()
        if directory and Path(directory).exists():
            messagebox.showinfo("Aggiornamento", 
                              "Riavvio l'analisi per aggiornare i risultati...")
            self.start_analysis()
    
    def create_thumbnail(self, parent, image_path, size=(80, 60)):
        """Crea una piccola thumbnail per i controlli."""
        theme = self.themes[self.current_theme]
        
        try:
            with Image.open(image_path) as img:
                # Mantieni aspect ratio
                img.thumbnail(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                label = tk.Label(parent, 
                                image=photo,
                                bg=theme["frame_bg"],
                                relief='solid',
                                bd=1,
                                highlightbackground=theme["frame_border"])
                label.image = photo  # Mantieni riferimento
                return label
        except Exception:
            # Placeholder se non riesce a caricare
            placeholder = tk.Label(parent, 
                                   text="🖼️\nN/A",
                                   font=('Arial', 8),
                                   bg=theme["frame_bg"],
                                   fg=theme["fg"],
                                   justify='center',
                                   relief='solid',
                                   bd=1,
                                   highlightbackground=theme["frame_border"])
            return placeholder
    
    def open_image_preview(self, group):
        """Apre la finestra di preview per un gruppo di duplicati."""
        try:
            original_idx = self.find_original_file_index(group['paths'])
            preview_window = ImagePreviewWindow(self.root, group, original_idx)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aprire l'anteprima:\n{str(e)}")

class ImagePreviewWindow:
    """Finestra per visualizzare e confrontare originale e duplicati."""
    
    def __init__(self, parent, group_data, original_idx):
        self.parent = parent
        self.group_data = group_data
        self.original_idx = original_idx
        self.paths = group_data['paths']
        
        # Crea finestra
        self.window = tk.Toplevel(parent)
        self.window.title(f"🔍 Preview Gruppo {group_data['id'] + 1} - {len(self.paths)} immagini")
        self.window.geometry("1000x700")
        self.window.minsize(800, 600)
        
        # Rende la finestra modale
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_preview_ui()
        
        # Centra la finestra
        self.center_window()
    
    def center_window(self):
        """Centra la finestra sullo schermo."""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
    
    def setup_preview_ui(self):
        """Configura l'interfaccia della finestra di preview."""
        # Frame principale
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titolo
        title_label = ttk.Label(main_frame, 
                               text=f"📸 Confronto Visivo - Gruppo {self.group_data['id'] + 1}",
                               font=('Arial', 16, 'bold'),
                               foreground='#1976D2')
        title_label.pack(pady=(0, 15))
        
        # Info gruppo
        file_size = self.paths[0].stat().st_size if self.paths else 0
        space_saved = file_size * (len(self.paths) - 1)
        info_label = ttk.Label(main_frame,
                              text=f"💾 {len(self.paths)} file identici - Spazio recuperabile: {space_saved/1024/1024:.1f} MB",
                              font=('Arial', 11),
                              foreground='#666666')
        info_label.pack(pady=(0, 20))
        
        # Notebook per le tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Tab per confronto affiancato
        self.comparison_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.comparison_frame, text="🔄 Confronto Affiancato")
        
        # Tab per vista singola
        self.single_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.single_frame, text="🖼️ Vista Singola")
        
        self.setup_comparison_tab()
        self.setup_single_tab()
        
        # Pulsanti controllo
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="📁 Apri Cartella Originale",
                  command=self.open_original_folder).pack(side="left", padx=(0, 10))
        
        ttk.Button(button_frame, text="� Sposta Duplicati nel Cestino",
                  command=self.delete_duplicates).pack(side="left", padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Chiudi",
                  command=self.window.destroy).pack(side="right")
    
    def setup_comparison_tab(self):
        """Configura il tab per il confronto affiancato."""
        # Scrollable frame
        canvas = tk.Canvas(self.comparison_frame)
        scrollbar = ttk.Scrollbar(self.comparison_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout a griglia per le immagini
        cols = min(3, len(self.paths))  # Max 3 colonne
        
        for i, path in enumerate(self.paths):
            row = i // cols
            col = i % cols
            
            # Frame per ogni immagine
            img_frame = ttk.LabelFrame(scrollable_frame, padding="10")
            img_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Configura peso colonne
            scrollable_frame.columnconfigure(col, weight=1)
            
            # Status (originale/duplicato)
            if i == self.original_idx:
                status_text = "⭐ ORIGINALE (mantieni)"
                status_color = "#2E7D32"
                img_frame.config(text=f"⭐ ORIGINALE")
            else:
                status_text = "🗑️ DUPLICATO"
                status_color = "#D32F2F"
                img_frame.config(text=f"🗑️ DUPLICATO {i}")
            
            # Carica e mostra immagine
            try:
                img_label = self.create_image_thumbnail(img_frame, path, size=(250, 200))
                img_label.pack(pady=(0, 10))
            except Exception as e:
                error_label = ttk.Label(img_frame, 
                                       text=f"❌ Errore caricamento:\n{str(e)[:50]}...",
                                       font=('Arial', 8),
                                       foreground='red')
                error_label.pack(pady=(0, 10))
            
            # Info file
            info_text = f"📄 {path.name}\n📁 {path.parent.name}\n📏 {path.stat().st_size:,} bytes"
            
            try:
                with Image.open(path) as img:
                    info_text += f"\n📐 {img.size[0]}x{img.size[1]} px"
            except:
                pass
            
            info_label = ttk.Label(img_frame, text=info_text,
                                  font=('Arial', 9),
                                  foreground=status_color,
                                  justify='left')
            info_label.pack()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def setup_single_tab(self):
        """Configura il tab per la vista singola con navigazione."""
        self.current_image_idx = 0
        
        # Frame controlli navigazione
        nav_frame = ttk.Frame(self.single_frame)
        nav_frame.pack(fill="x", pady=(0, 10))
        
        self.prev_btn = ttk.Button(nav_frame, text="◀ Precedente",
                                  command=self.prev_image)
        self.prev_btn.pack(side="left")
        
        self.image_counter = ttk.Label(nav_frame, 
                                      text=f"1 / {len(self.paths)}",
                                      font=('Arial', 12, 'bold'))
        self.image_counter.pack(side="left", expand=True)
        
        self.next_btn = ttk.Button(nav_frame, text="Successiva ▶",
                                  command=self.next_image)
        self.next_btn.pack(side="right")
        
        # Frame immagine principale
        self.single_img_frame = ttk.Frame(self.single_frame)
        self.single_img_frame.pack(fill="both", expand=True)
        
        self.load_single_image()
    
    def create_image_thumbnail(self, parent, image_path, size=(150, 120)):
        """Crea una thumbnail dell'immagine."""
        try:
            # Carica immagine
            with Image.open(image_path) as img:
                # Mantieni aspect ratio
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Crea PhotoImage
                photo = ImageTk.PhotoImage(img)
                
                # Crea label
                label = ttk.Label(parent, image=photo)
                label.image = photo  # Mantieni riferimento
                
                return label
        except Exception as e:
            # Se non riesce a caricare, mostra un placeholder
            placeholder = ttk.Label(parent, 
                                   text=f"❌ Errore\n{str(e)[:30]}...",
                                   font=('Arial', 8),
                                   foreground='red',
                                   justify='center')
            return placeholder
    
    def load_single_image(self):
        """Carica l'immagine corrente nella vista singola."""
        # Pulisci frame
        for widget in self.single_img_frame.winfo_children():
            widget.destroy()
        
        path = self.paths[self.current_image_idx]
        
        # Status frame
        status_frame = ttk.Frame(self.single_img_frame)
        status_frame.pack(fill="x", pady=(0, 15))
        
        if self.current_image_idx == self.original_idx:
            status_text = "⭐ ORIGINALE (consigliato da mantenere)"
            status_color = "#2E7D32"
        else:
            status_text = f"🗑️ DUPLICATO {self.current_image_idx + 1}"
            status_color = "#D32F2F"
        
        status_label = ttk.Label(status_frame, text=status_text,
                                font=('Arial', 14, 'bold'),
                                foreground=status_color)
        status_label.pack()
        
        # Immagine grande
        try:
            img_label = self.create_image_thumbnail(self.single_img_frame, path, size=(600, 400))
            img_label.pack(pady=(0, 15))
        except Exception as e:
            error_label = ttk.Label(self.single_img_frame,
                                   text=f"❌ Errore nel caricamento dell'immagine:\n{str(e)}",
                                   font=('Arial', 10),
                                   foreground='red')
            error_label.pack(pady=(0, 15))
        
        # Info dettagliate
        info_frame = ttk.LabelFrame(self.single_img_frame, text="📋 Informazioni File", padding="10")
        info_frame.pack(fill="x")
        
        # Carica metadati
        try:
            stat = path.stat()
            info_text = f"📄 Nome: {path.name}\n"
            info_text += f"📁 Percorso: {path.parent}\n"
            info_text += f"📏 Dimensione: {stat.st_size:,} bytes ({stat.st_size/1024/1024:.2f} MB)\n"
            info_text += f"📅 Modificato: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            # Info immagine
            try:
                with Image.open(path) as img:
                    info_text += f"📐 Risoluzione: {img.size[0]} x {img.size[1]} pixel\n"
                    info_text += f"🎨 Modalità: {img.mode}\n"
                    if hasattr(img, '_getexif') and img._getexif():
                        info_text += f"📷 EXIF: Presente"
                    else:
                        info_text += f"📷 EXIF: Non disponibile"
            except:
                info_text += f"📐 Impossibile leggere metadati immagine"
            
            info_label = ttk.Label(info_frame, text=info_text,
                                  font=('Arial', 9),
                                  justify='left')
            info_label.pack(anchor="w")
        
        except Exception as e:
            error_label = ttk.Label(info_frame,
                                   text=f"Errore nel caricamento delle informazioni: {str(e)}",
                                   foreground='red')
            error_label.pack()
        
        # Aggiorna contatore e pulsanti
        self.image_counter.config(text=f"{self.current_image_idx + 1} / {len(self.paths)}")
        self.prev_btn.config(state="normal" if self.current_image_idx > 0 else "disabled")
        self.next_btn.config(state="normal" if self.current_image_idx < len(self.paths) - 1 else "disabled")
    
    def prev_image(self):
        """Vai all'immagine precedente."""
        if self.current_image_idx > 0:
            self.current_image_idx -= 1
            self.load_single_image()
    
    def next_image(self):
        """Vai all'immagine successiva."""
        if self.current_image_idx < len(self.paths) - 1:
            self.current_image_idx += 1
            self.load_single_image()
    
    def open_original_folder(self):
        """Apre la cartella del file originale."""
        original_path = self.paths[self.original_idx]
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(original_path.parent))
            elif os.name == 'posix':  # macOS/Linux
                os.system(f'open "{original_path.parent}"')
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aprire la cartella:\n{str(e)}")
    
    def delete_duplicates(self):
        """Sposta tutti i duplicati nel cestino mantenendo solo l'originale."""
        duplicates = [path for i, path in enumerate(self.paths) if i != self.original_idx]
        
        if not duplicates:
            messagebox.showinfo("Info", "Non ci sono duplicati da spostare.")
            return
        
        total_space = sum(path.stat().st_size for path in duplicates)
        
        message = (f"� SPOSTA DUPLICATI NEL CESTINO\n\n"
                  f"File da spostare: {len(duplicates)}\n"
                  f"Dimensione totale: {total_space/1024/1024:.1f} MB\n\n"
                  f"ORIGINALE DA MANTENERE:\n"
                  f"⭐ {self.paths[self.original_idx].name}\n\n"
                  f"DUPLICATI DA SPOSTARE:\n")
        
        for dup in duplicates[:3]:  # Mostra solo i primi 3
            message += f"� {dup.name}\n"
        if len(duplicates) > 3:
            message += f"... e altri {len(duplicates) - 3} file\n"
        
        message += f"\n💡 I file verranno spostati nel cestino temporaneo.\nProcedere?"
        
        if messagebox.askyesno("Conferma Spostamento", message):
            moved = 0
            errors = []
            
            # Trova l'istanza della GUI principale per accedere ai metodi di gestione cestino
            root_widget = self.parent
            while hasattr(root_widget, 'master') and root_widget.master:
                root_widget = root_widget.master
            
            # Cerca l'istanza DuplicateFinderGUI
            gui_instance = None
            for child in root_widget.children.values():
                if hasattr(child, 'move_to_garbage'):
                    gui_instance = child
                    break
            
            if gui_instance:
                # Crea cartella garbage se necessario
                if not gui_instance.garbage_folder:
                    gui_instance.create_garbage_folder()
                
                for dup_path in duplicates:
                    try:
                        if gui_instance.move_to_garbage(dup_path):
                            moved += 1
                        else:
                            errors.append(f"{dup_path.name}: Errore nello spostamento")
                    except Exception as e:
                        errors.append(f"{dup_path.name}: {str(e)}")
            else:
                # Fallback: eliminazione normale se non trova la GUI
                for dup_path in duplicates:
                    try:
                        os.remove(dup_path)
                        moved += 1
                    except Exception as e:
                        errors.append(f"{dup_path.name}: {str(e)}")
            
            if errors:
                messagebox.showerror("Spostamento Parziale",
                                   f"Spostati {moved}/{len(duplicates)} file.\n\n"
                                   f"Errori:\n" + "\n".join(errors[:3]))
            else:
                messagebox.showinfo("Successo",
                                   f"✅ Spostati {moved} duplicati nel cestino!\n"
                                   f"Dimensione spostata: {total_space/1024/1024:.1f} MB")
                self.window.destroy()

def main():
    """Avvia l'interfaccia grafica."""
    root = tk.Tk()
    app = DuplicateFinderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
