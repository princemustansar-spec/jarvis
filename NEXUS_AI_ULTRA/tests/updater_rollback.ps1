# Filesystem test under PowerShell Core; Windows process detection is explicitly mocked.
$ErrorActionPreference='Stop'
function Get-CimInstance { @() }
$root=Join-Path ([IO.Path]::GetTempPath()) ('nexus-rollback-test-'+[Guid]::NewGuid().ToString('N'))
$dest=Join-Path $root 'NEXUS_AI_ULTRA'
$backup=$dest+'.backup-test'
New-Item -ItemType Directory -Path $dest,$backup -Force | Out-Null
Set-Content (Join-Path $dest 'run.py') 'new code'
Set-Content (Join-Path $backup 'run.py') 'old code'
Set-Content (Join-Path $dest 'memory.sqlite3') 'latest user data'
Set-Content (Join-Path $backup 'memory.sqlite3') 'older user data'
Set-Content (Join-Path $dest '.env') 'TEST_ONLY_NOT_A_REAL_SECRET=latest'
@{destination=$dest;managed=@('run.py')}|ConvertTo-Json|Set-Content (Join-Path $backup '.nexus-update-backup.json')
$script=Join-Path $PSScriptRoot '../install_update.ps1'
& $script -Destination $dest -Rollback -BackupPath $backup
if((Get-Content (Join-Path $dest 'run.py') -Raw).Trim() -ne 'old code'){throw 'Code rollback failed'}
if((Get-Content (Join-Path $dest 'memory.sqlite3') -Raw).Trim() -ne 'latest user data'){throw 'Latest user data lost'}
if((Get-Content (Join-Path $dest '.env') -Raw).Trim() -ne 'TEST_ONLY_NOT_A_REAL_SECRET=latest'){throw 'Environment data lost'}
'Rollback filesystem test passed: old code restored, latest user data/environment preserved.'
Remove-Item $root -Recurse -Force
