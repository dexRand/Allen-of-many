# Prepara content/ per build MkDocs locale (copia leggera delle note)
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (Test-Path content) { Remove-Item content -Recurse -Force }
New-Item -ItemType Directory -Path content | Out-Null

foreach ($dir in @("Canon", "404", "zz_CIcli", "zzz_Attachments")) {
    if (Test-Path $dir) {
        Copy-Item -Path $dir -Destination "content\$dir" -Recurse
    }
}

if (Test-Path "ALLEN.md") {
    Copy-Item -Path "ALLEN.md" -Destination "content\ALLEN.md"
}

Write-Host "content/ pronto. Esegui: mkdocs build"
