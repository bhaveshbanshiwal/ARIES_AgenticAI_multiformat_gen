@echo off
echo Authenticating with Nasiko Platform...
nasiko login -k YOUR_ACTUAL_ACCESS_KEY -s YOUR_ACTUAL_ACCESS_SECRET --api-url http://localhost:8000/api/v1

echo.
echo [1/3] Testing Excel Generation...
nasiko chat send --url http://localhost:10010/ --session-id test-docs-01 --message "Build a sales performance tracker for Q1 with columns for rep name, deals closed, revenue, and quota attainment."

echo.
echo [2/3] Testing Word Document Generation...
nasiko chat send --url http://localhost:10010/ --session-id test-docs-01 --message "Write a competitive analysis report on three project management tools — include acomparison table and a recommendation."

echo.
echo [3/3] Testing PowerPoint Generation...
nasiko chat send --url http://localhost:10010/ --session-id test-docs-01 --message "Create a 10-slide pitch deck for a fintech startup targeting seed investors.'"

echo.
echo All tests completed!
pause