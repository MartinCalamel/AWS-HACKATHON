# 🏋️ FitCoach AI V2 — Guide de déploiement

## Test en local

### Frontend uniquement (sans backend AWS)

Le frontend fonctionne en local avec des données mock (fallback) quand l'API n'est pas disponible.

```bash
cd fitcoach-v2/frontend
npm install
npm run dev
# → http://localhost:5173
```

> La webcam fonctionne en local (localhost est considéré comme sécurisé).
> Les pages Dashboard, Calendar, Performance, Profile, Leaderboard affichent des données mock.
> L'analyse posture et le Coach IA nécessitent le backend AWS.

### Backend local (limité)

Le backend utilise des services AWS (DynamoDB, Bedrock) donc il ne tourne pas 100% en local.
Pour tester les fonctions Lambda localement, vous pouvez utiliser **SAM CLI** :

```bash
cd fitcoach-v2
pip install aws-sam-cli

# Tester la pose analysis
sam local invoke PoseAnalysisLambda --event test-event.json
```

---

## Déploiement AWS complet

### Prérequis

| Outil | Version | Installation |
|-------|---------|--------------|
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| Python | 3.12+ | [python.org](https://python.org/) |
| AWS CLI | 2.x | [aws.amazon.com/cli](https://aws.amazon.com/cli/) |
| AWS CDK | 2.x | `npm install -g aws-cdk` |

### Étape 1 — Configurer AWS CLI

```bash
aws configure
# → Access Key ID: AKIA...
# → Secret Access Key: ...
# → Region: us-east-1
# → Output format: json

# Vérifier que ça marche :
aws sts get-caller-identity
```

### Étape 2 — Activer Bedrock (Claude 3 Haiku)

1. Aller sur [console Bedrock](https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess)
2. **Model access** → **Manage model access**
3. Cocher **Anthropic → Claude 3 Haiku**
4. **Save changes**
5. Attendre "Access granted" (2-5 min)

> ⚠️ Sans cette étape, les agents Programme, Coach et Advice ne fonctionneront pas.

### Étape 3 — Bootstrap CDK (première fois uniquement)

```bash
# Trouver votre Account ID
aws sts get-caller-identity --query Account --output text

# Bootstrap
cdk bootstrap aws://VOTRE_ACCOUNT_ID/us-east-1
```

### Étape 4 — Installer les dépendances infrastructure

```bash
cd fitcoach-v2/infrastructure

# Créer un virtualenv
python -m venv .venv

# Activer (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Installer
pip install -r requirements.txt
```

### Étape 5 — Déployer le backend

```bash
cd fitcoach-v2/infrastructure

# Déployer en environnement dev
cdk deploy -c env=dev --require-approval never
```

**Sortie attendue :**
```
✅  FitCoachV2-dev

Outputs:
FitCoachV2-dev.ApiUrl = https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/
FitCoachV2-dev.UserPoolId = us-east-1_XXXXXXXXX
FitCoachV2-dev.UserPoolClientId = xxxxxxxxxxxxxxxxxxxxxxxxxx
FitCoachV2-dev.FrontendBucket = fitcoach-dev-frontend
FitCoachV2-dev.CloudFrontUrl = https://dxxxxxxxxxx.cloudfront.net
```

> 📝 **Notez l'ApiUrl et le CloudFrontUrl**

### Étape 6 — Build et déployer le frontend

```bash
cd fitcoach-v2/frontend

# Installer les dépendances
npm install

# Créer le fichier .env avec l'URL de l'API
echo VITE_API_URL=https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod > .env

# Build
npm run build

# Upload sur S3
aws s3 sync dist/ s3://fitcoach-dev-frontend --delete

# Invalider le cache CloudFront (optionnel mais recommandé)
aws cloudfront create-invalidation --distribution-id EXXXXXXXXXX --paths "/*"
```

> Pour trouver le Distribution ID :
> ```bash
> aws cloudfront list-distributions --query "DistributionList.Items[?Comment=='FitCoachV2-dev'].Id" --output text
> ```

### Étape 7 — Tester

Ouvrir le **CloudFrontUrl** dans votre navigateur. L'application est live !

---

## Déploiement multi-environnement

```bash
# Dev (auto sur push develop)
cdk deploy -c env=dev

# Staging (après tests intégration)
cdk deploy -c env=staging

# Production (après approval)
cdk deploy -c env=prod
```

Chaque environnement crée ses propres ressources isolées :
- `fitcoach-dev-*` / `fitcoach-staging-*` / `fitcoach-prod-*`

---

## Commandes utiles

| Commande | Description |
|----------|-------------|
| `cdk synth -c env=dev` | Voir le template CloudFormation généré |
| `cdk diff -c env=dev` | Voir les changements avant deploy |
| `cdk destroy -c env=dev` | Supprimer toutes les ressources |
| `aws logs tail /aws/lambda/fitcoach-dev-master-agent --follow` | Voir les logs en live |
| `aws logs tail /aws/lambda/fitcoach-dev-pose-analysis --follow` | Logs pose analysis |

---

## Dépannage

| Problème | Solution |
|----------|----------|
| `AccessDeniedException` Bedrock | Activer Claude 3 Haiku (Étape 2) |
| `cdk bootstrap` échoue | Vérifier `aws sts get-caller-identity` |
| CORS error | Vérifier que VITE_API_URL finit par `/prod/` |
| Lambda timeout | Image trop grande → réduire qualité webcam |
| Webcam ne marche pas | HTTPS requis (CloudFront OK, HTTP non) |
| `Module not found` Lambda | Vérifier que le code est dans `../backend` relatif à `infrastructure/` |

---

## Coûts estimés

| Service | Estimation (usage modéré) |
|---------|--------------------------|
| Lambda (2 fonctions) | ~$1/mois |
| API Gateway | ~$3.50/mois |
| DynamoDB (7 tables, on-demand) | ~$2/mois |
| Bedrock Claude Haiku | ~$3/mois (200 appels/jour) |
| S3 + CloudFront | ~$1/mois |
| Cognito | Gratuit (< 50k MAU) |
| **Total** | **~$10/mois** |

> 💡 Coût nul si pas d'utilisation (100% pay-per-use).

---

## Nettoyage

```bash
cd fitcoach-v2/infrastructure
cdk destroy -c env=dev
```

Cela supprime TOUTES les ressources AWS créées (Lambda, API Gateway, DynamoDB, S3, CloudFront, Cognito).
