# ============================================
# Script de deploiement FitCoach AI sur AWS
# ============================================
# Prerequis :
#   - AWS CLI configure (aws configure)
#   - AWS CDK installe (npm install -g aws-cdk)
#   - Node.js installe
#   - Python 3.12+
#
# Executer depuis la racine du projet :
#   .\deploy.ps1
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FitCoach AI - Deploiement AWS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Etape 1 : Installer les dependances CDK
Write-Host "`n[1/3] Preparation infrastructure..." -ForegroundColor Yellow
Set-Location infrastructure
pip install -r requirements.txt -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: pip install echoue" -ForegroundColor Red
    Set-Location ..
    exit 1
}
Write-Host "  Dependances CDK OK" -ForegroundColor Green

# Etape 2 : Bootstrap CDK (premiere fois seulement)
Write-Host "`n[2/3] CDK Bootstrap..." -ForegroundColor Yellow
npx cdk bootstrap
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Bootstrap deja fait ou erreur non-bloquante, on continue..." -ForegroundColor DarkYellow
}

# Etape 3 : Deployer
Write-Host "`n[3/3] Deploiement CDK..." -ForegroundColor Yellow
npx cdk deploy --require-approval never
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
Write-Host "`nPour le frontend :" -ForegroundColor Yellow
Write-Host "  1. Copiez l'ApiUrl" -ForegroundColor White
Write-Host "  2. Editez frontend/.env.production -> VITE_API_URL=<ApiUrl>" -ForegroundColor White
Write-Host "  3. cd frontend; npm run build" -ForegroundColor White
Write-Host "  4. Hebergez frontend/dist sur S3+CloudFront ou Amplify" -ForegroundColor White
