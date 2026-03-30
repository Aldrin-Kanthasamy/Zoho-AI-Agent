<#
run-local.ps1 - helper to start local Postgres (if available), create DB,
install backend deps, and optionally start backend and frontend servers.

Usage:
  .\run-local.ps1 -StartBackend -StartFrontend
#>

param(
  [switch]$StartBackend,
  [switch]$StartFrontend
)

Write-Host "Detecting PostgreSQL service..."
$svc = $null
try {
  $svc = Get-Service -Name '*postgres*' -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Name
} catch {}

if ($svc) {
  Write-Host "Found service: $svc. Starting..."
  Start-Service -Name $svc -ErrorAction SilentlyContinue
} else {
  Write-Host "No Windows Postgres service found. Checking Program Files install..."
  $pgRoot = "$Env:ProgramFiles\PostgreSQL"
  if (Test-Path $pgRoot) {
    $ver = Get-ChildItem $pgRoot | Select-Object -First 1
    if ($ver) {
      $bin = Join-Path $ver.FullName 'bin'
      $data = Join-Path $ver.FullName 'data'
      $pgctl = Join-Path $bin 'pg_ctl.exe'
      if (Test-Path $pgctl) {
        Write-Host "Starting Postgres via pg_ctl from $bin..."
        & $pgctl -D $data start
      } else {
        Write-Host "pg_ctl not found under $bin. Please start PostgreSQL manually."
      }
    } else {
      Write-Host "No PostgreSQL version folder found under $pgRoot"
    }
  } else {
    Write-Host "PostgreSQL not installed. Please install from https://www.postgresql.org/download/windows/"
  }
}

Write-Host "Attempting to create database 'ai_agent_db' (if createdb is available)..."
if (Get-Command createdb -ErrorAction SilentlyContinue) {
  try {
    createdb -h localhost -U postgres ai_agent_db 2>$null | Out-Null
    Write-Host "createdb executed (may already exist)."
  } catch {
    Write-Host "Could not run createdb; you may need to create the DB manually."
  }
} else {
  Write-Host "createdb not found in PATH. If Postgres is installed, add its 'bin' folder to PATH or create DB with psql."
}

Write-Host "Installing backend dependencies..."
python -m pip install -r .\backend\requirements.txt

if ($StartBackend) {
  Write-Host "Starting backend (uvicorn) in a background process..."
  Start-Process -NoNewWindow -FilePath python -ArgumentList '-m', 'uvicorn', 'backend.app:app', '--reload', '--host', '0.0.0.0', '--port', '8000'
}

if ($StartFrontend) {
  Write-Host "Starting static frontend server on port 8080..."
  Start-Process -NoNewWindow -FilePath python -ArgumentList '-m', 'http.server', '8080' -WorkingDirectory (Resolve-Path .\frontend)
}

Write-Host "Helper script finished. Use -StartBackend and/or -StartFrontend to run servers." 
