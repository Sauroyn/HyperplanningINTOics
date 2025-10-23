#!/bin/bash
# Script de vérification rapide de l'installation

# Aller dans le dossier parent du script
cd "$(dirname "$0")/.." || exit 1

# Détecter le Python à utiliser (venv si disponible, sinon système)
if [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
    echo "🔧 Utilisation de l'environnement virtuel (.venv)"
elif command -v python3 &> /dev/null; then
    PYTHON="python3"
    echo "🔧 Utilisation de Python système"
else
    echo "❌ Python non trouvé!"
    exit 1
fi

echo "🔍 Vérification de l'installation..."
echo ""

# Vérifier les modules
echo "📦 Modules Python:"
modules=("src/config.py" "src/dev_logger.py" "src/pdf_extractor.py" "src/thresholds_manager.py" "src/excel_manager.py" "main_new.py")
for module in "${modules[@]}"; do
    if [ -f "$module" ]; then
        echo "  ✅ $module"
    else
        echo "  ❌ $module - MANQUANT"
    fi
done
echo ""

# Vérifier la documentation
echo "📚 Documentation:"
docs=("docs/RECAP.md" "docs/ARCHITECTURE.md" "docs/STRUCTURE.md" "docs/MIGRATION.md")
for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "  ✅ $doc"
    else
        echo "  ❌ $doc - MANQUANT"
    fi
done
echo ""

# Vérifier Python
echo "🐍 Python:"
echo "  ✅ Python trouvé: $PYTHON"
$PYTHON --version | sed 's/^/     /'
echo ""

# Test d'import
echo "🧪 Test d'import des modules:"
$PYTHON -c "
import sys
import os
sys.path.insert(0, 'src')
try:
    import config
    import dev_logger
    import pdf_extractor
    import thresholds_manager
    import excel_manager
    print('  ✅ Tous les modules importés avec succès')
except Exception as e:
    print(f'  ❌ Erreur: {e}')
" 2>&1
echo ""

# Vérifier les dépendances
echo "📦 Dépendances Python:"
$PYTHON -c "
import sys
deps = [('pdfplumber', 'pdfplumber'), ('pandas', 'pandas'), ('openpyxl', 'openpyxl'), ('python-dotenv', 'dotenv')]
for name, module in deps:
    try:
        __import__(module)
        print(f'  ✅ {name}')
    except ImportError:
        print(f'  ⚠️  {name} - Non installé (pip install {name})')
" 2>&1
echo ""

# Résumé
echo "══════════════════════════════════════════════════"
echo "✨ Installation vérifiée !"
echo ""
echo "Pour utiliser le script:"
echo "  $ python main_new.py --dev"
echo ""
echo "Pour lire la documentation:"
echo "  $ cat RECAP.md"
echo "══════════════════════════════════════════════════"
