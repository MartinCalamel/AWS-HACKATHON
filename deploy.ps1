# ============================================
# Script de déploiement FitCoach AI sur AWS
# ============================================
# Prérequis :
#   - AWS CLI configuré (aws configure)
#   - AWS CDK installé (npm install -g aws-cdk)
#   - Docker Desktop lancé (pour la Lambda MediaPipe)
#   - Node.js installé
#   - Python 3.12+
#
# Exécuter depuis la racine du projet :
#   .\deploy.ps1
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FitCoach AI - Deploiement AWS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Vérifier Docker
Write-Host "`n[0/3] Verification Docker..." -ForegroundColor Yellow
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: Docker n'est pas lance. Lancez Docker Desktop et reessayez." -ForegroundColor Red
    exit 1
}
Write-Host "  Docker OK" -ForegroundColor Green

# Étape 1 : Installer les dépendances CDK
Write-Host "`n[1/3] Preparation infrastructure..." -ForegroundColor Yellow
Set-Location infrastructure
pip install -r requirements.txt -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: pip install echoue" -ForegroundColor Red
    Set-Location ..
    exit 1
}
Write-Host "  Dependances CDK OK" -ForegroundColor Green

# Étape 2 : Bootstrap CDK (première fois seulement)
Write-Host "`n[2/3] CDK Bootstrap..." -ForegroundColor Yellow
cdk bootstrap
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Bootstrap deja fait ou erreur non-bloquante, on continue..." -ForegroundColor DarkYellow
}

# Étape 3 : Déployer
Write-Host "`n[3/3] Deploiement CDK..." -ForegroundColor Yellow
cdk deploy --require-approval never
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: Deploiement echoue" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Deploiement termine !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nVerifiez les outputs ci-dessus pour :" -ForegroundColor White
Write-Host "  - ApiUrl : URL de l'API backend" -ForegroundColor White
Write-Host "  - UserPoolId : ID du pool Cognito" -ForegroundColor White
Write-Host "  - UserPoolClientId : ID du client Cognito" -ForegroundColor White
Write-Host "`nPour le frontend, mettez l'ApiUrl dans:" -ForegroundColor Yellow
Write-Host "  frontend/.env.production -> VITE_API_URL=<ApiUrl>" -ForegroundColor White
Write-Host "  Puis: cd frontend; npm run build" -ForegroundColor White
Write-Host "  Hebergez le dossier frontend/dist sur S3+CloudFront ou Amplify" -ForegroundColor White
