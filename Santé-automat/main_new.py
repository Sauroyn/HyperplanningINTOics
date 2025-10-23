"""
Script principal d'analyse des résultats médicaux.
Orchestre l'extraction des PDF, la mise à jour Excel et la génération de graphiques.
"""
import os
import sys
import argparse

# Ajouter le dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import PDF_FOLDER
from dev_logger import DevLogger
from pdf_extractor import PDFExtractor
from thresholds_manager import ThresholdsManager
from excel_manager import ExcelManager


def main():
    """Point d'entrée principal du script."""
    parser = argparse.ArgumentParser(
        description="Analyse des résultats médicaux depuis des fichiers PDF"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forcer la ré-extraction même si la date existe déjà"
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Mode développement: log le texte brut et les résultats filtrés dans dev.txt"
    )
    args = parser.parse_args()
    
    # Initialisation des composants
    dev_logger = DevLogger(enabled=args.dev)
    pdf_extractor = PDFExtractor(dev_logger=dev_logger)
    thresholds_manager = ThresholdsManager()
    excel_manager = ExcelManager()
    
    # Message de bienvenue
    if args.dev:
        print("[DEV MODE] Les détails d'extraction seront enregistrés dans dev.txt")
    
    # Traitement des fichiers PDF
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]
    
    if not pdf_files:
        print(f"[WARN] Aucun fichier PDF trouvé dans {PDF_FOLDER}")
        return
    
    print(f"[INFO] {len(pdf_files)} fichier(s) PDF à traiter")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(PDF_FOLDER, pdf_file)
        print(f"\n[INFO] Traitement de {pdf_file}...")
        
        # Extraction des données
        date, results = pdf_extractor.extract_data_from_pdf(pdf_path)
        
        # Mise à jour Excel
        excel_manager.update_excel(
            pdf_path, date, results, thresholds_manager, force=args.force
        )
    
    # Post-traitement: colorisation et graphiques
    print("\n[INFO] Colorisation des valeurs hors normes...")
    excel_manager.colorize_outliers(thresholds_manager)
    
    print("[INFO] Génération des graphiques...")
    excel_manager.insert_charts()
    
    print("\n[SUCCESS] Traitement terminé avec succès!")
    if args.dev:
        print(f"[DEV MODE] Consultez dev.txt pour les détails d'extraction")


if __name__ == "__main__":
    main()
