curl -X POST http://localhost:10010/ -H "Content-Type: application/json" -d "{\"jsonrpc\": \"2.0\", \"id\": \"req-001\", \"method\": \"message/send\", \"params\": {\"session_id\": \"test-session-02\", \"message\": {\"role\": \"user\", \"parts\": [{\"kind\": \"text\", \"text\": \"Create a 10-slide pitch deck for a fintech startup targeting seed investors.'\"}], \"messageId\": \"msg-001\"}}}"

pause