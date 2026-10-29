# Real Windows install/update/rollback against disposable data. No microphone/model requests.
$ErrorActionPreference='Stop'
$root=Join-Path ([IO.Path]::GetTempPath()) ('nexus-updater-smoke-'+[Guid]::NewGuid().ToString('N'))
$dest=Join-Path $root 'NEXUS_AI_ULTRA'
New-Item -ItemType Directory -Path $dest -Force | Out-Null
$archive=Join-Path $root 'source.zip'
$updater=Join-Path $PSScriptRoot '../install_update.ps1'
try {
    & git -C (Join-Path $PSScriptRoot '../..') archive --format=zip --prefix=fixture/ "--output=$archive" HEAD NEXUS_AI_ULTRA
    # git archive runs from the repository root, avoiding any .git credentials/runtime data.
    if ($LASTEXITCODE -ne 0) { throw 'Could not create fixture archive.' }
    Set-Content (Join-Path $dest 'run.py') '# old version fixture'
    Set-Content (Join-Path $dest 'user.sqlite3') 'original data fixture'
    Set-Content (Join-Path $dest '.env') 'TEST_ONLY_NOT_A_SECRET=keep'
    & python -m venv (Join-Path $dest '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Fixture virtual environment failed.' }
    & $updater -Destination $dest -ArchivePath $archive -Revision 'ci-fixture'
    if ($LASTEXITCODE -ne 0) { throw 'Windows updater failed.' }
    if ((Get-Content (Join-Path $dest '.env') -Raw).Trim() -ne 'TEST_ONLY_NOT_A_SECRET=keep') { throw 'Environment fixture changed.' }
    if ((Get-Content (Join-Path $dest 'user.sqlite3') -Raw).Trim() -ne 'original data fixture') { throw 'User database fixture changed.' }
    if (-not (Test-Path (Join-Path $dest 'nexus\voice_online.py'))) { throw 'Voice upgrade missing.' }
    Set-Content (Join-Path $dest 'user.sqlite3') 'latest data fixture'
    $backups=@(Get-ChildItem $root -Directory | Where-Object Name -like 'NEXUS_AI_ULTRA.backup-*')
    if ($backups.Count -ne 1) { throw 'Expected a complete recognized backup.' }
    & $updater -Destination $dest -Rollback -BackupPath $backups[0].FullName
    if ((Get-Content (Join-Path $dest 'run.py') -Raw).Trim() -ne '# old version fixture') { throw 'Old code not restored.' }
    if ((Get-Content (Join-Path $dest 'user.sqlite3') -Raw).Trim() -ne 'latest data fixture') { throw 'Latest data not preserved.' }
    'Real Windows updater/backup/dependency install/rollback: passed.'
} finally {
    if (Test-Path $root) { Remove-Item $root -Recurse -Force }
}
