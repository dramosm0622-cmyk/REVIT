# Instalador de CAD-MCP para AutoCAD / Civil 3D + Claude Desktop
# Copie este archivo (y INSTALAR.bat) dentro de la carpeta del proyecto cad-mcp,
# junto a pyproject.toml, y ejecute INSTALAR.bat con doble clic.

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$utf8 = New-Object System.Text.UTF8Encoding $false

function Paso($n, $t) { Write-Host ""; Write-Host "[$n] $t" -ForegroundColor Cyan }
function Ok($t)  { Write-Host "    OK  $t" -ForegroundColor Green }
function Mal($t) { Write-Host "    ERROR  $t" -ForegroundColor Red; Read-Host "Presione Enter para salir"; exit 1 }

Write-Host "=============================================" -ForegroundColor Yellow
Write-Host "  Conexion de CAD-MCP con AutoCAD / Civil 3D" -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Yellow

# 1) Carpeta del proyecto
Paso 1 "Revisando la carpeta del proyecto"
# busca la carpeta que contiene src\server.py (aqui o en subcarpetas, p. ej. CAD-MCP-main\CAD-MCP-main)
$hit = Get-ChildItem -Path $root -Filter 'server.py' -Recurse -Depth 3 -ErrorAction SilentlyContinue |
       Where-Object { $_.Directory.Name -eq 'src' -and (Test-Path (Join-Path $_.Directory.Parent.FullName 'pyproject.toml')) } |
       Select-Object -First 1
if (-not $hit) {
    Mal "No se encontro src\server.py. Copie INSTALAR.bat e instalar_cad_mcp.ps1 dentro de la carpeta CAD-MCP-main (la que tiene la carpeta src)."
}
$root = $hit.Directory.Parent.FullName
$server = $hit.FullName
$config = Join-Path $root 'src\config.json'
Ok "Proyecto encontrado en $root"

# 2) Python
Paso 2 "Buscando Python 3.10 o superior"
$py = $null
foreach ($cand in @('py', 'python')) {
    $cmd = Get-Command $cand -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source -notlike '*WindowsApps*') {
        try {
            $args0 = @('-c', 'import sys; print(sys.executable); print(sys.version_info[0]*100+sys.version_info[1])')
            if ($cand -eq 'py') { $args0 = @('-3') + $args0 }
            $out = & $cmd.Source @args0 2>$null
            if ($out -and [int]$out[1] -ge 310) { $py = $out[0].Trim(); break }
        } catch { }
    }
}
if (-not $py) {
    Mal "No se encontro Python 3.10+. Instalelo desde https://www.python.org/downloads/ marcando 'Add Python to PATH' y vuelva a ejecutar INSTALAR.bat."
}
Ok "Python: $py"

# 3) Dependencias
Paso 3 "Instalando dependencias (puede tardar unos minutos)"
& $py -m pip install --upgrade pip --quiet
& $py -m pip install -e "$root" --quiet
if ($LASTEXITCODE -ne 0) {
    $req = Join-Path $root 'requirements.txt'
    if (Test-Path $req) { & $py -m pip install -r "$req" --quiet } else { & $py -m pip install "mcp>=1.12,<2" "pywin32>=306" "pydantic>=2.0.0" "Pillow>=10.0.0" --quiet }
    if ($LASTEXITCODE -ne 0) { Mal "Fallo la instalacion de dependencias con pip." }
}
& $py -c "import win32com.client, mcp, pydantic, PIL; print('dependencias ok')"
if ($LASTEXITCODE -ne 0) { Mal "Las dependencias no quedaron instaladas correctamente." }
Ok "Dependencias instaladas"

# 4) config.json del servidor
Paso 4 "Configurando el tipo de CAD (AutoCAD / Civil 3D)"
if (Test-Path $config) {
    $txt = [System.IO.File]::ReadAllText($config, [System.Text.Encoding]::UTF8)
    $cfg = $txt | ConvertFrom-Json
    if (-not $cfg.cad) { $cfg | Add-Member -NotePropertyName cad -NotePropertyValue ([pscustomobject]@{}) }
    $cfg.cad | Add-Member -NotePropertyName type -NotePropertyValue 'AUTOCAD' -Force
    $cfg.cad | Add-Member -NotePropertyName startup_wait_time -NotePropertyValue 40 -Force
    Copy-Item $config "$config.bak" -Force
    [System.IO.File]::WriteAllText($config, ($cfg | ConvertTo-Json -Depth 10), $utf8)
    Ok "src\config.json -> type = AUTOCAD, startup_wait_time = 40 (copia en config.json.bak)"
} else {
    Write-Host "    AVISO  No hay src\config.json; se usaran los valores por defecto." -ForegroundColor Yellow
}

# 5) Configuracion de Claude Desktop
Paso 5 "Registrando el MCP 'CAD' en Claude Desktop"
$destinos = @(Join-Path $env:APPDATA 'Claude\claude_desktop_config.json')
Get-ChildItem (Join-Path $env:LOCALAPPDATA 'Packages') -Directory -Filter 'Claude_*' -ErrorAction SilentlyContinue | ForEach-Object {
    $destinos += (Join-Path $_.FullName 'LocalCache\Roaming\Claude\claude_desktop_config.json')
}
foreach ($dest in $destinos) {
    $dir = Split-Path -Parent $dest
    if (-not (Test-Path $dir)) {
        if ($dest -like "$env:APPDATA*") { New-Item -ItemType Directory -Path $dir -Force | Out-Null } else { continue }
    }
    if (Test-Path $dest) {
        Copy-Item $dest "$dest.bak" -Force
        $raw = [System.IO.File]::ReadAllText($dest, [System.Text.Encoding]::UTF8)
        if ($raw.Trim()) { $cc = $raw | ConvertFrom-Json } else { $cc = [pscustomobject]@{} }
    } else {
        $cc = [pscustomobject]@{}
    }
    if (-not $cc.mcpServers) { $cc | Add-Member -NotePropertyName mcpServers -NotePropertyValue ([pscustomobject]@{}) -Force }
    $entrada = [pscustomobject]@{ command = $py; args = @($server) }
    $cc.mcpServers | Add-Member -NotePropertyName CAD -NotePropertyValue $entrada -Force
    [System.IO.File]::WriteAllText($dest, ($cc | ConvertTo-Json -Depth 10), $utf8)
    Ok "Configurado: $dest"
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "  LISTO. Ahora:" -ForegroundColor Green
Write-Host "  1. Abra AutoCAD o Civil 3D con un dibujo abierto." -ForegroundColor Green
Write-Host "  2. Cierre Claude Desktop por completo (tambien desde el" -ForegroundColor Green
Write-Host "     icono junto al reloj) y vuelva a abrirlo." -ForegroundColor Green
Write-Host "  3. En el chat debe aparecer la herramienta 'CAD'." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Read-Host "Presione Enter para cerrar"
