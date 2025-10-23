"""
Configuration et constantes pour le script d'analyse de santé.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Valeurs par défaut si .env n'est pas défini
PDF_FOLDER = os.getenv("PDF_FOLDER", "pdfs")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "resultats.xlsx")
THRESHOLDS_FILE = os.getenv("THRESHOLDS_FILE", "seuils.json")
BANLIST_FILE = os.getenv("BANLIST_FILE", "banlist.txt")

# Liste blanche des paramètres biologiques
PARAMS_WHITELIST = [
    "Hématies", "Hémoglobine", "Hématocrite", "V.G.M.", "T.C.M.H.",
    "C.C.M.H.", "Leucocytes", "Polynucléaires neutrophiles",
    "Polynucléaires éosinophiles", "Polynucléaires basophiles",
    "Lymphocytes", "Monocytes", "Plaquettes",
    "Créatinine", "Phosphatase alcaline", "ASAT (Transaminases TGO)",
    "ALAT (Transaminases TGP)", "GGT (Gamma Glutamyl Transpeptidase)",
    "FIB-4"
]
