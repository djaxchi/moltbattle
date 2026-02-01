#!/bin/bash


echo "================================"
echo "User Story 7: Timeout & Redirect"
echo "================================"
echo ""

API_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

echo "1. Creating combat with 10 second timeout..."
CREATE_RESPONSE=$(curl -s -X POST "$API_URL/api/combats" \
  -H "Content-Type: application/json" \
  -d '{"handle":"TimeoutTesterA","opponentHandle":"TimeoutTesterB"}')

CODE=$(echo $CREATE_RESPONSE | grep -o '"code":"[^"]*"' | cut -d'"' -f4)
INVITE_URL=$(echo $CREATE_RESPONSE | grep -o '"inviteUrl":"[^"]*"' | cut -d'"' -f4)

if [ -z "$CODE" ]; then
  echo "❌ Failed to create combat"
  echo "Response: $CREATE_RESPONSE"
  exit 1
fi

echo "✓ Combat created with code: $CODE"
echo ""

echo "2. Accepting combat..."
ACCEPT_RESPONSE=$(curl -s -X POST "$API_URL/api/combats/$CODE/accept" \
  -H "Content-Type: application/json" \
  -d '{"handle":"TimeoutTesterB"}')

ACCEPT_OK=$(echo $ACCEPT_RESPONSE | grep -o '"ok":true')
if [ -z "$ACCEPT_OK" ]; then
  echo "❌ Failed to accept combat"
  exit 1
fi

echo "✓ Combat accepted"
echo ""

echo "3. Issuing API keys (starting timer)..."
KEYS_RESPONSE=$(curl -s -X POST "$API_URL/api/combats/$CODE/keys")
KEY_A=$(echo $KEYS_RESPONSE | grep -o '"keyA":"[^"]*"' | cut -d'"' -f4)

if [ -z "$KEY_A" ]; then
  echo "❌ Failed to issue keys"
  exit 1
fi

echo "✓ Combat started - timer running"
echo ""

echo "4. Checking initial status..."
sleep 2
STATUS=$(curl -s "$API_URL/api/combats/$CODE")
STATE=$(echo $STATUS | grep -o '"state":"[^"]*"' | cut -d'"' -f4)

if [ "$STATE" != "RUNNING" ]; then
  echo "❌ Expected state RUNNING, got: $STATE"
  exit 1
fi

echo "✓ Combat is RUNNING"
COUNTDOWN=$(echo $STATUS | grep -o '"countdownSeconds":[0-9]*' | cut -d':' -f2)
echo "  Countdown: ${COUNTDOWN}s remaining"
echo ""

echo "5. Waiting for timeout (this will take ~60 seconds)..."
echo "   Note: In production, you would set TIME_LIMIT_SECONDS=10 for faster testing"
echo ""

for i in {1..7}; do
  sleep 10
  STATUS=$(curl -s "$API_URL/api/combats/$CODE")
  STATE=$(echo $STATUS | grep -o '"state":"[^"]*"' | cut -d'"' -f4)
  COUNTDOWN=$(echo $STATUS | grep -o '"countdownSeconds":[0-9]*' | cut -d':' -f2)
  
  echo "   [$(($i * 10))s] State: $STATE, Countdown: ${COUNTDOWN}s"
  
  if [ "$STATE" = "EXPIRED" ]; then
    echo ""
    echo "✓ Combat expired due to timeout!"
    break
  fi
done

echo ""
echo "6. Verifying final timeout state..."
FINAL_STATUS=$(curl -s "$API_URL/api/combats/$CODE")
FINAL_STATE=$(echo $FINAL_STATUS | grep -o '"state":"[^"]*"' | cut -d'"' -f4)

if [ "$FINAL_STATE" != "EXPIRED" ]; then
  echo "❌ Expected state EXPIRED, got: $FINAL_STATE"
  exit 1
fi

echo "✓ State correctly set to EXPIRED"

SUBMISSIONS=$(echo $FINAL_STATUS | grep -o '"submissionsStatus":{[^}]*}')
if echo "$SUBMISSIONS" | grep -q "timeout"; then
  echo "✓ Submission status shows timeout for non-responders"
else
  echo "❌ Expected timeout status in submissions"
  exit 1
fi

echo ""
echo "================================"
echo "✅ USER STORY 7 PASSED"
echo "================================"
echo ""
echo "Summary:"
echo "- Combat created and accepted"
echo "- Timer started with key issuance"
echo "- No submissions made"
echo "- Combat automatically expired after timeout"
echo "- Non-responders marked with timeout status (LOSS)"
echo "- Frontend will redirect to home page after 5 seconds"
echo ""
echo "To test UI redirect, visit: $FRONTEND_URL/dashboard/$CODE"
echo "The page will show timeout message and redirect to home."
echo ""
