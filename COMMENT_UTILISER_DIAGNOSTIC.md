# 🎯 Comment utiliser le diagnostic - GUIDE SIMPLE

## ✅ Version FACILE (diagnostic_auto.py)

### **Étape 1: Mettez vos PDFs dans le dossier `liasse/`**

Placez vos fichiers PDF dans le dossier `liasse/` de votre projet:

```
Application-extraction-liasse-fiscale-v2/
├── liasse/
│   ├── ma_liasse.pdf          ← Mettez vos PDFs ici
│   ├── autre_liasse.pdf       ← Vous pouvez en mettre plusieurs
│   └── liasse_vierge.pdf
├── diagnostic_auto.py
└── ...
```

### **Étape 2: Dans PyCharm**

1. **Ouvrez** le fichier `diagnostic_auto.py` dans PyCharm
2. **Clic droit** sur le fichier
3. **Sélectionnez** "Run 'diagnostic_auto'"
4. **C'est tout!** 🎉

Le script va:
- Détecter automatiquement tous les PDFs dans `liasse/`
- Vous demander lequel analyser
- Afficher le diagnostic complet

### **Exemple de sortie:**

```
================================================================================
  🔍 DIAGNOSTIC AUTOMATIQUE - EXTRACTION DE LIASSES FISCALES
================================================================================

📂 Recherche de PDFs dans le dossier 'liasse/'...

✅ 2 fichier(s) PDF trouvé(s):
   - ma_liasse_2024.pdf
   - liasse_vierge.pdf

📋 Sélectionnez un fichier à analyser:
   1. ma_liasse_2024.pdf
   2. liasse_vierge.pdf
   0. Analyser TOUS les fichiers

Votre choix (0-2): 1

[... diagnostic complet s'affiche ...]
```

---

## 🔧 Version AVANCÉE (diagnostic_extraction.py)

Si vous voulez plus de contrôle, utilisez `diagnostic_extraction.py` avec un argument.

### **Dans PyCharm:**

1. **Clic droit** sur `diagnostic_extraction.py`
2. **Sélectionnez** "Modify Run Configuration..."
3. **Dans "Parameters"**, ajoutez: `liasse/votre_fichier.pdf`
4. **Cliquez** "OK"
5. **Run** le fichier

### **Dans le Terminal:**

```bash
# Ouvrir le terminal dans PyCharm (Alt+F12 ou View → Tool Windows → Terminal)
python diagnostic_extraction.py liasse/ma_liasse.pdf
```

---

## 📊 Que faire avec les résultats?

### **Si vous voulez sauvegarder les résultats:**

Dans le terminal PyCharm:

```bash
python diagnostic_auto.py > resultats_diagnostic.txt
```

Ou modifiez la configuration Run pour ajouter une redirection.

### **Comparer plusieurs liasses:**

```bash
python diagnostic_extraction.py liasse/liasse_A.pdf > diag_A.txt
python diagnostic_extraction.py liasse/liasse_B.pdf > diag_B.txt
```

Puis ouvrez `diag_A.txt` et `diag_B.txt` dans PyCharm pour comparer.

---

## ❓ Problèmes courants

### **Problème 1: "Aucun fichier PDF trouvé"**

✅ **Solution**: Vérifiez que vos PDFs sont bien dans le dossier `liasse/` à la racine du projet.

### **Problème 2: "Module not found"**

✅ **Solution**: Installez les dépendances:
```bash
pip install -r requirements.txt
```

### **Problème 3: Le script ne démarre pas**

✅ **Solution**: Vérifiez que vous utilisez le bon interpréteur Python dans PyCharm:
- File → Settings → Project → Python Interpreter
- Assurez-vous que pdfplumber, openpyxl sont installés

---

## 💡 Résumé RAPIDE

**Pour 99% des cas, utilisez `diagnostic_auto.py`:**

1. Mettez vos PDFs dans `liasse/`
2. Ouvrez `diagnostic_auto.py` dans PyCharm
3. Clic droit → Run
4. Sélectionnez le fichier à analyser
5. Lisez les résultats!

**C'est tout!** 🚀
