param (
    [string]$OutDir = ".\respuestas\parte2"
)

# Directorio donde está ESTE script (.ps1)
$ScriptDir = $PSScriptRoot

# Candidatos a main.py (no usar comas dentro de Join-Path)
$candidatePaths = @(
    (Join-Path $ScriptDir "main.py")
    (Join-Path $ScriptDir "respuestas\parte2\main.py")
    (Join-Path $ScriptDir "..\main.py")
    (Join-Path $ScriptDir "..\..\main.py")
    (Join-Path (Get-Location) "main.py")
    (Join-Path (Get-Location) "..\main.py")
)

$MainPy = $null
foreach ($p in $candidatePaths) {
    if (Test-Path -LiteralPath $p) {
        $MainPy = (Resolve-Path -LiteralPath $p).Path
        break
    }
}

if (-not $MainPy) {
    Write-Error "No se encontró main.py. Colocá runscript.ps1 en la misma carpeta que main.py o ajustá la ruta."
    exit 1
}

# Crear carpeta de salida si no existe
if (-not (Test-Path -LiteralPath $OutDir)) {
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
}

# Instalar dependencias si hay requirements.txt (al lado del .ps1 o al lado del main.py)
$Req1 = Join-Path $ScriptDir "requirements.txt"
$Req2 = Join-Path (Split-Path -Parent $MainPy) "requirements.txt"
if (Test-Path $Req1) { python -m pip install -r $Req1 }
elseif (Test-Path $Req2) { python -m pip install -r $Req2 }

# Ejecutar ETL
python $MainPy --out $OutDir

Write-Host "CSV generados en: $OutDir"
