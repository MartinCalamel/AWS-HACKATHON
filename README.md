# 🏋️ FitCoach AI — Personal Trainer avec Webcam

## Description

Application web serverless AWS qui utilise la webcam comme **personal trainer intelligent**. L'IA analyse votre posture en temps réel, compte vos répétitions, et génère des programmes d'entraînement personnalisés.

## Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| 🫸 **Pompes** | Analyse posture coudes + alignement du corps |
| 🦵 **Squats** | Vérification profondeur genoux + dos droit |
| 💪 **Curls** | Contrôle contraction biceps + coude fixe |
| 💡 **Conseils temps réel** | Feedback instantané pour corriger la posture |
| 📅 **Planning IA** | Programme personnalisé généré par Claude (Bedrock) |
| 📊 **Score posture** | Note de 0 à 100% sur chaque frame |

---

## Architecture AWS

```
┌──────────────────┐         ┌──────────────────┐         ┌─────────────────────────────────────┐
│                  │  HTTPS  │                  │  Proxy  │         AWS Lambda (Python 3.12)     │
│   React App     │────────▶│  API Gateway     │────────▶│                                     │
│   (Webcam)      │◀────────│  (REST API)      │◀────────│  ┌─────────────┐ ┌──────────────┐   │
│                  │         │                  │         │  │ pose-analysis│ │   planning   │   │
│  • TypeScript    │         │  POST /analyze   │         │  │ (MediaPipe)  │ │  (Bedrock)   │   │
│  • TailwindCSS   │         │  POST /planning  │         │  └─────────────┘ └──────────────┘   │
│  • react-webcam  │         │  POST /advice    │         │  ┌─────────────┐                    │
│                  │         │                  │         │  │   advice    │                    │
└──────────────────┘         └──────────────────┘         │  │  (Bedrock)  │                    │
                                                          │  └─────────────┘                    │
        ┌──────────────────┐                              └──────────┬──────────────┬───────────┘
        │  Amazon Cognito  │                                         │              │
        │  (User Pool)     │                                         ▼              ▼
        └──────────────────┘                              ┌──────────────┐  ┌──────────────────┐
                                                          │  DynamoDB    │  │ Amazon Bedrock   │
                                                          │              │  │ Claude 3 Haiku   │
                                                          │ • plannings  │  │                  │
                                                          │ • sessions   │  │ • Génère plans   │
                                                          └──────────────┘  │ • Conseils IA    │
                                                                            └──────────────────┘
```

> 📐 Un diagramme draw.io détaillé est disponible : [`architecture.drawio`](./architecture.drawio)

---

## Services AWS utilisés

| Service | Rôle | Configuration |
|---------|------|---------------|
| **API Gateway** | Point d'entrée REST, CORS | 3 routes POST |
| **Lambda** | Logique métier serverless | Python 3.12, 3 fonctions |
| **DynamoDB** | Stockage plannings + sessions | PAY_PER_REQUEST |
| **Bedrock** | IA générative (Claude 3 Haiku) | Planning + Conseils |
| **Cognito** | Authentification utilisateurs | Email + mot de passe |
| **IAM** | Permissions fine-grained | Least privilege |
| **CloudFormation** | Déploiement (via CDK) | Infrastructure as Code |

---

## Prérequis

### Outils requis

| Outil | Version minimum | Installation |
|-------|----------------|--------------|
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org/) |
| **Python** | 3.12+ | [python.org](https://www.python.org/) |
| **AWS CLI** | 2.x | [docs.aws.amazon.com](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) |
| **AWS CDK** | 2.x | `npm install -g aws-cdk` |
| **Git** | 2.x | [git-scm.com](https://git-scm.com/) |

### Configuration AWS requise

1. **Compte AWS** actif avec accès à la région `us-east-1`
2. **AWS CLI configuré** avec des credentials valides
3. **Accès Bedrock** : le modèle `anthropic.claude-3-haiku-20240307-v1:0` doit être activé dans votre compte

---

## Déploiement pas à pas

### Étape 1 — Cloner le projet

```bash
git clone <url-du-repo>
cd AWS-HACKATHON
```

### Étape 2 — Activer l'accès au modèle Bedrock

> ⚠️ **Important** : Sans cette étape, les Lambdas planning et advice ne fonctionneront pas.

1. Ouvrir la [console Amazon Bedrock](https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess)
2. Aller dans **Model access** (menu gauche)
3. Cliquer **Manage model access**
4. Cocher **Anthropic → Claude 3 Haiku**
5. Cliquer **Save changes**
6. Attendre que le statut passe à **Access granted** (quelques minutes)

### Étape 3 — Installer les dépendances infrastructure

```bash
cd infrastructure
python -m venv .venv
```

**Windows (PowerShell) :**
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux/macOS :**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Étape 4 — Bootstrap CDK (première fois uniquement)

```bash
cdk bootstrap aws://ACCOUNT_ID/us-east-1
```

> Remplacez `ACCOUNT_ID` par votre ID de compte AWS (12 chiffres).  
> Pour le trouver : `aws sts get-caller-identity --query Account --output text`

### Étape 5 — Déployer l'infrastructure

```bash
cd infrastructure
cdk deploy --require-approval never
```

**Sortie attendue :**
```
 ✅  FitCoachAIStack

Outputs:
FitCoachAIStack.ApiUrl = https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/
FitCoachAIStack.UserPoolId = us-east-1_XXXXXXXXX
FitCoachAIStack.UserPoolClientId = xxxxxxxxxxxxxxxxxxxxxxxxxx
```

> 📝 **Notez l'`ApiUrl`** — vous en aurez besoin pour le frontend.

### Étape 6 — Configurer et déployer le frontend

```bash
cd frontend
npm install
```

Créer le fichier d'environnement :

```bash
echo VITE_API_URL=https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod > .env
```

> Remplacez l'URL par celle obtenue à l'étape 5.

**Lancer en développement local :**
```bash
npm run dev
```

**Build pour production :**
```bash
npm run build
```

Le build se trouve dans `frontend/dist/` — prêt à être déployé sur S3 + CloudFront ou Amplify.

---

## Déploiement frontend sur AWS (optionnel)

### Option A — AWS Amplify Hosting (recommandé)

1. Aller sur [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. **New app** → **Host web app**
3. Connecter votre repo Git
4. Configurer le build :
   - Base directory : `frontend`
   - Build command : `npm run build`
   - Output directory : `dist`
5. Ajouter la variable d'environnement `VITE_API_URL`
6. Déployer

### Option B — S3 + CloudFront

```bash
cd frontend
npm run build

# Créer le bucket S3
aws s3 mb s3://fitcoach-ai-frontend --region us-east-1

# Upload le build
aws s3 sync dist/ s3://fitcoach-ai-frontend --delete

# Configurer l'hébergement statique
aws s3 website s3://fitcoach-ai-frontend --index-document index.html --error-document index.html
```

---

## Structure du projet

```
AWS-HACKATHON/
├── architecture.drawio          # Diagramme d'architecture (draw.io)
├── README.md                    # Ce fichier
│
├── frontend/                    # Application React
│   ├── src/
│   │   ├── components/          # Composants réutilisables (Layout)
│   │   ├── pages/               # Pages (Home, Workout, Planning)
│   │   ├── services/            # Client API (axios)
│   │   ├── App.tsx              # Router principal
│   │   └── main.tsx             # Point d'entrée
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── backend/                     # Lambda functions (Python)
│   ├── pose_analysis/
│   │   └── handler.py           # Analyse posture (MediaPipe)
│   ├── planning/
│   │   └── handler.py           # Génération planning (Bedrock)
│   ├── advice/
│   │   └── handler.py           # Conseils personnalisés (Bedrock)
│   └── requirements.txt
│
└── infrastructure/              # AWS CDK (Python)
    ├── app.py                   # Entry point CDK
    ├── cdk.json                 # Configuration CDK
    ├── requirements.txt         # Dépendances CDK
    └── stacks/
        └── fitcoach_stack.py    # Stack principale
```

---

## Endpoints API

| Méthode | Route | Description | Body |
|---------|-------|-------------|------|
| `POST` | `/analyze-pose` | Analyse une frame webcam | `{ "image": "base64...", "exercise": "pushups\|squats\|curls" }` |
| `POST` | `/generate-planning` | Génère un planning IA | `{ "level": "beginner", "goal": "strength", "daysPerWeek": 3 }` |
| `POST` | `/get-advice` | Conseils personnalisés | `{ "exercise": "pushups", "scores": [75, 80], "commonIssues": [...] }` |

---

## Développement local

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### Tester les Lambdas localement (optionnel)

```bash
cd backend
pip install -r requirements.txt

# Test rapide pose_analysis
python -c "
import json
from pose_analysis.handler import handler
event = {'body': json.dumps({'image': '', 'exercise': 'pushups'})}
print(handler(event, None))
"
```

---

## Coûts estimés

| Service | Estimation (usage modéré) |
|---------|--------------------------|
| Lambda | ~$0.50/mois (1000 analyses/jour) |
| API Gateway | ~$3.50/mois |
| DynamoDB | ~$1.00/mois (on-demand) |
| Bedrock (Claude Haiku) | ~$2.00/mois (100 plannings) |
| Cognito | Gratuit (< 50k MAU) |
| **Total** | **~$7/mois** |

> 💡 Tous les services utilisent un modèle **pay-per-use**. Coût nul si pas d'utilisation.

---

## Dépannage

| Problème | Solution |
|----------|----------|
| `AccessDeniedException` sur Bedrock | Activer le modèle Claude 3 Haiku dans la console Bedrock (Étape 2) |
| `cdk bootstrap` échoue | Vérifier que AWS CLI est configuré : `aws sts get-caller-identity` |
| CORS error dans le navigateur | Vérifier que `VITE_API_URL` pointe vers l'URL API Gateway avec `/prod/` |
| Webcam non détectée | Autoriser l'accès caméra dans le navigateur (HTTPS requis en prod) |
| Lambda timeout | Vérifier la taille de l'image envoyée (< 6MB recommandé) |
| MediaPipe ne détecte pas la posture | S'assurer d'être bien visible, éclairage suffisant, corps entier dans le cadre |

---

## Nettoyage (supprimer les ressources)

```bash
cd infrastructure
cdk destroy
```

> Cela supprime toutes les ressources AWS créées (Lambda, API Gateway, DynamoDB, Cognito).

---

## Stack technique

- **Frontend** : React 18 + TypeScript + Vite + TailwindCSS + react-webcam
- **Backend** : AWS Lambda (Python 3.12) + MediaPipe + Boto3
- **IA** : Amazon Bedrock (Claude 3 Haiku)
- **Base de données** : Amazon DynamoDB (serverless)
- **Auth** : Amazon Cognito
- **Infrastructure** : AWS CDK (Python)
- **Région** : us-east-1 (N. Virginia)

---

## Auteurs

Projet réalisé dans le cadre du AWS Hackathon — CPE Lyon 4ETI MSO
