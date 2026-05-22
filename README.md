# FitCoach AI - Personal Trainer avec Webcam

## Description
Application web AWS qui utilise la webcam comme personal trainer intelligent.

## Fonctionnalités
- **Reconnaissance de posture** sur plusieurs exercices :
  - Pompes (Push-ups)
  - Squats
  - Curls (Bicep curls)
- **Conseils de posture** en temps réel (comment améliorer la forme)
- **Analyse active** via webcam (traitement Lambda)
- **Création de planning** d'exercices personnalisé

## Architecture de chaque partie

1. Frontend
- Capture la webcam, envoie les frames toutes les 2s à l'API, affiche score + conseils en temps réel

2. pose_analysis
- Reçoit l'image, détecte les landmarks du corps avec MediaPipe, calcule les angles articulaires, donne un score et des feedbacks

3. planning
- Utilise Bedrock (Claude) pour générer un programme d'entraînement personnalisé

4. advice
- Génère des conseils détaillés basés sur l'historique

5. Infrastructure CDK 
- Déploie tout sur AWS (API Gateway, 3 Lambdas, DynamoDB, Cognito)


## Architecture AWS
```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐
│   React     │────▶│ API Gateway │────▶│  Lambda (Python) │
│  (Webcam)   │◀────│             │◀────│                  │
└─────────────┘     └─────────────┘     └──────────────────┘
                                               │
                         ┌─────────────────────┼─────────────────────┐
                         │                     │                     │
                         ▼                     ▼                     ▼
                ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
                │  Rekognition│     │   DynamoDB   │     │   Bedrock    │
                │  (Pose)     │     │  (Planning)  │     │  (Conseils)  │
                └─────────────┘     └──────────────┘     └──────────────┘
```

## Stack Technique
- **Frontend** : React + TypeScript + TailwindCSS
- **Backend** : AWS Lambda (Python 3.12)
- **Analyse posture** : Amazon Rekognition / MediaPipe
- **IA Conseils** : Amazon Bedrock (Claude)
- **Base de données** : DynamoDB
- **Auth** : Amazon Cognito
- **Infrastructure** : AWS CDK (Python)

## Structure du projet
```
├── frontend/          # Application React
├── backend/           # Lambda functions
│   ├── pose_analysis/ # Analyse de posture
│   ├── planning/      # Gestion des plannings
│   └── advice/        # Génération de conseils
└── infrastructure/    # AWS CDK stack
```

## Démarrage rapide

### Prérequis
- Node.js 18+
- Python 3.12+
- AWS CLI configuré
- AWS CDK installé (`npm install -g aws-cdk`)

### Installation
```bash
# Frontend
cd frontend && npm install

# Backend
cd backend && pip install -r requirements.txt

# Infrastructure
cd infrastructure && pip install -r requirements.txt
```

### Développement local
```bash
# Lancer le frontend
cd frontend && npm run dev
```
