# 📋 TODO — Bonnes pratiques DevOps à implémenter (V2)

## 🎯 Objectif

Passer d'un prototype hackathon à une architecture **production-ready** avec séparation des environnements, CI/CD, monitoring, sécurité et scalabilité.

---

## 1. 🌍 Séparation des environnements

### Comptes AWS séparés (AWS Organizations)

| Environnement | Compte AWS | Usage |
|---------------|-----------|-------|
| **dev** | `fitcoach-dev` | Développement local, tests unitaires |
| **staging** | `fitcoach-staging` | Tests d'intégration, QA, pré-prod |
| **prod** | `fitcoach-prod` | Production utilisateurs finaux |

- [ ] Créer une AWS Organization avec 3 comptes
- [ ] Configurer AWS SSO pour accès centralisé
- [ ] Utiliser des SCPs (Service Control Policies) pour limiter les actions en prod
- [ ] Chaque environnement a son propre stack CDK avec des paramètres différents

### Variables par environnement

- [ ] Créer un fichier `cdk.context.json` par environnement
- [ ] Paramétrer : taille mémoire Lambda, timeout, throttling API Gateway
- [ ] Noms de ressources préfixés : `fitcoach-dev-*`, `fitcoach-staging-*`, `fitcoach-prod-*`

---

## 2. 🔄 CI/CD Pipeline

### Pipeline GitHub Actions (ou CodePipeline)

```
push → lint → test → build → deploy dev → tests intégration → deploy staging → approval → deploy prod
```

- [ ] **Lint** : ESLint (frontend) + flake8/ruff (backend)
- [ ] **Tests unitaires** : Vitest (frontend) + pytest (backend)
- [ ] **Tests d'intégration** : Appels API sur environnement staging
- [ ] **Build** : `npm run build` + packaging Lambda
- [ ] **Deploy** : `cdk deploy` avec rôle IAM dédié par environnement
- [ ] **Approval gate** : Validation manuelle avant prod
- [ ] **Rollback automatique** : Si health check échoue post-deploy

### Branching strategy

| Branche | Environnement | Déploiement |
|---------|---------------|-------------|
| `feature/*` | — | PR uniquement |
| `develop` | dev | Auto |
| `staging` | staging | Auto |
| `main` | prod | Après approval |

---

## 3. 🏗️ Infrastructure as Code (IaC) avancée

- [ ] **Stacks séparées** : Network, Auth, Compute, Storage, Monitoring
- [ ] **Constructs réutilisables** : Créer des L3 constructs pour les patterns récurrents
- [ ] **State locking** : Utiliser CDK Pipelines pour éviter les conflits
- [ ] **Drift detection** : Alerter si l'infra réelle diverge du code
- [ ] **Tagging obligatoire** : `Environment`, `Project`, `Owner`, `CostCenter`

---

## 4. 🔒 Sécurité

### Authentification & Autorisation

- [ ] Activer l'authorizer Cognito sur API Gateway (pas juste provisionné)
- [ ] Implémenter les JWT tokens dans le frontend
- [ ] Configurer les scopes OAuth2 par endpoint
- [ ] Rate limiting par utilisateur (pas juste global)

### Secrets & Configuration

- [ ] Utiliser AWS Secrets Manager pour les clés sensibles
- [ ] Pas de secrets en dur dans le code (déjà OK)
- [ ] Rotation automatique des credentials
- [ ] Variables d'environnement Lambda via SSM Parameter Store

### Réseau

- [ ] WAF (Web Application Firewall) devant API Gateway
- [ ] Throttling API Gateway : 1000 req/s burst, 500 req/s sustained
- [ ] Validation des inputs côté Lambda (taille image max, types)
- [ ] Headers de sécurité sur le frontend (CSP, HSTS, X-Frame-Options)

### Least Privilege

- [ ] Auditer les policies IAM (pas de `*` en resource)
- [ ] Séparer les rôles Lambda (un rôle par fonction)
- [ ] Activer CloudTrail pour l'audit

---

## 5. 📊 Monitoring & Observabilité

### Logs

- [ ] Structured logging (JSON) dans toutes les Lambdas
- [ ] Log levels : DEBUG (dev), INFO (staging), WARN (prod)
- [ ] Retention des logs : 7j (dev), 30j (staging), 90j (prod)
- [ ] CloudWatch Log Insights pour les requêtes

### Métriques

- [ ] Dashboard CloudWatch par environnement
- [ ] Métriques custom : score moyen posture, latence analyse, erreurs Bedrock
- [ ] Métriques business : nombre d'analyses/jour, plannings générés

### Alertes

- [ ] Alerte si taux d'erreur Lambda > 5%
- [ ] Alerte si latence P99 > 10s
- [ ] Alerte si DynamoDB throttling
- [ ] Alerte si coût journalier dépasse le budget
- [ ] Notification via SNS → Slack/Email

### Tracing

- [ ] Activer AWS X-Ray sur Lambda + API Gateway
- [ ] Tracer les appels Bedrock (latence, tokens utilisés)
- [ ] Correlation ID dans chaque requête (header X-Request-Id)

---

## 6. 🚀 Performance & Scalabilité

### Lambda

- [ ] Provisioned Concurrency pour pose-analysis (cold start critique)
- [ ] Lambda Layers pour MediaPipe (réduire taille du package)
- [ ] ARM64 (Graviton2) pour réduire coûts et améliorer perf
- [ ] Optimiser la taille des images envoyées (compression côté client)

### API Gateway

- [ ] Caching API Gateway pour `/generate-planning` (mêmes params = même résultat)
- [ ] Request validation (JSON Schema) au niveau API Gateway
- [ ] Compression gzip activée

### Frontend

- [ ] CDN CloudFront devant S3 (cache global)
- [ ] Lazy loading des pages (code splitting)
- [ ] Service Worker pour mode offline partiel
- [ ] Compression images WebP avant envoi

### Base de données

- [ ] DynamoDB Auto Scaling (si passage en PROVISIONED pour la prod)
- [ ] DAX (DynamoDB Accelerator) si lectures fréquentes
- [ ] TTL sur les sessions anciennes (nettoyage auto)

---

## 7. 🧪 Tests

### Pyramide de tests

| Niveau | Outil | Couverture cible |
|--------|-------|-----------------|
| Unitaire | pytest + Vitest | 80% |
| Intégration | pytest + API calls | Tous les endpoints |
| E2E | Playwright/Cypress | Parcours utilisateur complet |
| Performance | Artillery/k6 | Charge 100 users simultanés |
| Sécurité | OWASP ZAP | Scan automatique |

- [ ] Tests unitaires backend (mock MediaPipe, mock Bedrock)
- [ ] Tests unitaires frontend (composants React)
- [ ] Tests d'intégration API (staging)
- [ ] Tests de charge (vérifier les limites Lambda)
- [ ] Tests de sécurité automatisés dans la CI

---

## 8. 💰 Gestion des coûts

- [ ] AWS Budgets : alerte à 80% et 100% du budget mensuel
- [ ] Tags de coûts sur toutes les ressources
- [ ] Rapport Cost Explorer hebdomadaire
- [ ] Environnement dev/staging éteint la nuit (scheduled scaling)
- [ ] Reserved Capacity pour Bedrock si usage prévisible

---

## 9. 📦 Gestion des releases

- [ ] Semantic Versioning (vX.Y.Z)
- [ ] Changelog automatique (conventional commits)
- [ ] Feature flags (AWS AppConfig) pour déploiement progressif
- [ ] Canary deployments : 10% du trafic sur la nouvelle version
- [ ] Rollback automatique si métriques dégradées

---

## 10. 📖 Documentation

- [ ] Architecture Decision Records (ADR) pour chaque choix technique
- [ ] Runbook pour les incidents courants
- [ ] API documentation (OpenAPI/Swagger) auto-générée
- [ ] Onboarding guide pour nouveaux développeurs
- [ ] Diagramme d'architecture à jour (architecture-v2.drawio)

---

## Priorités d'implémentation

| Phase | Items | Effort |
|-------|-------|--------|
| **P0 — Immédiat** | Séparation env, CI/CD basique, Cognito authorizer, logs structurés | 1-2 jours |
| **P1 — Court terme** | WAF, X-Ray, alertes, tests unitaires, CloudFront | 3-5 jours |
| **P2 — Moyen terme** | Canary deploy, feature flags, tests E2E, Lambda Layers | 1-2 semaines |
| **P3 — Long terme** | Multi-région, DAX, Reserved Capacity, audit sécurité complet | 1 mois+ |
