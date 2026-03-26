@echo off
echo =======================================================
echo ⏱️ LIVE BENCHMARK: 5 Multi-Format Test Cases
echo =======================================================
echo.

:: TEST 1: Quick PPTX
echo [1/5] Testing Quick PPTX (3 slides on AI)...
powershell -NoProfile -Command "$timer = [Diagnostics.Stopwatch]::StartNew(); curl.exe -s -X POST http://localhost:10010/ -H 'Content-Type: application/json' -d '{\"jsonrpc\": \"2.0\", \"id\": \"req-1\", \"method\": \"message/send\", \"params\": {\"session_id\": \"test-01\", \"message\": {\"role\": \"user\", \"parts\": [{\"kind\": \"text\", \"text\": \"Create a simple 3-slide PPTX about artificial intelligence.\"}], \"messageId\": \"msg-1\"}}}' | Out-Null; $timer.Stop(); Write-Host \"   ✅ Done in $($timer.Elapsed.TotalSeconds) seconds\" -ForegroundColor Green"
echo.

:: TEST 2: Tabular XLSX
echo [2/5] Testing Tabular XLSX (Q1 Sales Tracker)...
powershell -NoProfile -Command "$timer = [Diagnostics.Stopwatch]::StartNew(); curl.exe -s -X POST http://localhost:10010/ -H 'Content-Type: application/json' -d '{\"jsonrpc\": \"2.0\", \"id\": \"req-2\", \"method\": \"message/send\", \"params\": {\"session_id\": \"test-02\", \"message\": {\"role\": \"user\", \"parts\": [{\"kind\": \"text\", \"text\": \"Build a sales performance tracker for Q1 with columns for rep name, revenue, and attainment.\"}], \"messageId\": \"msg-2\"}}}' | Out-Null; $timer.Stop(); Write-Host \"   ✅ Done in $($timer.Elapsed.TotalSeconds) seconds\" -ForegroundColor Green"
echo.

:: TEST 3: Standard DOCX
echo [3/5] Testing Standard DOCX (Competitive Analysis)...
powershell -NoProfile -Command "$timer = [Diagnostics.Stopwatch]::StartNew(); curl.exe -s -X POST http://localhost:10010/ -H 'Content-Type: application/json' -d '{\"jsonrpc\": \"2.0\", \"id\": \"req-3\", \"method\": \"message/send\", \"params\": {\"session_id\": \"test-03\", \"message\": {\"role\": \"user\", \"parts\": [{\"kind\": \"text\", \"text\": \"Write a brief competitive analysis report on three project management tools.\"}], \"messageId\": \"msg-3\"}}}' | Out-Null; $timer.Stop(); Write-Host \"   ✅ Done in $($timer.Elapsed.TotalSeconds) seconds\" -ForegroundColor Green"
echo.

:: TEST 4: Complex PPTX
echo [4/5] Testing Complex PPTX (Seed Investor Pitch Deck)...
powershell -NoProfile -Command "$timer = [Diagnostics.Stopwatch]::StartNew(); curl.exe -s -X POST http://localhost:10010/ -H 'Content-Type: application/json' -d '{\"jsonrpc\": \"2.0\", \"id\": \"req-4\", \"method\": \"message/send\", \"params\": {\"session_id\": \"test-04\", \"message\": {\"role\": \"user\", \"parts\": [{\"kind\": \"text\", \"text\": \"Create a 10-slide pitch deck for a fintech startup targeting seed investors.\"}], \"messageId\": \"msg-4\"}}}' | Out-Null; $timer.Stop(); Write-Host \"   ✅ Done in $($timer.Elapsed.TotalSeconds) seconds\" -ForegroundColor Green"
echo.

:: TEST 5: Visual DOCX w/ Chart
echo [5/5] Testing Visual DOCX (Report + Generated Chart)...
powershell -NoProfile -Command "$timer = [Diagnostics.Stopwatch]::StartNew(); curl.exe -s -X POST http://localhost:10010/ -H 'Content-Type: application/json' -d '{\"jsonrpc\": \"2.0\", \"id\": \"req-5\", \"method\": \"message/send\", \"params\": {\"session_id\": \"test-05\", \"message\": {\"role\": \"user\", \"parts\": [{\"kind\": \"text\", \"text\": \"Write a 1-page DOCX report on mobile OS market share and generate a pie chart to include in it.\"}], \"messageId\": \"msg-5\"}}}' | Out-Null; $timer.Stop(); Write-Host \"   ✅ Done in $($timer.Elapsed.TotalSeconds) seconds\" -ForegroundColor Green"
echo.

echo =======================================================
echo 🎉 All benchmarks complete!
echo =======================================================
pause