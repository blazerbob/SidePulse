$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$lib = Join-Path $root 'src\lib'
$temp = Join-Path $env:TEMP 'SidePulse-LibreHardwareMonitor.zip'
$url = 'https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases/download/v0.9.6/LibreHardwareMonitor.zip'

New-Item -ItemType Directory -Force -Path $lib | Out-Null
Write-Host 'Downloading official LibreHardwareMonitor runtime...'
Invoke-WebRequest -Uri $url -OutFile $temp
$extract = Join-Path $env:TEMP 'SidePulse-LHM'
if (Test-Path $extract) { Remove-Item $extract -Recurse -Force }
Expand-Archive -Path $temp -DestinationPath $extract -Force
$dll = Get-ChildItem -Path $extract -Filter 'LibreHardwareMonitorLib.dll' -Recurse | Select-Object -First 1
if (-not $dll) { throw 'LibreHardwareMonitorLib.dll was not found in the downloaded archive.' }
Get-ChildItem -Path $extract -Filter '*.dll' -Recurse | ForEach-Object {
    Copy-Item $_.FullName (Join-Path $lib $_.Name) -Force
}
Remove-Item $temp -Force -ErrorAction SilentlyContinue
Remove-Item $extract -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Installed: $(Join-Path $lib 'LibreHardwareMonitorLib.dll')"
