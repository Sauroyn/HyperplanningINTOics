#!/usr/bin/env python3
"""
Script de test pour vérifier que tous les modules fonctionnent correctement.
"""
import sys
import os

# Ajouter le dossier parent et src au path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

def test_imports():
    """Test que tous les modules peuvent être importés."""
    print("🧪 Test 1: Import des modules")
    print("─" * 50)
    
    modules = [
        "config",
        "dev_logger",
        "pdf_extractor",
        "thresholds_manager",
        "excel_manager"
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}.py")
        except Exception as e:
            print(f"  ❌ {module}.py - Erreur: {e}")
            return False
    
    print()
    return True


def test_config():
    """Test du module config."""
    print("🧪 Test 2: Configuration")
    print("─" * 50)
    
    try:
        from config import PDF_FOLDER, OUTPUT_FILE, THRESHOLDS_FILE, BANLIST_FILE, PARAMS_WHITELIST
        
        print(f"  ✅ PDF_FOLDER: {PDF_FOLDER}")
        print(f"  ✅ OUTPUT_FILE: {OUTPUT_FILE}")
        print(f"  ✅ THRESHOLDS_FILE: {THRESHOLDS_FILE}")
        print(f"  ✅ BANLIST_FILE: {BANLIST_FILE}")
        print(f"  ✅ PARAMS_WHITELIST: {len(PARAMS_WHITELIST)} paramètres")
        print()
        return True
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        print()
        return False


def test_dev_logger():
    """Test du module dev_logger."""
    print("🧪 Test 3: DevLogger")
    print("─" * 50)
    
    try:
        from dev_logger import DevLogger
        
        # Test en mode désactivé
        logger = DevLogger(enabled=False, log_file="test_dev.txt")
        logger.log_message("Ceci ne devrait pas être écrit")
        
        # Test en mode activé
        logger = DevLogger(enabled=True, log_file="test_dev.txt")
        logger.log_separator("TEST")
        logger.log_message("Message de test")
        
        # Vérifier que le fichier existe
        if os.path.exists("test_dev.txt"):
            print("  ✅ Fichier de log créé")
            os.remove("test_dev.txt")
            print("  ✅ Fichier de test nettoyé")
        else:
            print("  ❌ Fichier de log non créé")
            return False
        
        print()
        return True
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        print()
        return False


def test_pdf_extractor():
    """Test du module pdf_extractor."""
    print("🧪 Test 4: PDFExtractor")
    print("─" * 50)
    
    try:
        from pdf_extractor import PDFExtractor
        
        extractor = PDFExtractor()
        print(f"  ✅ PDFExtractor initialisé")
        print(f"  ✅ Banlist chargée: {len(extractor.banlist)} éléments")
        print()
        return True
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        print()
        return False


def test_thresholds_manager():
    """Test du module thresholds_manager."""
    print("🧪 Test 5: ThresholdsManager")
    print("─" * 50)
    
    try:
        from thresholds_manager import ThresholdsManager
        
        manager = ThresholdsManager()
        print(f"  ✅ ThresholdsManager initialisé")
        print(f"  ✅ Seuils chargés: {len(manager.thresholds)} paramètres")
        
        # Test de récupération d'un seuil
        if manager.thresholds:
            first_param = list(manager.thresholds.keys())[0]
            threshold = manager.get_threshold(first_param)
            print(f"  ✅ Exemple: {first_param} → min={threshold['min']}, max={threshold['max']}")
        
        print()
        return True
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        print()
        return False


def test_excel_manager():
    """Test du module excel_manager."""
    print("🧪 Test 6: ExcelManager")
    print("─" * 50)
    
    try:
        from excel_manager import ExcelManager
        
        manager = ExcelManager()
        print(f"  ✅ ExcelManager initialisé")
        print(f"  ✅ Fichier cible: {manager.output_file}")
        print()
        return True
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        print()
        return False


def test_file_structure():
    """Test de la structure des fichiers."""
    print("🧪 Test 7: Structure des fichiers")
    print("─" * 50)
    
    # Remonter au dossier parent
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    
    required_files = [
        "src/config.py",
        "src/dev_logger.py",
        "src/pdf_extractor.py",
        "src/thresholds_manager.py",
        "src/excel_manager.py",
        "main_new.py"
    ]
    
    all_exist = True
    for file in required_files:
        file_path = os.path.join(parent_dir, file)
        if os.path.exists(file_path):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MANQUANT")
            all_exist = False
    
    print()
    return all_exist


def main():
    """Fonction principale."""
    print()
    print("═" * 50)
    print("  TEST DES MODULES - Santé-automat")
    print("═" * 50)
    print()
    
    tests = [
        test_file_structure,
        test_imports,
        test_config,
        test_dev_logger,
        test_pdf_extractor,
        test_thresholds_manager,
        test_excel_manager
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
            results.append(False)
    
    # Résumé
    print("═" * 50)
    print("  RÉSUMÉ")
    print("═" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n  Tests réussis: {passed}/{total}")
    
    if passed == total:
        print("\n  ✅ Tous les tests sont passés!")
        print("  → Le script est prêt à être utilisé")
        print("\n  Utilisez: python main_new.py --dev")
        return 0
    else:
        print("\n  ⚠️  Certains tests ont échoué")
        print("  → Vérifiez les erreurs ci-dessus")
        return 1


if __name__ == "__main__":
    sys.exit(main())
