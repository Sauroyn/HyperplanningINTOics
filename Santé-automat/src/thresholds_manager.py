"""
Module de gestion des seuils de référence.
"""
import os
import json
import pandas as pd
from config import THRESHOLDS_FILE


class ThresholdsManager:
    """Gestionnaire des seuils de référence pour les paramètres biologiques."""
    
    def __init__(self):
        self.thresholds = self.load_thresholds()
    
    def load_thresholds(self):
        """Charge les seuils depuis le fichier de configuration."""
        thresholds = {}
        if not THRESHOLDS_FILE or not os.path.exists(THRESHOLDS_FILE):
            return thresholds
        
        _, ext = os.path.splitext(THRESHOLDS_FILE)
        try:
            if ext.lower() in [".json"]:
                with open(THRESHOLDS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # normaliser {param: {min: x, max: y}}
                for k, v in data.items():
                    try:
                        thresholds[k] = {
                            "min": None if v.get("min") is None else float(str(v.get("min")).replace(",", ".")),
                            "max": None if v.get("max") is None else float(str(v.get("max")).replace(",", ".")),
                        }
                    except Exception:
                        continue
            elif ext.lower() in [".xlsx", ".xlsm", ".xltx", ".xltm"]:
                df_thresh = pd.read_excel(THRESHOLDS_FILE, engine="openpyxl")
                for _, row in df_thresh.iterrows():
                    try:
                        pname = str(row["Paramètre"]) if "Paramètre" in row else None
                        if not pname:
                            continue
                        vmin = row["min"] if "min" in row else None
                        vmax = row["max"] if "max" in row else None
                        thresholds[pname] = {
                            "min": None if vmin is None or pd.isna(vmin) else float(vmin),
                            "max": None if vmax is None or pd.isna(vmax) else float(vmax),
                        }
                    except Exception:
                        continue
            else:
                print(f"[WARN] Extension de THRESHOLDS_FILE non supportée: {ext}")
        except Exception as e:
            print(f"[WARN] Impossible de lire THRESHOLDS_FILE : {e}")
        
        return thresholds
    
    def save_thresholds(self, thresholds=None):
        """Sauvegarde les seuils dans le fichier de configuration."""
        if thresholds is not None:
            self.thresholds = thresholds
        
        if not THRESHOLDS_FILE:
            return
        
        os.makedirs(os.path.dirname(THRESHOLDS_FILE) or ".", exist_ok=True)
        _, ext = os.path.splitext(THRESHOLDS_FILE)
        try:
            if ext.lower() == ".json":
                with open(THRESHOLDS_FILE, "w", encoding="utf-8") as f:
                    json.dump(self.thresholds, f, ensure_ascii=False, indent=2)
            else:
                # Sauvegarde JSON par défaut même si extension non-json
                with open(THRESHOLDS_FILE + ".json", "w", encoding="utf-8") as f:
                    json.dump(self.thresholds, f, ensure_ascii=False, indent=2)
                print(f"[INFO] Seuils enregistrés dans {THRESHOLDS_FILE + '.json'}")
        except Exception as e:
            print(f"[WARN] Échec d'enregistrement des seuils: {e}")
    
    def update_from_results(self, results):
        """Met à jour les seuils à partir des résultats extraits du PDF."""
        for param, info in results.items():
            if info.get("min") is not None and info.get("max") is not None:
                if param not in self.thresholds:
                    self.thresholds[param] = {"min": info["min"], "max": info["max"]}
    
    def get_threshold(self, param):
        """Récupère les seuils min/max pour un paramètre donné."""
        return self.thresholds.get(param, {"min": None, "max": None})
