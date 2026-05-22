# 🎤 Pitch FitCoach AI — 5 minutes

---

## 🎯 Accroche (30 sec)

"Vous avez déjà essayé de faire des pompes chez vous en vous demandant si votre posture était correcte ? Ou abandonné un programme sportif parce que vous n'aviez pas de coach pour vous guider ? Aujourd'hui, on vous présente **FitCoach AI** — votre personal trainer intelligent, accessible depuis n'importe quel navigateur, avec juste une webcam."

---

## 💡 Le problème (45 sec)

- Un coach sportif coûte entre 40 et 80€ la séance
- Les vidéos YouTube ne corrigent pas vos erreurs en temps réel
- Une mauvaise posture = blessures (dos, genoux, épaules)
- Pas de suivi personnalisé quand on s'entraîne seul chez soi
- Résultat : 80% des gens abandonnent leur programme en moins de 3 mois

---

## 🚀 La solution : FitCoach AI (1 min 30)

FitCoach AI transforme votre webcam en coach sportif intelligent grâce à l'IA.

**3 fonctionnalités clés :**

1. **Analyse de posture en temps réel** — Toutes les 2 secondes, l'app capture une frame de votre webcam, l'envoie à notre backend, et MediaPipe détecte 33 points de votre corps. On calcule les angles articulaires (coudes, genoux, hanches) et on vous donne un score de 0 à 100% avec des corrections instantanées. "Descendez plus bas", "Gardez le dos droit", "Excellente posture !"

2. **Comptage de répétitions intelligent** — L'algorithme détecte les phases de chaque mouvement (montée/descente pour les pompes, contraction/extension pour les curls) et compte automatiquement vos reps.

3. **Planning personnalisé par IA générative** — Claude 3 (via Amazon Bedrock) génère un programme d'entraînement adapté à votre niveau (débutant, intermédiaire, avancé), votre objectif (force, endurance, masse) et votre disponibilité. Un vrai programme de coach, généré en 3 secondes.

**Exercices supportés** : Pompes, Squats, Curls biceps — avec des modèles d'angles spécifiques pour chaque mouvement.

---

## 🏗️ Architecture technique (1 min 15)

On a fait le choix d'une architecture **100% serverless sur AWS** :

- **Frontend** : React + TypeScript + TailwindCSS, déployable sur Amplify. Interface sombre, moderne, responsive. La webcam est gérée par react-webcam.

- **API Gateway** : 3 endpoints REST avec CORS. Point d'entrée unique, sécurisé.

- **3 fonctions Lambda Python** :
  - `pose-analysis` (512 MB) — MediaPipe pour la détection de pose
  - `planning` (256 MB) — Appel Bedrock pour générer les programmes
  - `advice` (256 MB) — Conseils personnalisés basés sur l'historique

- **Amazon Bedrock** (Claude 3 Haiku) — IA générative pour le planning et les conseils. Rapide, peu coûteux, pas de GPU à gérer.

- **DynamoDB** — Stockage des plannings et sessions utilisateur, pay-per-request.

- **Cognito** — Authentification email/mot de passe.

- **CDK** — Toute l'infra est en Infrastructure as Code, déployable en une commande.

**Pourquoi serverless ?** Zéro serveur à gérer, scaling automatique, et un coût estimé à **~7€/mois** pour un usage modéré. Coût nul si personne n'utilise.

---

## 📊 Démo rapide (30 sec)

"Je sélectionne 'Pompes', j'active ma webcam, je clique 'Démarrer l'analyse'... et en 2 secondes, j'ai mon score de posture, la phase détectée, et des conseils pour m'améliorer. Si je veux un programme complet, je vais sur Planning, je choisis mon niveau et mon objectif, et Claude me génère un planning sur mesure."

---

## 🎬 Conclusion & perspectives (30 sec)

FitCoach AI, c'est un coach sportif dans votre navigateur, pour le prix d'un café par mois.

**Prochaines étapes** :
- Ajouter plus d'exercices (planche, fentes, dips)
- Intégrer un historique de progression
- Gamification avec des challenges entre amis

Merci ! Des questions ?
