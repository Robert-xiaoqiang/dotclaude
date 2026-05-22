# PreToolUse(Edit|Write) hook — blocks Claude from editing secret files (Windows/PowerShell).
# Reads the hook event JSON on stdin; exit 2 = block (stderr shown to Claude).
$ErrorActionPreference = 'Stop'

$raw = [Console]::In.ReadToEnd()
try { $data = $raw | ConvertFrom-Json } catch { exit 0 }

$path = ''
if ($data.tool_input -and $data.tool_input.file_path) { $path = [string]$data.tool_input.file_path }
if (-not $path) { exit 0 }

$patterns = @('\.env($|\.)', '\.pem$', '\.key$', 'id_rsa', 'credentials', '\.secret')
foreach ($p in $patterns) {
    if ($path -match "(?i)$p") {
        [Console]::Error.WriteLine("Blocked: '$path' looks like a secret file; edit it manually.")
        exit 2
    }
}
exit 0
