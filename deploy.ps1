# ============================================
# Script de déploiement FitCoach AI sur AWS
# ============================================
# Exécuter depuis la racine du projet :
#   .\deploy.ps1
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FitCoach AI - Déploiement AWS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Étape 1 : Build du frontend
Write-Host "`n[1/4] Build du frontend..." -ForegroundColor Yellow
Set-Location frontend
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: Build frontend échoué" -ForegroundColor Red
    exit 1
}
Set-Location ..

# Étape 2 : Installer les dépendances CDK
Write-Host "`n[2/4] Préparation infrastructure..." -ForegroundColor Yellow
Set-Location infrastructure
pip install -r requirements.txt -q

# Étape 3 : Bootstrap CDK (première fois seulement)
Write-Host "`n[3/4] CDK Bootstrap (si nécessaire)..." -ForegroundColor Yellow
cdk bootstrap
if ($LASTEXITCODE -ne 0) {
    Write-Host "ATTENTION: Bootstrap peut échouer si déjà fait, on continue..." -ForegroundColor DarkYellow
}

# Étape 4 : Déployer
Write-Host "`n[4/4] Déploiement CDK..." -ForegroundColor Yellow
cdk deploy --require-approval never
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR: Déploiement échoué" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Déploiement terminé !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nVérifiez les outputs ci-dessus pour :" -ForegroundColor White
Write-Host "  - FrontendUrl : URL de votre application" -ForegroundColor White
Write-Host "  - ApiUrl : URL de l'API backend" -ForegroundColor White
Write-Host "`nIMPORTANT: Après le premier déploiement :" -ForegroundColor Yellow
Write-Host "  1. Copiez l'ApiUrl depuis les outputs" -ForegroundColor White
Write-Host "  2. Mettez-la dans frontend/.env.production (VITE_API_URL=...)" -ForegroundColor White
Write-Host "  3. Relancez: cd frontend; npm run build; cd .." -ForegroundColor White
Write-Host "  4. Redéployez: cd infrastructure; cdk deploy; cd .." -ForegroundColor White
