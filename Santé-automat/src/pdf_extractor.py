"""
Module d'extraction des données depuis les fichiers PDF.
"""
import os
import re
import pdfplumber
from config import PARAMS_WHITELIST, BANLIST_FILE


class PDFExtractor:
    """Extracteur de données médicales depuis les PDF."""
    
    def __init__(self, dev_logger=None):
        self.dev_logger = dev_logger
        self.banlist = self._load_banlist()
        if self.dev_logger:
            self.dev_logger.log_banlist_info(self.banlist)
    
    def _load_banlist(self):
        """Charge la liste des termes à exclure."""
        banlist = []
        if BANLIST_FILE and os.path.exists(BANLIST_FILE):
            try:
                with open(BANLIST_FILE, "r", encoding="utf-8") as f:
                    for raw in f:
                        s = raw.strip()
                        if not s or s.startswith("#"):
                            continue
                        banlist.append(s)
            except Exception:
                pass
        return banlist
    
    def extract_data_from_pdf(self, pdf_path):
        """
        Extrait les données d'un fichier PDF.
        
        Returns:
            tuple: (date, results_dict)
        """
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        
        # Log du texte brut en mode dev
        if self.dev_logger:
            self.dev_logger.log_raw_text(os.path.basename(pdf_path), text)
        
        # Extraction de la date de prélèvement
        date_match = re.search(r"Prélevé le (\d{2}[-−]\d{2}[-−]\d{4})", text)
        if date_match:
            date = date_match.group(1).replace("−", "-")
            text = text.split(date_match.group(0), 1)[1]  # texte après la date
        else:
            date = "inconnue"
        
        if self.dev_logger:
            self.dev_logger.log_extracted_date(os.path.basename(pdf_path), date)
        
        # Extraction des résultats
        results = self._parse_results(text)
        
        # Log des résultats filtrés en mode dev
        if self.dev_logger:
            self.dev_logger.log_filtered_results(os.path.basename(pdf_path), results)
        
        return date, results
    
    def _parse_results(self, text):
        """Parse le texte pour extraire les résultats médicaux."""
        results = {}
        pattern = re.compile(
            r"^\s*([A-Za-zÀ-ÿ\s\-\(\)/]+?)\s+([\d,\.]+)\s*([a-zA-Zµ%/]+)?\s*(?:\(([^)]+)\))?"
        )
        
        for line in text.split("\n"):
            line = line.strip()
            if not line or len(line) > 120:
                continue
            
            # 1) Essayer de parser les paramètres whitelistés (prioritaire sur banlist)
            parsed = False
            for param in PARAMS_WHITELIST:
                if line.startswith(param):
                    match = pattern.match(line)
                    if match:
                        val_str = match.group(2).replace(",", ".")
                        try:
                            value = float(val_str)
                            interval = match.group(4) or ""
                            low, high = None, None
                            if interval and "-" in interval:
                                parts = interval.replace("−", "-").split("-")
                                try:
                                    low = float(parts[0].replace(",", "."))
                                    high = float(parts[1].replace(",", "."))
                                except:
                                    pass
                            results[param] = {
                                "valeur": value,
                                "unité": match.group(3) or "",
                                "intervalle": interval,
                                "min": low,
                                "max": high
                            }
                            parsed = True
                        except ValueError:
                            pass
                    break  # ne pas matcher plusieurs fois
            if parsed:
                continue
            
            # 2) Si non-parsable et la ligne contient un élément banni (insensible à la casse), ignorer
            line_low = line.lower()
            if any(b.lower() in line_low for b in self.banlist):
                continue
        
        return results
