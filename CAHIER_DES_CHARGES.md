# 📋 Cahier des Charges — FitCoach AI

## Application de musculation assistée par IA avec système agentique

---

## 1. Présentation du projet

### 1.1 Contexte

FitCoach AI est une application web et mobile de musculation au poids du corps, assistée par intelligence artificielle. L'application utilise la caméra de l'utilisateur pour analyser et corriger la posture en temps réel, génère des programmes d'entraînement personnalisés, et assure un suivi complet de la performance.

### 1.2 Objectifs

| Objectif | Description |
|----------|-------------|
| Correction posturale | Analyse temps réel via caméra (TensorFlow + MediaPipe Pose) |
| Programmes personnalisés | Génération IA adaptée au niveau et objectifs |
| Calendrier intelligent | Planification automatique avec gestion du repos |
| Suivi de performance | Métriques détaillées, progression, historique |
| Gamification | Badges, streaks, XP, classements |
| Multi-plateforme | Web (React) + Mobile (PWA) |

### 1.3 Public cible

- Débutants à avancés en musculation poids du corps
- Personnes souhaitant s'entraîner à domicile sans matériel
- Utilisateurs recherchant un coaching IA personnalisé

---

## 2. Architecture système agentique

### 2.1 Vue d'ensemble

L'application repose sur un **système multi-agents orchestré par un Master Agent**. Chaque agent est spécialisé dans un domaine et communique avec les autres via le Master pour prendre des décisions cohérentes.

```
                    ┌─────────────────────────┐
                    │      MASTER AGENT       │
                    │   (Orchestrateur IA)    │
                    │                         │
                    │  • Routing des requêtes  │
                    │  • Coordination agents   │
                    │  • Décisions globales    │
                    └────────────┬────────────┘
                                 │
         ┌───────────┬───────────┼───────────┬───────────┬───────────┐
         │           │           │           │           │           │
         ▼           ▼           ▼           ▼           ▼           ▼
   ┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐
   │  AGENT   ││  AGENT   ││  AGENT   ││  AGENT   ││  AGENT   ││  AGENT   │
   │ POSTURE  ││PROGRAMME ││CALENDRIER││PERFORMANCE│ REPOS    ││  COACH   │
   │          ││          ││          ││          ││          ││          │
   │MediaPipe ││Génération││Planning  ││Métriques ││Récupéra- ││Conseils  │
   │TensorFlow││Plans     ││Semaine   ││Graphiques││tion      ││Motivation│
   └──────────┘└──────────┘└──────────┘└──────────┘└──────────┘└──────────┘
```

### 2.2 Master Agent (Orchestrateur)

**Rôle** : Point d'entrée unique pour toutes les requêtes utilisateur. Route vers le bon agent, agrège les réponses, et coordonne les interactions inter-agents.

**Responsabilités** :
- Analyser l'intention de l'utilisateur
- Router vers le(s) agent(s) approprié(s)
- Agréger les réponses multi-agents
- Gérer les conflits entre agents (ex: Programme veut intensifier mais Repos dit de récupérer)
- Maintenir le contexte utilisateur global

**Implémentation** :
- AWS Lambda (Python 3.12)
- Amazon Bedrock (Claude 3 Sonnet) pour le raisonnement
- DynamoDB pour le contexte de session

### 2.3 Agent Posture

**Rôle** : Analyse en temps réel de la posture via la caméra.

**Responsabilités** :
- Recevoir les frames vidéo (base64 JPEG)
- Détecter les landmarks corporels (33 points MediaPipe)
- Calculer les angles articulaires
- Évaluer la qualité du mouvement (score 0-100)
- Compter les répétitions automatiquement
- Générer des feedbacks correctifs en temps réel
- Détecter les risques de blessure

**Technologies** :
- MediaPipe Pose (détection landmarks)
- TensorFlow (modèle custom pour scoring)
- NumPy (calculs géométriques)

**Exercices détectés** :

| Exercice | Angles surveillés | Variantes |
|----------|-------------------|-----------|
| Pompes | Coude, hanche, épaule | Standard, diamant, déclinées, archer |
| Squats | Genou, hanche, cheville | Standard, pistol, jump, sumo |
| Dips | Coude, épaule | Standard, bench dips |
| Tractions | Coude, épaule, dos | Pull-up, chin-up, wide grip |
| Planche | Hanche, épaule | Standard, latérale, dynamique |
| Fentes | Genou avant/arrière, hanche | Standard, marchées, sautées |
| Burpees | Séquence complète | Standard, sans pompe |
| Mountain climbers | Genou, hanche | Standard, cross-body |

### 2.4 Agent Programme

**Rôle** : Génération et adaptation de programmes d'entraînement personnalisés.

**Responsabilités** :
- Créer des programmes adaptés au niveau (débutant/intermédiaire/avancé)
- Adapter selon l'objectif (force, endurance, hypertrophie, perte de poids)
- Progression automatique (augmentation charge/volume)
- Prise en compte des retours de l'Agent Performance
- Gestion de la périodisation (microcycles, mésocycles)

**Inputs** :
- Profil utilisateur (niveau, objectif, disponibilité)
- Historique de performance (via Agent Performance)
- État de récupération (via Agent Repos)
- Exercices maîtrisés (via Agent Posture)

**Outputs** :
- Programme hebdomadaire structuré
- Séances détaillées (exercices, séries, reps, tempo)
- Progressions planifiées

### 2.5 Agent Calendrier

**Rôle** : Planification temporelle des séances et gestion de l'agenda.

**Responsabilités** :
- Placer les séances dans la semaine selon les disponibilités
- Respecter les contraintes de repos entre groupes musculaires
- Gérer les reports et rattrapages
- Envoyer des rappels (notifications push)
- Vue semaine et mois
- Synchronisation possible avec calendriers externes

**Règles métier** :
- Minimum 48h entre deux séances ciblant le même groupe musculaire
- Maximum 2 jours consécutifs d'entraînement intense
- Au moins 1 jour de repos complet par semaine

### 2.6 Agent Performance

**Rôle** : Suivi, analyse et visualisation des progrès.

**Responsabilités** :
- Enregistrer chaque séance (exercices, reps, séries, durée)
- Calculer les métriques de progression
- Détecter les plateaux et régressions
- Générer des graphiques et rapports
- Alerter le Master Agent en cas de stagnation

**Métriques suivies** :

| Métrique | Description |
|----------|-------------|
| Volume total | Nombre total de reps × séries par séance |
| Score posture moyen | Moyenne des scores de l'Agent Posture |
| PR (Personal Records) | Meilleur score par exercice |
| Régularité | % de séances complétées vs planifiées |
| Progression | Évolution du volume sur 4 semaines |
| Temps sous tension | Durée totale d'effort par séance |
| Calories estimées | Estimation basée sur le volume et l'intensité |

### 2.7 Agent Repos

**Rôle** : Gestion de la récupération et prévention du surentraînement.

**Responsabilités** :
- Calculer le temps de repos optimal entre séries (30s à 3min selon objectif)
- Timer interactif entre les séries avec notification sonore
- Évaluer la fatigue accumulée (charge d'entraînement sur 7 jours)
- Recommander des jours de repos
- Détecter les signes de surentraînement
- Suggérer des séances de récupération active (stretching, mobilité)

**Règles** :
- Repos entre séries : 30-60s (endurance), 60-90s (hypertrophie), 2-3min (force)
- Charge hebdomadaire maximale adaptée au niveau
- Alerte si volume augmente de +20% d'une semaine à l'autre

### 2.8 Agent Coach

**Rôle** : Motivation, conseils personnalisés et communication naturelle.

**Responsabilités** :
- Fournir des conseils nutritionnels basiques
- Motiver l'utilisateur (messages personnalisés)
- Expliquer les exercices et leur intérêt
- Répondre aux questions fitness en langage naturel
- Adapter le ton selon la personnalité de l'utilisateur

### 2.9 Communication inter-agents

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUX DE COMMUNICATION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Performance ──(stagnation détectée)──→ Master ──→ Programme    │
│  Programme adapte la charge automatiquement                      │
│                                                                  │
│  Posture ──(score < 50% répété)──→ Master ──→ Coach             │
│  Coach envoie des conseils correctifs ciblés                     │
│                                                                  │
│  Repos ──(fatigue élevée)──→ Master ──→ Calendrier              │
│  Calendrier reporte la séance et propose récupération active     │
│                                                                  │
│  Performance ──(PR battu)──→ Master ──→ Coach + Gamification    │
│  Coach félicite, badge débloqué                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Fonctionnalités détaillées

### 3.1 Analyse posture temps réel

| Fonctionnalité | Description |
|----------------|-------------|
| Détection automatique d'exercice | L'IA reconnaît quel exercice est effectué |
| Comptage de reps | Incrémentation automatique basée sur les phases du mouvement |
| Score posture | Note 0-100 mise à jour à chaque frame |
| Feedback visuel | Overlay sur la vidéo montrant les angles (vert=bon, rouge=mauvais) |
| Feedback textuel | Conseils en temps réel ("Descendez plus bas", "Dos trop cambré") |
| Alerte blessure | Warning si angle dangereux détecté |
| Historique vidéo | Option d'enregistrer la séance pour revoir après |

**Spécifications techniques** :
- Capture : 5 frames/seconde envoyées au serveur
- Résolution : 640×480 JPEG quality 0.7
- Latence cible : < 500ms entre capture et feedback
- Taille frame : ~20-40KB (base64)

### 3.2 Programmes d'entraînement

| Fonctionnalité | Description |
|----------------|-------------|
| Questionnaire initial | Niveau, objectif, jours dispo, limitations physiques |
| Génération IA | Programme complet généré par Bedrock |
| Templates | Programmes pré-faits pour démarrer rapidement |
| Personnalisation | Modifier exercices, séries, reps manuellement |
| Progression auto | Augmentation progressive (+2 reps/semaine ou variante plus dure) |
| Périodisation | Cycles de 4 semaines (3 progressives + 1 deload) |

**Types de programmes** :

| Type | Fréquence | Focus |
|------|-----------|-------|
| Full Body | 3×/semaine | Débutants, forme générale |
| Push/Pull/Legs | 4-6×/semaine | Intermédiaire, hypertrophie |
| Upper/Lower | 4×/semaine | Force, équilibre |
| HIIT | 3-5×/semaine | Perte de poids, cardio |

### 3.3 Calendrier d'entraînement

| Fonctionnalité | Description |
|----------------|-------------|
| Vue semaine | Séances planifiées avec détail |
| Vue mois | Vue d'ensemble avec code couleur |
| Drag & drop | Déplacer une séance à un autre jour |
| Rappels | Notification push 30min avant la séance |
| Report intelligent | Si séance manquée, proposition de rattrapage |
| Jours de repos | Marqués explicitement, non modifiables sans validation |
| Streak tracker | Compteur de jours consécutifs d'entraînement |

### 3.4 Suivi de performance

| Fonctionnalité | Description |
|----------------|-------------|
| Dashboard | Vue d'ensemble avec KPIs principaux |
| Graphiques | Courbes de progression par exercice |
| Personal Records | Tableau des meilleurs scores |
| Historique séances | Liste détaillée de toutes les séances passées |
| Comparaison | Comparer semaine actuelle vs précédente |
| Export | Export PDF/CSV des données |
| Insights IA | Analyse textuelle des tendances par l'Agent Coach |

### 3.5 Gestion du repos

| Fonctionnalité | Description |
|----------------|-------------|
| Timer inter-séries | Compte à rebours avec notification sonore |
| Timer configurable | Ajustable selon l'objectif (30s à 5min) |
| Auto-suggestion | Temps de repos recommandé selon l'exercice et la fatigue |
| Indicateur fatigue | Barre de fatigue estimée (basée sur volume cumulé) |
| Jours de repos | Recommandation de repos basée sur la charge récente |
| Récupération active | Séances de stretching/mobilité proposées les jours off |

### 3.6 Gamification

| Fonctionnalité | Description |
|----------------|-------------|
| Système XP | Points gagnés par séance complétée, score posture, régularité |
| Niveaux | Débutant → Intermédiaire → Avancé → Expert → Légende |
| Badges | Récompenses pour accomplissements spécifiques |
| Streaks | Compteur de jours consécutifs (bonus XP) |
| Leaderboard | Classement hebdomadaire entre utilisateurs |
| Défis | Challenges communautaires (ex: "1000 pompes en 7 jours") |

**Exemples de badges** :

| Badge | Condition |
|-------|-----------|
| 🔥 Premier pas | Compléter sa première séance |
| 💯 Perfectionniste | Score posture > 90% sur une séance entière |
| 📅 Régulier | 7 jours de streak |
| 🏆 Centurion | 100 pompes en une séance |
| ⚡ Infatigable | 30 jours de streak |
| 🎯 Sniper | 10 PR battus |
| 👑 Légende | Atteindre le niveau maximum |

---

## 4. Architecture technique

### 4.1 Stack technologique

| Couche | Technologie |
|--------|-------------|
| **Frontend Web** | React 18 + TypeScript + Vite + TailwindCSS |
| **Frontend Mobile** | PWA (Progressive Web App) |
| **Backend** | AWS Lambda (Python 3.12) |
| **API** | Amazon API Gateway (REST) |
| **IA Générative** | Amazon Bedrock (Claude 3 Sonnet/Haiku) |
| **Analyse posture** | MediaPipe Pose + TensorFlow |
| **Base de données** | Amazon DynamoDB |
| **Auth** | Amazon Cognito |
| **Stockage fichiers** | Amazon S3 |
| **CDN** | Amazon CloudFront |
| **Notifications** | Amazon SNS + Web Push API |
| **Infrastructure** | AWS CDK (Python) |
| **CI/CD** | GitHub Actions → CodePipeline |

### 4.2 Architecture AWS

```
┌─────────────┐     ┌──────────┐     ┌───────────┐     ┌─────────────────────────────────┐
│  Utilisateur │────▶│CloudFront│────▶│    S3     │     │        AWS Lambda               │
│  (PWA)       │     │  (CDN)   │     │(Frontend) │     │                                 │
└──────┬───────┘     └──────────┘     └───────────┘     │  ┌───────────────────────────┐  │
       │                                                 │  │     Master Agent Lambda    │  │
       │  REST API                                       │  └─────────────┬─────────────┘  │
       │                                                 │                │                 │
       ▼                                                 │  ┌─────┬──────┼──────┬──────┐   │
┌──────────────┐     ┌──────────┐                        │  │     │      │      │      │   │
│  API Gateway │────▶│ Cognito  │                        │  ▼     ▼      ▼      ▼      ▼   │
│  (REST)      │     │(Authoriz)│                        │ Pose Prog  Calen Perf  Repos    │
└──────┬───────┘     └──────────┘                        │ Agent Agent Agent Agent Agent   │
       │                                                 └────┬────┬──────┬──────┬─────────┘
       └────────────────────────────────────────────────────▶ │    │      │      │
                                                              ▼    ▼      ▼      ▼
                                                        ┌──────────────────────────────┐
                                                        │         DynamoDB             │
                                                        │  • users    • sessions       │
                                                        │  • programs • performance    │
                                                        │  • calendar • achievements   │
                                                        └──────────────────────────────┘
                                                              │
                                                              ▼
                                                        ┌──────────────┐
                                                        │   Bedrock    │
                                                        │ Claude 3     │
                                                        └──────────────┘
```

### 4.3 Tables DynamoDB

| Table | PK | SK | Usage |
|-------|----|----|-------|
| `fitcoach-users` | userId | `PROFILE` | Profil utilisateur, préférences |
| `fitcoach-programs` | userId | programId | Programmes d'entraînement |
| `fitcoach-sessions` | userId | sessionId (timestamp) | Historique des séances |
| `fitcoach-performance` | userId | `{exercise}#{date}` | Métriques par exercice |
| `fitcoach-calendar` | userId | date | Séances planifiées |
| `fitcoach-achievements` | userId | badgeId | Badges et XP |
| `fitcoach-leaderboard` | `WEEKLY#{week}` | score | Classement hebdomadaire |

### 4.4 Endpoints API

| Méthode | Route | Agent | Description |
|---------|-------|-------|-------------|
| POST | `/agent/ask` | Master | Point d'entrée unique (routing IA) |
| POST | `/pose/analyze` | Posture | Analyse une frame webcam |
| POST | `/program/generate` | Programme | Génère un programme |
| GET | `/program/{id}` | Programme | Récupère un programme |
| PUT | `/program/{id}` | Programme | Modifie un programme |
| GET | `/calendar/week` | Calendrier | Séances de la semaine |
| PUT | `/calendar/{date}` | Calendrier | Modifier une séance planifiée |
| POST | `/session/start` | Performance | Démarre une séance |
| POST | `/session/end` | Performance | Termine une séance |
| GET | `/performance/stats` | Performance | Métriques globales |
| GET | `/performance/history` | Performance | Historique détaillé |
| GET | `/rest/timer` | Repos | Temps de repos recommandé |
| GET | `/achievements` | Coach | Badges et progression |
| GET | `/leaderboard` | Coach | Classement |

---

## 5. Interfaces utilisateur

### 5.1 Pages principales

| Page | Description |
|------|-------------|
| **Accueil / Dashboard** | KPIs, prochaine séance, streak, niveau |
| **Workout** | Séance en cours avec caméra + timer + feedback |
| **Programmes** | Liste des programmes, création, modification |
| **Calendrier** | Vue semaine/mois des séances |
| **Performance** | Graphiques, PR, historique |
| **Profil** | Paramètres, badges, niveau, stats globales |
| **Leaderboard** | Classement communautaire |
| **Chat Coach** | Interface conversationnelle avec l'Agent Coach |

### 5.2 Écran Workout (principal)

```
┌─────────────────────────────────────────────────────────────┐
│  ← Retour          POMPES (Série 2/4)           ⏱️ 01:23   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                                                       │   │
│  │              [FLUX WEBCAM]                             │   │
│  │         (overlay angles + squelette)                   │   │
│  │                                                       │   │
│  │                                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐    │
│  │ Score: 87% │  │ Reps: 8/12 │  │ Phase: descente ↓  │    │
│  └────────────┘  └────────────┘  └────────────────────┘    │
│                                                              │
│  💡 Conseil: "Gardez le dos bien droit, ne cambrez pas"     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ⏸️ Pause  │  ⏭️ Série suivante  │  ⏹️ Terminer     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ⏱️ REPOS: 45s restantes  [━━━━━━━━░░░░]                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Sécurité

| Aspect | Implémentation |
|--------|----------------|
| Authentification | Cognito (email + mot de passe, MFA optionnel) |
| Autorisation | JWT tokens, scopes par endpoint |
| API Protection | WAF (rate limiting, IP filtering) |
| Données personnelles | Chiffrement at-rest (DynamoDB) et in-transit (HTTPS) |
| RGPD | Droit à l'effacement, export données, consentement caméra |
| Vidéo | Frames traitées en mémoire, jamais stockées (sauf opt-in) |
| Secrets | AWS Secrets Manager, rotation automatique |

---

## 7. Performance & Scalabilité

| Métrique | Cible |
|----------|-------|
| Latence analyse posture | < 500ms |
| Latence API standard | < 200ms |
| Disponibilité | 99.9% |
| Utilisateurs simultanés | 1000+ |
| Cold start Lambda | < 2s (Provisioned Concurrency pour Pose) |
| Taille bundle frontend | < 500KB gzipped |

---

## 8. PWA (Progressive Web App)

| Fonctionnalité | Description |
|----------------|-------------|
| Installation | Installable sur mobile (Add to Home Screen) |
| Offline | Cache des programmes et calendrier |
| Notifications push | Rappels de séance, badges débloqués |
| Caméra | Accès webcam via Web API |
| Responsive | Adapté mobile, tablette, desktop |
| Service Worker | Cache stratégique (stale-while-revalidate) |

---

## 9. Gamification détaillée

### 9.1 Système XP

| Action | XP gagnés |
|--------|-----------|
| Compléter une séance | +100 XP |
| Score posture > 80% | +50 XP bonus |
| Score posture > 95% | +100 XP bonus |
| Battre un PR | +75 XP |
| Streak journalier | +25 XP × jours consécutifs |
| Compléter un défi | +200 XP |

### 9.2 Niveaux

| Niveau | XP requis | Titre |
|--------|-----------|-------|
| 1 | 0 | Débutant |
| 2 | 500 | Apprenti |
| 3 | 1500 | Régulier |
| 4 | 3500 | Athlète |
| 5 | 7000 | Expert |
| 6 | 12000 | Maître |
| 7 | 20000 | Légende |

### 9.3 Leaderboard

- Classement hebdomadaire (reset chaque lundi)
- Basé sur : XP gagnés dans la semaine
- Top 3 reçoivent un badge spécial
- Filtrable par niveau pour équité

---

## 10. Livrables

| Phase | Livrable | Délai estimé |
|-------|----------|--------------|
| **Phase 1** | MVP : Analyse posture + 1 programme | 2 semaines |
| **Phase 2** | Calendrier + Suivi performance | 2 semaines |
| **Phase 3** | Système agentique complet + Repos | 2 semaines |
| **Phase 4** | Gamification + Leaderboard + PWA | 2 semaines |
| **Phase 5** | CI/CD + Monitoring + Production | 1 semaine |

---

## 11. Contraintes

| Contrainte | Description |
|------------|-------------|
| Hébergement | AWS uniquement (us-east-1) |
| Budget | Optimisé serverless (pay-per-use) |
| Langue | Français (interface) + Anglais (code) |
| Navigateurs | Chrome, Firefox, Safari, Edge (2 dernières versions) |
| Mobile | iOS 15+ et Android 10+ (via PWA) |
| Caméra | Nécessite HTTPS pour accès webcam |
| RGPD | Conformité données personnelles EU |

---

## 12. Critères d'acceptation

### 12.1 Analyse posture
- [ ] Détection correcte sur 8+ exercices
- [ ] Score posture cohérent (validé manuellement sur 50 mouvements)
- [ ] Comptage de reps précis à ±1 rep
- [ ] Latence < 500ms
- [ ] Feedback pertinent et non répétitif

### 12.2 Programmes
- [ ] Génération en < 5s
- [ ] Programme adapté au niveau déclaré
- [ ] Progression cohérente sur 4 semaines
- [ ] Modification manuelle possible

### 12.3 Calendrier
- [ ] Vue semaine et mois fonctionnelles
- [ ] Drag & drop sur mobile et desktop
- [ ] Notifications push fonctionnelles
- [ ] Report intelligent opérationnel

### 12.4 Performance
- [ ] Graphiques lisibles et interactifs
- [ ] Données cohérentes avec les séances effectuées
- [ ] Export PDF fonctionnel
- [ ] PR détectés automatiquement

### 12.5 Gamification
- [ ] XP calculés correctement
- [ ] Badges débloqués au bon moment
- [ ] Leaderboard mis à jour en temps réel
- [ ] Streaks comptés correctement (timezone utilisateur)

### 12.6 Système agentique
- [ ] Master Agent route correctement 95%+ des requêtes
- [ ] Communication inter-agents fonctionnelle
- [ ] Temps de réponse global < 3s
- [ ] Cohérence des décisions (pas de contradictions entre agents)

---

## 13. Évolutions futures (hors scope V1)

- Intégration montres connectées (Apple Watch, Garmin)
- Mode duo (entraînement à deux via caméra)
- Marketplace de programmes (créés par des coachs)
- Analyse nutritionnelle (photo de repas)
- Réalité augmentée (overlay 3D sur le corps)
- Support matériel (haltères, élastiques) via détection d'objets
- App native (React Native) si PWA insuffisante
