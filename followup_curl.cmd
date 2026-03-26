@echo off
echo ===================================================
echo Testing Conversational Memory and Document Editing via CURL
echo ===================================================

echo.
echo [1/2] Step 1: Initial Document Creation...
echo Sending prompt: "Create a 3-slide pitch deck for a new AI fitness app called 'FitBot'."
curl -X POST http://localhost:10010/ -H "Content-Type: application/json" -d "{\"jsonrpc\": \"2.0\", \"id\": \"req-001\", \"method\": \"message/send\", \"params\": {\"session_id\": \"followup-curl-test\", \"message\": {\"role\": \"user\", \"parts\": [{\"kind\": \"text\", \"text\": \"Create a 3-slide pitch deck for a new AI fitness app called 'FitBot'.\"}], \"messageId\": \"msg-001\"}}}"

echo.
echo.
echo Waiting 15 seconds for the file to be generated...
timeout /t 15 /nobreak > nul

echo.
echo [2/2] Step 2: The Follow-Up Request (Editing)...
echo Sending prompt: "Change the second slide to focus exclusively on our $9.99/month premium subscription model instead."
curl -X POST http://localhost:10010/ -H "Content-Type: application/json" -d "{\"jsonrpc\": \"2.0\", \"id\": \"req-002\", \"method\": \"message/send\", \"params\": {\"session_id\": \"followup-curl-test\", \"message\": {\"role\": \"user\", \"parts\": [{\"kind\": \"text\", \"text\": \"Change the second slide to focus exclusively on our $9.99/month premium subscription model instead.\"}], \"messageId\": \"msg-002\"}}}"

echo.
echo.
echo Test complete! Check the /output directory for the updated presentation.
pause