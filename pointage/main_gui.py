# =============================================================================
# FICHIER: main_gui.py - Interface graphique principale
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import threading
import os
from database import DatabaseManager
from fingerprint_manager import FingerprintManager
from excel_generator import ExcelGenerator

class PointageApp:
    """Application principale de pointage"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Application de Pointage - Empreintes Digitales")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialisation des composants
        self.db = DatabaseManager()
        self.fingerprint_manager = FingerprintManager()
        self.excel_generator = ExcelGenerator()
        
        # Variables
        self.current_reunion = None
        self.participants_var = tk.StringVar()
        
        # Interface
        self.setup_gui()
        self.fingerprint_manager.check_device()
    
    def setup_gui(self):
        """Configure l'interface graphique"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration du grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Titre
        title_label = ttk.Label(main_frame, text="SYSTÈME DE POINTAGE PAR EMPREINTES", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Onglets
        self.setup_membres_tab()
        self.setup_reunions_tab()
        self.setup_pointage_tab()
        self.setup_rapports_tab()
    
    def setup_membres_tab(self):
        """Configure l'onglet de gestion des membres"""
        membres_frame = ttk.Frame(self.notebook)
        self.notebook.add(membres_frame, text="Gestion des Membres")
        
        # Frame de formulaire
        form_frame = ttk.LabelFrame(membres_frame, text="Ajouter/Modifier un membre", padding="10")
        form_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Champs du formulaire
        fields = [
            ("Titre:", "titre_var"),
            ("Nom:", "nom_var"),
            ("Prénom:", "prenom_var"),
            ("Service:", "service_var"),
            ("Email:", "email_var"),
            ("Téléphone:", "telephone_var")
        ]
        
        self.membre_vars = {}
        for i, (label, var_name) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            var = tk.StringVar()
            self.membre_vars[var_name] = var
            if var_name == "titre_var":
                combo = ttk.Combobox(form_frame, textvariable=var, values=["M.", "Mme", "Dr.", "Pr."])
                combo.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
            else:
                entry = ttk.Entry(form_frame, textvariable=var)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        form_frame.columnconfigure(1, weight=1)
        
        # Boutons de gestion des empreintes
        fingerprint_frame = ttk.Frame(form_frame)
        fingerprint_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        
        ttk.Button(fingerprint_frame, text="Capturer Empreinte", 
                  command=self.capture_empreinte_membre).pack(side=tk.LEFT, padx=5)
        
        self.fingerprint_status = ttk.Label(fingerprint_frame, text="Aucune empreinte capturée", 
                                          foreground="red")
        self.fingerprint_status.pack(side=tk.LEFT, padx=10)
        
        # Boutons d'action
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)
        
        ttk.Button(buttons_frame, text="Ajouter Membre", 
                  command=self.ajouter_membre).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Modifier Membre", 
                  command=self.modifier_membre).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Effacer Formulaire", 
                  command=self.effacer_formulaire_membre).pack(side=tk.LEFT, padx=5)
        
        # Liste des membres
        list_frame = ttk.LabelFrame(membres_frame, text="Liste des membres", padding="10")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                       padx=5, pady=5)
        
        # Treeview pour la liste
        columns = ('Titre', 'Nom', 'Prénom', 'Service', 'Email', 'Téléphone')
        self.membres_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.membres_tree.heading(col, text=col)
            self.membres_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar_membres = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.membres_tree.yview)
        self.membres_tree.configure(yscrollcommand=scrollbar_membres.set)
        
        self.membres_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_membres.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Événement de sélection
        self.membres_tree.bind('<<TreeviewSelect>>', self.on_membre_select)
        
        # Configuration du grid
        membres_frame.columnconfigure(0, weight=1)
        membres_frame.rowconfigure(1, weight=1)
        
        # Variables pour l'empreinte en cours
        self.current_fingerprint_data = None
        self.current_fingerprint_hash = None
        self.selected_membre_id = None
        
        # Charger les membres
        self.refresh_membres_list()
    
    def setup_reunions_tab(self):
        """Configure l'onglet de gestion des réunions"""
        reunions_frame = ttk.Frame(self.notebook)
        self.notebook.add(reunions_frame, text="Gestion des Réunions")
        
        # Frame de création de réunion
        create_frame = ttk.LabelFrame(reunions_frame, text="Créer une nouvelle réunion", padding="10")
        create_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Champs de la réunion
        ttk.Label(create_frame, text="Titre de la réunion:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.reunion_titre_var = tk.StringVar()
        ttk.Entry(create_frame, textvariable=self.reunion_titre_var, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        ttk.Label(create_frame, text="Lieu:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.reunion_lieu_var = tk.StringVar()
        ttk.Entry(create_frame, textvariable=self.reunion_lieu_var, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        ttk.Label(create_frame, text="Date et heure:").grid(row=2, column=0, sticky=tk.W, pady=2)
        date_frame = ttk.Frame(create_frame)
        date_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        self.reunion_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.reunion_heure_var = tk.StringVar(value=datetime.now().strftime('%H:%M'))
        
        ttk.Entry(date_frame, textvariable=self.reunion_date_var, width=12).pack(side=tk.LEFT)
        ttk.Label(date_frame, text="à").pack(side=tk.LEFT, padx=5)
        ttk.Entry(date_frame, textvariable=self.reunion_heure_var, width=8).pack(side=tk.LEFT)
        
        create_frame.columnconfigure(1, weight=1)
        
        # Bouton de création
        ttk.Button(create_frame, text="Créer la Réunion", 
                  command=self.creer_reunion).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Liste des réunions
        list_frame = ttk.LabelFrame(reunions_frame, text="Liste des réunions", padding="10")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                       padx=5, pady=5)
        
        # Treeview pour les réunions
        columns = ('ID', 'Titre', 'Lieu', 'Date', 'Statut')
        self.reunions_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.reunions_tree.heading(col, text=col)
            if col == 'ID':
                self.reunions_tree.column(col, width=50)
            else:
                self.reunions_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar_reunions = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.reunions_tree.yview)
        self.reunions_tree.configure(yscrollcommand=scrollbar_reunions.set)
        
        self.reunions_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_reunions.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Configuration du grid
        reunions_frame.columnconfigure(0, weight=1)
        reunions_frame.rowconfigure(1, weight=1)
        
        # Charger les réunions
        self.refresh_reunions_list()
    
    def setup_pointage_tab(self):
        """Configure l'onglet de pointage"""
        pointage_frame = ttk.Frame(self.notebook)
        self.notebook.add(pointage_frame, text="Pointage")
        
        # Frame de sélection de réunion
        select_frame = ttk.LabelFrame(pointage_frame, text="Sélection de la réunion", padding="10")
        select_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(select_frame, text="Réunion active:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.reunion_combo = ttk.Combobox(select_frame, state="readonly", width=60)
        self.reunion_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        self.reunion_combo.bind('<<ComboboxSelected>>', self.on_reunion_selected)
        
        ttk.Button(select_frame, text="Actualiser", 
                  command=self.refresh_reunion_combo).grid(row=0, column=2, padx=5)
        
        select_frame.columnconfigure(1, weight=1)
        
        # Frame de pointage
        scan_frame = ttk.LabelFrame(pointage_frame, text="Scanner l'empreinte", padding="10")
        scan_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Status du lecteur
        self.device_status = ttk.Label(scan_frame, text="Lecteur d'empreintes: Connecté", 
                                      foreground="green", font=('Arial', 10, 'bold'))
        self.device_status.pack(pady=10)
        
        # Instructions
        instructions = """
Instructions:
1. Sélectionnez une réunion active
2. Placez votre doigt sur le lecteur d'empreintes
3. Cliquez sur "Scanner Empreinte"
4. Vérifiez les informations affichées
5. Confirmez le pointage
        """
        ttk.Label(scan_frame, text=instructions, justify=tk.LEFT).pack(pady=10)
        
        # Bouton de scan
        scan_button = ttk.Button(scan_frame, text="Scanner Empreinte", 
                                command=self.scanner_empreinte, style='Accent.TButton')
        scan_button.pack(pady=10)
        
        # Zone de résultat
        self.result_frame = ttk.LabelFrame(scan_frame, text="Résultat de la reconnaissance", padding="10")
        self.result_frame.pack(fill=tk.X, pady=10)
        
        self.result_text = tk.Text(self.result_frame, height=6, width=40, state=tk.DISABLED)
        self.result_text.pack(fill=tk.X)
        
        # Bouton de confirmation
        self.confirm_button = ttk.Button(scan_frame, text="Confirmer le Pointage", 
                                        command=self.confirmer_pointage, state=tk.DISABLED)
        self.confirm_button.pack(pady=10)
        
        # Frame des participants
        participants_frame = ttk.LabelFrame(pointage_frame, text="Participants présents", padding="10")
        participants_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Compteur
        self.count_label = ttk.Label(participants_frame, text="Participants: 0", 
                                    font=('Arial', 12, 'bold'))
        self.count_label.pack(pady=5)
        
        # Liste des participants
        self.participants_listbox = tk.Listbox(participants_frame, height=15)
        scrollbar_participants = ttk.Scrollbar(participants_frame, orient=tk.VERTICAL, 
                                             command=self.participants_listbox.yview)
        self.participants_listbox.configure(yscrollcommand=scrollbar_participants.set)
        
        self.participants_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_participants.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Boutons de gestion
        buttons_frame = ttk.Frame(participants_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(buttons_frame, text="Actualiser Liste", 
                  command=self.refresh_participants_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Terminer Réunion", 
                  command=self.terminer_reunion).pack(side=tk.RIGHT, padx=5)
        
        # Configuration du grid
        pointage_frame.columnconfigure(0, weight=1)
        pointage_frame.columnconfigure(1, weight=1)
        pointage_frame.rowconfigure(1, weight=1)
        
        # Variables pour le pointage
        self.scanned_membre = None
        self.refresh_reunion_combo()
    
    def setup_rapports_tab(self):
        """Configure l'onglet des rapports"""
        rapports_frame = ttk.Frame(self.notebook)
        self.notebook.add(rapports_frame, text="Rapports")
        
        # Frame de sélection
        select_frame = ttk.LabelFrame(rapports_frame, text="Génération de rapport", padding="10")
        select_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(select_frame, text="Sélectionner une réunion:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.rapport_combo = ttk.Combobox(select_frame, state="readonly", width=60)
        self.rapport_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        ttk.Button(select_frame, text="Actualiser", 
                  command=self.refresh_rapport_combo).grid(row=0, column=2, padx=5)
        
        select_frame.columnconfigure(1, weight=1)
        
        # Boutons d'action
        actions_frame = ttk.Frame(select_frame)
        actions_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(actions_frame, text="Prévisualiser", 
                  command=self.previsualiser_rapport).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Générer Excel", 
                  command=self.generer_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Ouvrir Dossier", 
                  command=self.ouvrir_dossier_rapports).pack(side=tk.LEFT, padx=5)
        
        # Frame de prévisualisation
        preview_frame = ttk.LabelFrame(rapports_frame, text="Prévisualisation", padding="10")
        preview_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                          padx=5, pady=5)
        
        # Treeview pour la prévisualisation
        columns = ('Titre', 'Nom', 'Prénom', 'Service', 'Email', 'Téléphone', 'Heure')
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.preview_tree.heading(col, text=col)
            if col == 'Heure':
                self.preview_tree.column(col, width=120)
            else:
                self.preview_tree.column(col, width=130)
        
        # Scrollbars
        scrollbar_preview_v = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        scrollbar_preview_h = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.preview_tree.xview)
        self.preview_tree.configure(yscrollcommand=scrollbar_preview_v.set, xscrollcommand=scrollbar_preview_h.set)
        
        self.preview_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_preview_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_preview_h.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # Configuration du grid
        rapports_frame.columnconfigure(0, weight=1)
        rapports_frame.rowconfigure(1, weight=1)
        
        # Charger les réunions pour rapports
        self.refresh_rapport_combo()
    
    # =============================================================================
    # MÉTHODES DE GESTION DES MEMBRES
    # =============================================================================
    
    def capture_empreinte_membre(self):
        """Capture l'empreinte pour un nouveau membre"""
        def capture_thread():
            try:
                result = self.fingerprint_manager.capture_fingerprint()
                if result:
                    self.current_fingerprint_data, self.current_fingerprint_hash = result
                    self.root.after(0, lambda: self.fingerprint_status.config(
                        text="Empreinte capturée avec succès", foreground="green"))
                else:
                    self.root.after(0, lambda: self.fingerprint_status.config(
                        text="Erreur lors de la capture", foreground="red"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Erreur", f"Erreur de capture: {e}"))
        
        self.fingerprint_status.config(text="Capture en cours...", foreground="orange")
        threading.Thread(target=capture_thread, daemon=True).start()
    
    def ajouter_membre(self):
        """Ajoute un nouveau membre"""
        # Validation des champs
        if not all([self.membre_vars['nom_var'].get(), self.membre_vars['prenom_var'].get(),
                   self.membre_vars['email_var'].get(), self.membre_vars['service_var'].get()]):
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return
        
        if not self.current_fingerprint_hash:
            messagebox.showerror("Erreur", "Veuillez capturer une empreinte")
            return
        
        # Préparation des données
        membre_data = {
            'titre': self.membre_vars['titre_var'].get() or 'M.',
            'nom': self.membre_vars['nom_var'].get(),
            'prenom': self.membre_vars['prenom_var'].get(),
            'service': self.membre_vars['service_var'].get(),
            'email': self.membre_vars['email_var'].get(),
            'telephone': self.membre_vars['telephone_var'].get(),
            'empreinte_data': self.current_fingerprint_data,
            'empreinte_hash': self.current_fingerprint_hash
        }
        
        # Ajout en base
        if self.db.add_membre(membre_data):
            messagebox.showinfo("Succès", "Membre ajouté avec succès")
            self.effacer_formulaire_membre()
            self.refresh_membres_list()
        else:
            messagebox.showerror("Erreur", "Erreur lors de l'ajout du membre")
    
    def modifier_membre(self):
        """Modifie un membre existant"""
        if not self.selected_membre_id:
            messagebox.showerror("Erreur", "Veuillez sélectionner un membre à modifier")
            return
        
        # Validation des champs
        if not all([self.membre_vars['nom_var'].get(), self.membre_vars['prenom_var'].get(),
                   self.membre_vars['email_var'].get(), self.membre_vars['service_var'].get()]):
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return
        
        # Préparation des données
        membre_data = {
            'titre': self.membre_vars['titre_var'].get() or 'M.',
            'nom': self.membre_vars['nom_var'].get(),
            'prenom': self.membre_vars['prenom_var'].get(),
            'service': self.membre_vars['service_var'].get(),
            'email': self.membre_vars['email_var'].get(),
            'telephone': self.membre_vars['telephone_var'].get()
        }
        
        # Modification en base
        if self.db.update_membre(self.selected_membre_id, membre_data):
            messagebox.showinfo("Succès", "Membre modifié avec succès")
            self.effacer_formulaire_membre()
            self.refresh_membres_list()
        else:
            messagebox.showerror("Erreur", "Erreur lors de la modification du membre")
    
    def effacer_formulaire_membre(self):
        """Efface le formulaire de membre"""
        for var in self.membre_vars.values():
            var.set("")
        self.current_fingerprint_data = None
        self.current_fingerprint_hash = None
        self.selected_membre_id = None
        self.fingerprint_status.config(text="Aucune empreinte capturée", foreground="red")
    
    def on_membre_select(self, event):
        """Gère la sélection d'un membre dans la liste"""
        selection = self.membres_tree.selection()
        if selection:
            item = self.membres_tree.item(selection[0])
            values = item['values']
            
            # Récupération de l'ID depuis la base
            membres = self.db.get_all_membres()
            for membre in membres:
                if (membre['nom'] == values[1] and membre['prenom'] == values[2] and 
                    membre['email'] == values[4]):
                    self.selected_membre_id = membre['id_empreinte']
                    
                    # Remplissage du formulaire
                    self.membre_vars['titre_var'].set(values[0])
                    self.membre_vars['nom_var'].set(values[1])
                    self.membre_vars['prenom_var'].set(values[2])
                    self.membre_vars['service_var'].set(values[3])
                    self.membre_vars['email_var'].set(values[4])
                    self.membre_vars['telephone_var'].set(values[5])
                    break
    
    def refresh_membres_list(self):
        """Actualise la liste des membres"""
        # Vider la liste
        for item in self.membres_tree.get_children():
            self.membres_tree.delete(item)
        
        # Recharger les membres
        membres = self.db.get_all_membres()
        for membre in membres:
            self.membres_tree.insert('', 'end', values=(
                membre['titre'], membre['nom'], membre['prenom'],
                membre['service'], membre['email'], membre['telephone']
            ))
    
    # =============================================================================
    # MÉTHODES DE GESTION DES RÉUNIONS
    # =============================================================================
    
    def creer_reunion(self):
        """Crée une nouvelle réunion"""
        # Validation
        if not all([self.reunion_titre_var.get(), self.reunion_lieu_var.get()]):
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        try:
            # Formation de la date complète
            date_str = f"{self.reunion_date_var.get()} {self.reunion_heure_var.get()}"
            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
            
            reunion_data = {
                'titre': self.reunion_titre_var.get(),
                'lieu': self.reunion_lieu_var.get(),
                'date': date_obj.isoformat()
            }
            
            reunion_id = self.db.create_reunion(reunion_data)
            if reunion_id:
                messagebox.showinfo("Succès", f"Réunion créée avec l'ID: {reunion_id}")
                
                # Effacer le formulaire
                self.reunion_titre_var.set("")
                self.reunion_lieu_var.set("")
                self.reunion_date_var.set(datetime.now().strftime('%Y-%m-%d'))
                self.reunion_heure_var.set(datetime.now().strftime('%H:%M'))
                
                # Actualiser les listes
                self.refresh_reunions_list()
                self.refresh_reunion_combo()
                self.refresh_rapport_combo()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la création de la réunion")
                
        except ValueError:
            messagebox.showerror("Erreur", "Format de date/heure invalide")
    
    def refresh_reunions_list(self):
        """Actualise la liste des réunions"""
        # Vider la liste
        for item in self.reunions_tree.get_children():
            self.reunions_tree.delete(item)
        
        # Recharger les réunions
        reunions = self.db.get_reunions()
        for reunion in reunions:
            # Formatage de la date
            try:
                date_obj = datetime.fromisoformat(reunion['date'])
                date_formatted = date_obj.strftime('%d/%m/%Y %H:%M')
            except:
                date_formatted = reunion['date']
            
            self.reunions_tree.insert('', 'end', values=(
                reunion['id_reunion'], reunion['titre'], reunion['lieu'],
                date_formatted, reunion['statut']
            ))
    
    # =============================================================================
    # MÉTHODES DE POINTAGE
    # =============================================================================
    
    def refresh_reunion_combo(self):
        """Actualise la combobox des réunions pour le pointage"""
        reunions = self.db.get_reunions()
        reunion_list = []
        for reunion in reunions:
            if reunion['statut'] in ['planifiee', 'en_cours']:
                try:
                    date_obj = datetime.fromisoformat(reunion['date'])
                    date_str = date_obj.strftime('%d/%m/%Y %H:%M')
                except:
                    date_str = reunion['date']
                
                reunion_text = f"{reunion['id_reunion']} - {reunion['titre']} ({date_str})"
                reunion_list.append(reunion_text)
        
        self.reunion_combo['values'] = reunion_list
        if reunion_list and not self.reunion_combo.get():
            self.reunion_combo.set(reunion_list[0])
    
    def on_reunion_selected(self, event):
        """Gère la sélection d'une réunion pour le pointage"""
        selection = self.reunion_combo.get()
        if selection:
            # Extraction de l'ID de la réunion
            self.current_reunion = int(selection.split(' - ')[0])
            self.refresh_participants_list()
    
    def scanner_empreinte(self):
        """Scanner une empreinte pour le pointage"""
        if not self.current_reunion:
            messagebox.showerror("Erreur", "Veuillez sélectionner une réunion")
            return
        
        def scan_thread():
            try:
                # Mise à jour de l'interface
                self.root.after(0, lambda: self.update_result_text("Scan en cours...\n"))
                
                # Capture de l'empreinte
                result = self.fingerprint_manager.capture_fingerprint()
                if not result:
                    self.root.after(0, lambda: self.update_result_text("Erreur lors de la capture\n"))
                    return
                
                fingerprint_data, fingerprint_hash = result
                
                # Recherche de correspondance
                self.root.after(0, lambda: self.update_result_text("Recherche de correspondance...\n"))
                
                membre = self.db.find_membre_by_fingerprint(fingerprint_hash)
                
                if membre:
                    self.scanned_membre = membre
                    result_text = f"""Membre identifié:
{membre['titre']} {membre['nom']} {membre['prenom']}
Service: {membre['service']}
Email: {membre['email']}
Téléphone: {membre['telephone']}

Empreinte reconnue avec succès!
"""
                    self.root.after(0, lambda: self.update_result_text(result_text))
                    self.root.after(0, lambda: self.confirm_button.config(state=tk.NORMAL))
                else:
                    self.root.after(0, lambda: self.update_result_text("Aucune correspondance trouvée.\nEmpreinte non reconnue."))
                    self.scanned_membre = None
                    self.root.after(0, lambda: self.confirm_button.config(state=tk.DISABLED))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Erreur", f"Erreur lors du scan: {e}"))
        
        # Démarrer le scan dans un thread séparé
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def update_result_text(self, text):
        """Met à jour le texte de résultat"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, text)
        self.result_text.config(state=tk.DISABLED)
    
    def confirmer_pointage(self):
        """Confirme le pointage du membre scanné"""
        if not self.scanned_membre or not self.current_reunion:
            return
        
        # Enregistrement de la participation
        if self.db.add_participation(self.current_reunion, self.scanned_membre['id_empreinte']):
            messagebox.showinfo("Succès", f"Pointage confirmé pour {self.scanned_membre['prenom']} {self.scanned_membre['nom']}")
            
            # Réinitialisation
            self.scanned_membre = None
            self.confirm_button.config(state=tk.DISABLED)
            self.update_result_text("Prêt pour un nouveau scan...")
            
            # Actualisation de la liste des participants
            self.refresh_participants_list()
        else:
            messagebox.showwarning("Attention", "Ce membre est déjà pointé pour cette réunion")
    
    def refresh_participants_list(self):
        """Actualise la liste des participants"""
        if not self.current_reunion:
            return
        
        # Vider la liste
        self.participants_listbox.delete(0, tk.END)
        
        # Récupérer les participants
        participants = self.db.get_participants(self.current_reunion)
        
        # Mettre à jour le compteur
        self.count_label.config(text=f"Participants: {len(participants)}")
        
        # Ajouter les participants à la liste
        for participant in participants:
            try:
                heure_obj = datetime.fromisoformat(participant['heure_pointage'])
                heure_str = heure_obj.strftime('%H:%M:%S')
            except:
                heure_str = participant['heure_pointage']
            
            participant_text = f"{heure_str} - {participant['prenom']} {participant['nom']} ({participant['service']})"
            self.participants_listbox.insert(tk.END, participant_text)
    
    def terminer_reunion(self):
        """Termine la réunion en cours"""
        if not self.current_reunion:
            messagebox.showerror("Erreur", "Aucune réunion sélectionnée")
            return
        
        if messagebox.askyesno("Confirmation", "Voulez-vous terminer cette réunion?"):
            if self.db.update_reunion_status(self.current_reunion, 'terminee'):
                messagebox.showinfo("Succès", "Réunion terminée")
                self.refresh_reunion_combo()
                self.refresh_reunions_list()
                self.refresh_rapport_combo()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la mise à jour")
    
    # =============================================================================
    # MÉTHODES DE GÉNÉRATION DES RAPPORTS
    # =============================================================================
    
    def refresh_rapport_combo(self):
        """Actualise la combobox des réunions pour les rapports"""
        reunions = self.db.get_reunions()
        reunion_list = []
        for reunion in reunions:
            try:
                date_obj = datetime.fromisoformat(reunion['date'])
                date_str = date_obj.strftime('%d/%m/%Y %H:%M')
            except:
                date_str = reunion['date']
            
            reunion_text = f"{reunion['id_reunion']} - {reunion['titre']} ({date_str}) - {reunion['statut']}"
            reunion_list.append(reunion_text)
        
        self.rapport_combo['values'] = reunion_list
    
    def previsualiser_rapport(self):
        """Prévisualise le rapport de la réunion sélectionnée"""
        selection = self.rapport_combo.get()
        if not selection:
            messagebox.showerror("Erreur", "Veuillez sélectionner une réunion")
            return
        
        # Extraction de l'ID de la réunion
        reunion_id = int(selection.split(' - ')[0])
        
        # Vider le treeview
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        # Récupérer les participants
        participants = self.db.get_participants(reunion_id)
        
        # Ajouter les participants au treeview
        for participant in participants:
            try:
                heure_obj = datetime.fromisoformat(participant['heure_pointage'])
                heure_str = heure_obj.strftime('%d/%m/%Y %H:%M:%S')
            except:
                heure_str = participant['heure_pointage']
            
            self.preview_tree.insert('', 'end', values=(
                participant['titre'], participant['nom'], participant['prenom'],
                participant['service'], participant['email'], participant['telephone'],
                heure_str
            ))
    
    def generer_excel(self):
        """Génère le fichier Excel"""
        selection = self.rapport_combo.get()
        if not selection:
            messagebox.showerror("Erreur", "Veuillez sélectionner une réunion")
            return
        
        # Extraction de l'ID de la réunion
        reunion_id = int(selection.split(' - ')[0])
        
        # Récupération des données
        reunions = self.db.get_reunions()
        reunion_info = None
        for reunion in reunions:
            if reunion['id_reunion'] == reunion_id:
                reunion_info = reunion
                break
        
        if not reunion_info:
            messagebox.showerror("Erreur", "Réunion non trouvée")
            return
        
        participants = self.db.get_participants(reunion_id)
        
        # Génération du nom de fichier
        filename = self.excel_generator.get_default_filename(reunion_info['titre'])
        
        # Boîte de dialogue pour sauvegarder
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialvalue=filename
        )
        
        if filepath:
            # Génération du fichier
            if self.excel_generator.generate_rapport_reunion(reunion_info, participants, filepath):
                messagebox.showinfo("Succès", f"Rapport généré avec succès:\n{filepath}")
                
                # Proposer d'ouvrir le fichier
                if messagebox.askyesno("Ouvrir", "Souhaitez-vous ouvrir le fichier?"):
                    try:
                        os.startfile(filepath)  # Windows
                    except:
                        try:
                            os.system(f"open '{filepath}'")  # macOS
                        except:
                            os.system(f"xdg-open '{filepath}'")  # Linux
            else:
                messagebox.showerror("Erreur", "Erreur lors de la génération du rapport")
    
    def ouvrir_dossier_rapports(self):
        """Ouvre le dossier des rapports"""
        try:
            os.startfile(os.getcwd())  # Windows
        except:
            try:
                os.system(f"open '{os.getcwd()}'")  # macOS
            except:
                os.system(f"xdg-open '{os.getcwd()}'")  # Linux
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()


# =============================================================================
# POINT D'ENTRÉE PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    # Vérification et installation des dépendances
    def check_dependencies():
        """Vérifie la présence des modules requis"""
        required_modules = [
            ('tkinter', 'Interface graphique'),
            ('sqlite3', 'Base de données'),
            ('PIL', 'Traitement d\'images - pip install Pillow'),
            ('openpyxl', 'Génération Excel - pip install openpyxl')
        ]
        
        missing_modules = []
        for module, description in required_modules:
            try:
                if module == 'PIL':
                    import PIL
                elif module == 'openpyxl':
                    import openpyxl
                else:
                    __import__(module)
            except ImportError:
                missing_modules.append((module, description))
        
        if missing_modules:
            print("MODULES MANQUANTS:")
            for module, desc in missing_modules:
                print(f"- {desc}")
            print("\nPour installer les modules manquants:")
            print("pip install Pillow openpyxl")
            return False
        return True
    
    # Vérifier les dépendances
    if not check_dependencies():
        input("Appuyez sur Entrée pour quitter...")
        exit(1)
    
    try:
        # Création et lancement de l'application
        print("Initialisation de l'application de pointage...")
        app = PointageApp()
        print("Application prête. Interface graphique en cours de chargement...")
        app.run()
    except Exception as e:
        print(f"Erreur lors du lancement de l'application: {e}")
        input("Appuyez sur Entrée pour quitter...")

