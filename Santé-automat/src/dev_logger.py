"""
Module de logging pour le mode développement.
"""
import os
from datetime import datetime


class DevLogger:
    """Gestionnaire de logs pour le mode développement."""
    
    def __init__(self, enabled=False, log_file="dev.txt"):
        self.enabled = enabled
        self.log_file = log_file
        if self.enabled:
            # Initialiser le fichier avec un en-tête
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write(f"=== MODE DÉVELOPPEMENT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
    
    def log_separator(self, title):
        """Ajoute un séparateur avec titre."""
        if not self.enabled:
            return
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"  {title}\n")
            f.write(f"{'='*80}\n\n")
    
    def log_raw_text(self, pdf_name, raw_text):
        """Log le texte brut extrait du PDF."""
        if not self.enabled:
            return
        self.log_separator(f"TEXTE BRUT DU PDF: {pdf_name}")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(raw_text)
            f.write("\n\n")
    
    def log_extracted_date(self, pdf_name, date):
        """Log la date extraite."""
        if not self.enabled:
            return
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"Date extraite pour {pdf_name}: {date}\n\n")
    
    def log_filtered_results(self, pdf_name, results):
        """Log les résultats après filtrage."""
        if not self.enabled:
            return
        self.log_separator(f"RÉSULTATS FILTRÉS POUR: {pdf_name}")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"Nombre de paramètres retenus: {len(results)}\n\n")
            for param, info in results.items():
                f.write(f"• {param}:\n")
                f.write(f"    Valeur: {info['valeur']} {info['unité']}\n")
                if info['intervalle']:
                    f.write(f"    Intervalle: {info['intervalle']}\n")
                if info['min'] is not None and info['max'] is not None:
                    f.write(f"    Min: {info['min']}, Max: {info['max']}\n")
                f.write("\n")
            f.write("\n")
    
    def log_banlist_info(self, banlist):
        """Log les éléments de la banlist."""
        if not self.enabled:
            return
        self.log_separator("BANLIST CHARGÉE")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"Nombre d'éléments dans la banlist: {len(banlist)}\n\n")
            for item in banlist:
                f.write(f"  - {item}\n")
            f.write("\n")
    
    def log_message(self, message):
        """Log un message général."""
        if not self.enabled:
            return
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
