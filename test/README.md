pdf_to_text.py
=================

Petit script Python qui extrait le texte de tous les fichiers PDF présents dans le dossier `pdfs/` et écrit un fichier `.txt` pour chaque PDF.

Caractéristiques
- Ne traite que les fichiers situés dans le dossier `pdfs/` (non récursif).
- Si `something.txt` existe et n'est pas vide, le script ignore `something.pdf`.
- Utilise PyPDF2, puis pdfminer.six, puis la commande `pdftotext` en fallback.

Installation

1. Installer Python 3.8+.
2. Installer une des dépendances Python recommandées (ou installer `pdftotext` via le paquet du système):

```bash
pip install PyPDF2
# ou
pip install pdfminer.six
```

Sur Debian/Ubuntu, `pdftotext` vient du paquet `poppler-utils`:

```bash
sudo apt update && sudo apt install poppler-utils
```

Usage

Placez vos fichiers PDF dans le dossier `pdfs/` (créé automatiquement) puis lancez:

```bash
python3 pdf_to_text.py
```

Résultat: pour chaque `name.pdf` dans `pdfs/` un fichier `name.txt` sera créé (ou écrasé si vide).

Remarques
- Le script n'est volontairement pas récursif. Si vous voulez traiter des sous-dossiers, modifiez `pdf_dir.glob("**/*.pdf")`.
- Si vous souhaitez forcer la ré-extraction, supprimez le `.txt` correspondant avant d'exécuter le script.
