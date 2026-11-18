param(
    [Parameter(Mandatory=$true)][string]$IdentityName,
    [Parameter(Mandatory=$true)][string]$Publisher,
    [string]$PublisherDisplayName='Keys Web & IT',
    [string]$PackageDisplayName='LabelFix 4×6',
    [string]$Version='1.2.1.0',
    [switch]$StoreSubmission
)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$exeDir=Join-Path $root 'dist/LabelFix4x6'
if (!(Test-Path (Join-Path $exeDir 'LabelFix4x6.exe'))) { throw 'First run python setup_cxfreeze.py build_exe to generate dist/LabelFix4x6.' }
if ([string]::IsNullOrWhiteSpace($PackageDisplayName)) { throw 'Package display name must not be empty' }
if ($StoreSubmission -and ($Publisher -match 'Preview|TEMP|TEST|Placeholder' -or $IdentityName -match 'PREVIEW|TEMP|TEST|Placeholder')) {
    throw 'Store production mode requires EXACT Name and Publisher from Partner Center > App identity.'
}
$makeappx=Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin\*\x64\MakeAppx.exe" -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1
if (!$makeappx) { throw 'MakeAppx.exe not found: install Windows SDK/MSIX tools.' }
$stage=Join-Path $root 'dist/msix-stage'
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $stage | Out-Null
Copy-Item (Join-Path $exeDir '*') -Destination $stage -Recurse -Force
New-Item -ItemType Directory -Force -Path (Join-Path $stage 'Assets') | Out-Null
Copy-Item (Join-Path $root 'branding/store/*.png') (Join-Path $stage 'Assets')
function E([string]$value){ return [System.Security.SecurityElement]::Escape($value) }
$name=E $IdentityName; $pub=E $Publisher; $display=E $PublisherDisplayName; $appName=E $PackageDisplayName; $ver=E $Version
$manifest=@"
<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
         xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
         xmlns:uap10="http://schemas.microsoft.com/appx/manifest/uap/windows10/10"
         xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"
         IgnorableNamespaces="uap uap10 rescap">
  <Identity Name="$name" Publisher="$pub" Version="$ver" ProcessorArchitecture="x64" />
  <Properties>
    <DisplayName>$appName</DisplayName>
    <PublisherDisplayName>$display</PublisherDisplayName>
    <Description>Local shipping label PDF converter by Keys Web &amp; IT</Description>
    <Logo>Assets\StoreLogo.png</Logo>
  </Properties>
  <Resources><Resource Language="en-us" /></Resources>
  <Dependencies><TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.19041.0" MaxVersionTested="10.0.26100.0" /></Dependencies>
  <Applications>
    <Application Id="LabelFix4x6" Executable="LabelFix4x6.exe" uap10:RuntimeBehavior="packagedClassicApp" uap10:TrustLevel="mediumIL">
      <uap:VisualElements DisplayName="$appName" Description="Convert PDF shipping labels to 4x6"
        Square150x150Logo="Assets\Square150x150Logo.png" Square44x44Logo="Assets\Square44x44Logo.png" BackgroundColor="#FFFFFF" />
    </Application>
  </Applications>
  <Capabilities><rescap:Capability Name="runFullTrust"/></Capabilities>
</Package>
"@
$manifestPath=Join-Path $stage 'AppxManifest.xml'
[System.IO.File]::WriteAllText($manifestPath,$manifest,(New-Object System.Text.UTF8Encoding($false)))
[xml](Get-Content -Raw $manifestPath) | Out-Null
$outFile=Join-Path $root 'dist/LabelFix4x6-Store-Preview-UNSIGNED.msix'
if ($StoreSubmission) { $outFile=Join-Path $root "dist/LabelFix4x6-Store-$Version-UNSIGNED.msix" }
& $makeappx.FullName pack /o /d $stage /p $outFile
if ($LASTEXITCODE -ne 0) { throw 'MakeAppx packaging failed' }
Write-Host "Created $outFile (UNSIGNED; Store can re-sign AFTER certification; do not sideload this draft)."
Get-FileHash $outFile -Algorithm SHA256 | Format-List
