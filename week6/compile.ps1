# compile.ps1
$all = @{}
Get-ChildItem *.json | % { $all[$_.Name] = $_ | Get-Content | ConvertFrom-Json }
$all | ConvertTo-Json -Depth 4 | Out-File idor_report.json -Encoding utf8