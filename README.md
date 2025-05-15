# Albert_group

Notre projet consiste à prédire l'issue des matchs de foot de toutes les compétitions au niveau mondial de la saison 2024-2025 sur la base de nombreuses données variées allant de la date du match, de la composition des équipes sur le terrain ou des séries de victoire de chaque équipes aux données relatives aux entraineurs ou encore aux terrains (surface, capacité de spectateur). Nous adossons nos résultats à une baseline établie grâce aux côtes récoltées sur la plateforme de pari en ligne bet365.
Notre projet s'inscrit dans une volonté réelle de pouvoir déployer ce programme pour réaliser des gains sûrs en pariant sereinement.

Les étapes : 

- Extraction par calls API sur Sportmonks qui nous permet d'obtenir des données "inhérentes" (ex : équipes, formations, séries de victoires...) et extérieures au match (ex : données météorologiques, date de naissance des coachs, capacité du stade...) pour la création de notre dataset.

- Création d'une baseline grâce aux côtes récupérées pour chaque match permettant de comparer les résultats de nos modèles (weighted average f1-score = 0,35).

- Entraînement de plusieurs modèles dont RandomForestClassifier et XGBClassifier avec des méthodes d'optimisation d'hyperparamètres. L'utilisation de GridSearch CV, qu'on a combiné avec un Stratified KFold pour garder l'équilibre des classes prédites (plus de matchs gagné à domicile que de matchs nuls par exemple), nous a permis d'améliorer les résultats. Nous avons aussi entrainé un modèle avec une RFE pour optimiser d'avantage en sélectionnant les features les plus determinantes avant l'optimisation des paramètres (nombre de features final : 31 au lieu de 34).

- Création d'un streamlit opérationnel et interactif pour générer des matchs fictifs ou remplir manuellement les données de matchs futurs que l'on voudrait prédire. Les résultats sont générés par notre algorithme de random forest pour pouvoir donner de l'interprétabilité aux utilisateurs avec des probabilités et un graphe de feature importance. D'autres pages annexes sont disponible sur le streamlit pour clusteriser les clubs et prédire le classement final des différentes leagues disponibles.


