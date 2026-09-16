

| Bachelor Data et IA — MD4 |
| :---- |
| **Dashboards & Data Visualisation** |
| **PROJET NOTÉ — Dashboard interactif (Streamlit)** |

# 

Date de rendu : jeudi 17 septembre 13h30

# **Contexte**

Vous allez concevoir un **dashboard interactif avec Streamlit**, à partir du dataset déjà utilisé pour votre projet d'Analyse Exploratoire de Données (AED). L'objectif n'est pas de refaire l'exploration, mais de choisir des messages à en tirer et de le restituer efficacement à une audience définie. Vous pouvez si vous le souhaitez utiliser un autre dataset si l’analyse en est déjà faite.

# **Objectifs pédagogiques**

* Formuler un message clair avant de coder (principe de la pyramide de Minto)  
* Choisir des KPIs actionnables plutôt que des vanity metrics  
* Appliquer les principes des canaux pré-attentifs et de la hiérarchie visuelle  
* Structurer une application Streamlit : sidebar, filtres, cache, mise en page en colonnes  
* Justifier le choix de chaque graphique

# **Modalités**

Travail en groupe — mêmes groupes que depuis le début du cours.

# **Livrables**

## 1\. Document de cadrage (une page)

* Le message clé, en une phrase  
* L'audience cible choisie  
* Les KPIs retenus, avec la justification vanity / actionable pour chacun  
* La structure prévue (zones KPIs / détail / filtres)

  ## 2\. Dashboard Streamlit fonctionnel

  Le script (.py) et les données utilisées. Le dashboard doit comporter :

* Un onglet par visualisation (ou plusieurs dashboards, au choix)  
* Un titre qui porte le message (pas juste le nom du dataset)  
* Une zone KPIs : 2 à 3 indicateurs maximum, contextualisés (tendance ou comparaison)  
* Une zone détail : au moins un graphique réactif aux filtres  
* Au moins 2 filtres interactifs dans la sidebar  
* L'usage de @st.cache\_data pour le chargement des données

  ## 3\. Pitch oral (5’ \+ 5’ présentation \+ questions)

  Date : jeudi 17 septembre à partir de 13h30. Présenter le message, montrer le dashboard en fonctionnement, et justifier deux ou trois choix de conception marquants. 

# **Critères d'évaluation**

Reprend la grille construite en cours, appliquée à votre propre production :

* **Message** — le dashboard porte-t-il une conclusion claire, pas seulement un thème ?  
* **Honnêteté** — les échelles, proportions et comparaisons sont-elles respectées ? Avez-vous utilisé l’IA ? Si oui, vous devez être capable d’expliquer chaque ligne de code.  
* **Lisibilité** — légendes, labels et axes sont-ils clairs sans effort ?  
* **Choix du graphique** — chaque type de graphique est-il adapté à la donnée et au message ?  
* **Hiérarchie & charge cognitive** — l'essentiel est-il visible en moins de 5 secondes ?  
* **Qualité technique** — filtres fonctionnels, cache utilisé, code lisible

**Pour aller plus loin** 

* **Structure multi-pages** — utiliser le dossier `pages/` de Streamlit pour proposer plusieurs vues liées (*ex :* une vue synthèse \+ une vue détail) plutôt qu'un écran unique. Renforce directement la hiérarchie de l'information vue en séance 4\.  
* **Déploiement en ligne** — publier le dashboard sur Streamlit Community Cloud (gratuit, connecté à un repo GitHub public ou privé). Le dashboard devient accessible par un simple lien, pas seulement démontré en local le jour de la soutenance.

## **Barème indicatif**

* Cadrage écrit : **/20**  
* Dashboard fonctionnel : **/40**  
* Pitch oral : **/20**  
* Structuration multi-pages : **/10**  
* Déploiement effectué : **/10**

# **Format de rendu**

Un dossier dans votre dossier personnel de  `Rendus/` (ou lien de repo Git), contenant :

* cadrage.md (ou .pdf)  
* Le(s) script(s) Streamlit (.py)  
* Le(s) fichier(s) de données utilisés  
* Le lien de déploiement streamlit.app