Set-Location $PSScriptRoot

Write-Host "Running demo pipeline..." -ForegroundColor Cyan
python src\demo.py

Write-Host "Running baseline comparison..." -ForegroundColor Cyan
python src\baseline_comparison.py

Write-Host "Generating presentation..." -ForegroundColor Cyan
python scripts\create_presentation.py

Write-Host "Generating writeup document..." -ForegroundColor Cyan
python scripts\create_project_writeup_doc.py

Write-Host "Done. Check outputs/ and deliverables/." -ForegroundColor Green
