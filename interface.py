import streamlit as st
import tempfile
import shutil
from pathlib import Path
from main import extraire_un_pdf, creer_fichier_excel

# Configuration de la page
st.set_page_config(
    page_title="Extraction Liasse Fiscale",
    page_icon="📊",
    layout="wide"
)

# Titre principal
st.title("📊 Extraction Automatique de Liasses Fiscales")
st.markdown("---")

# Instructions
st.markdown("""
### 📋 Instructions
1. **Téléversez** vos fichiers PDF (liasses fiscales)
2. **Indiquez l'année** pour chaque fichier
3. **Cliquez** sur "Extraire les données"
4. **Téléchargez** le fichier Excel généré
""")

st.markdown("---")

# Zone de téléversement
st.subheader("📁 Téléversement des fichiers")
uploaded_files = st.file_uploader(
    "Déposez vos fichiers PDF ici",
    type=['pdf'],
    accept_multiple_files=True,
    help="Vous pouvez glisser-déposer plusieurs fichiers PDF"
)

# Si des fichiers sont uploadés
if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} fichier(s) téléversé(s)")
    
    st.markdown("---")
    st.subheader("📅 Attribution des années")
    
    # Créer un dictionnaire pour stocker les années
    fichiers_annees = {}
    
    # Créer une colonne pour chaque fichier
    cols = st.columns(min(len(uploaded_files), 3))
    
    for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx % 3]:
            st.markdown(f"**{uploaded_file.name}**")
            annee = st.text_input(
                "Année",
                value="",
                key=f"annee_{idx}",
                placeholder="Ex: 2023",
                help="Indiquez l'année de cet exercice fiscal"
            )
            fichiers_annees[uploaded_file.name] = {
                'file': uploaded_file,
                'annee': annee
            }
    
    st.markdown("---")
    
    # Nom du fichier de sortie
    st.subheader("📝 Nom du fichier Excel")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        nom_fichier_excel = st.text_input(
            "Nom du fichier de sortie (sans extension)",
            value="extraction_liasses_fiscales",
            help="Le fichier sera enregistré avec l'extension .xlsx automatiquement"
        )
    
    with col2:
        ajouter_date = st.checkbox(
            "Ajouter la date",
            value=False,
            help="Ajoute la date du jour au nom (ex: fichier_20251023.xlsx)"
        )
    
    # Aperçu du nom
    from datetime import datetime
    nom_apercu = nom_fichier_excel
    if ajouter_date:
        nom_apercu = f"{nom_fichier_excel}_{datetime.now().strftime('%Y%m%d')}"
    st.caption(f"📄 Aperçu : `{nom_apercu}.xlsx`")
    
    st.markdown("---")
    
    # Bouton d'extraction
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Extraire les données", type="primary", use_container_width=True):
            
            # Vérifier que toutes les années sont renseignées
            annees_manquantes = [nom for nom, data in fichiers_annees.items() if not data['annee']]
            
            if annees_manquantes:
                st.error(f"❌ Veuillez renseigner l'année pour : {', '.join(annees_manquantes)}")
            else:
                # Créer un dossier temporaire pour les PDFs
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    
                    # Barre de progression
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    donnees_par_annee = {}
                    total_files = len(fichiers_annees)
                    
                    # Traiter chaque fichier
                    for idx, (nom_fichier, data) in enumerate(fichiers_annees.items()):
                        status_text.text(f"⏳ Traitement de {nom_fichier}...")
                        
                        # Sauvegarder le fichier temporairement
                        temp_pdf_path = temp_path / nom_fichier
                        with open(temp_pdf_path, 'wb') as f:
                            f.write(data['file'].getbuffer())
                        
                        # Extraire les données
                        resultats = extraire_un_pdf(temp_pdf_path)
                        
                        if resultats:
                            annee = data['annee'].strip()
                            donnees_par_annee[annee] = resultats
                            st.success(f"✅ {nom_fichier} → Année {annee} : Extraction réussie")
                        else:
                            st.error(f"❌ {nom_fichier} : Échec de l'extraction")
                        
                        # Mise à jour de la barre de progression
                        progress_bar.progress((idx + 1) / total_files)
                    
                    status_text.text("📊 Génération du fichier Excel...")
                    
                    # Générer le fichier Excel si on a des données
                    if donnees_par_annee:
                        # Créer le fichier Excel
                        resultats_dir = Path("resultats")
                        resultats_dir.mkdir(exist_ok=True)
                        
                        nom_excel = resultats_dir / "extraction_multi_annees.xlsx"
                        creer_fichier_excel(donnees_par_annee, nom_excel)
                        
                        status_text.text("✅ Extraction terminée !")
                        progress_bar.progress(1.0)
                        
                        st.markdown("---")
                        st.success("🎉 Extraction réussie !")
                        
                        # Bouton de téléchargement
                        with open(nom_excel, 'rb') as f:
                            from datetime import datetime
                            
                            # Nettoyer le nom du fichier (enlever caractères spéciaux)
                            nom_propre = "".join(c for c in nom_fichier_excel if c.isalnum() or c in (' ', '-', '_')).strip()
                            if not nom_propre:
                                nom_propre = "extraction_liasses_fiscales"
                            
                            # Ajouter la date si demandé
                            if ajouter_date:
                                nom_propre = f"{nom_propre}_{datetime.now().strftime('%Y%m%d')}"
                            
                            st.download_button(
                                label="📥 Télécharger le fichier Excel",
                                data=f,
                                file_name=f"{nom_propre}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="primary",
                                use_container_width=True
                            )
                        
                        # Afficher un résumé
                        st.markdown("### 📈 Résumé")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Fichiers traités", len(donnees_par_annee))
                        
                        with col2:
                            annees = sorted(donnees_par_annee.keys())
                            st.metric("Années couvertes", f"{annees[0]} - {annees[-1]}")
                        
                        with col3:
                            st.metric("Onglets créés", "2")
                    
                    else:
                        status_text.text("❌ Aucune donnée extraite")
                        st.error("Aucun fichier n'a pu être traité avec succès.")

else:
    st.info("👆 Commencez par téléverser vos fichiers PDF")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>📊 Extraction Automatique de Liasses Fiscales v2.0</p>
    <p>Onglet 1 : Données brutes • Onglet 2 : Analyse financière avec ratios automatiques</p>
</div>
""", unsafe_allow_html=True)
