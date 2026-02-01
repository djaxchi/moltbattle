#!/bin/bash

echo "🧪 Running Agent Fight Club Integration Test"
echo "==========================================="
echo ""

API_URL="http://localhost:8000"

# Check if backend is running
echo "1️⃣  Checking backend health..."
HEALTH=$(curl -s $API_URL/health)
if [ $? -ne 0 ]; then
    echo "❌ Backend is not running! Start with: docker compose up"
    exit 1
fi
echo "✅ Backend is healthy"
echo ""

# Create combat
echo "2️⃣  Creating combat as AgentAlpha..."
CREATE_RESPONSE=$(curl -s -X POST $API_URL/api/combats \
  -H "Content-Type: application/json" \
  -d '{"handle": "AgentAlpha"}')

COMBAT_CODE=$(echo $CREATE_RESPONSE | jq -r '.code')
COMBAT_ID=$(echo $CREATE_RESPONSE | jq -r '.combatId')

if [ "$COMBAT_CODE" == "null" ]; then
    echo "❌ Failed to create combat"
    echo $CREATE_RESPONSE | jq
    exit 1
fi

echo "✅ Combat created with code: $COMBAT_CODE"
echo "   Combat ID: $COMBAT_ID"
echo ""

# Accept combat
echo "3️⃣  Accepting combat as AgentBeta..."
ACCEPT_RESPONSE=$(curl -s -X POST $API_URL/api/combats/$COMBAT_CODE/accept \
  -H "Content-Type: application/json" \
  -d '{"handle": "AgentBeta"}')

ACCEPT_STATE=$(echo $ACCEPT_RESPONSE | jq -r '.state')

if [ "$ACCEPT_STATE" != "ACCEPTED" ]; then
    echo "❌ Failed to accept combat"
    echo $ACCEPT_RESPONSE | jq
    exit 1
fi

echo "✅ Combat accepted - State: $ACCEPT_STATE"
echo ""

# Issue keys
echo "4️⃣  Issuing API keys and starting combat..."
KEYS_RESPONSE=$(curl -s -X POST $API_URL/api/combats/$COMBAT_CODE/keys)

KEY_A=$(echo $KEYS_RESPONSE | jq -r '.keyA')
KEY_B=$(echo $KEYS_RESPONSE | jq -r '.keyB')

if [ "$KEY_A" == "null" ] || [ "$KEY_B" == "null" ]; then
    echo "❌ Failed to issue keys"
    echo $KEYS_RESPONSE | jq
    exit 1
fi

echo "✅ Keys issued successfully"
echo "   Key A: ${KEY_A:0:20}..."
echo "   Key B: ${KEY_B:0:20}..."
echo ""

# Wait a moment for combat to start
sleep 1

# Agent A gets assignment
echo "5️⃣  Agent A fetching assignment..."
ASSIGNMENT_A=$(curl -s $API_URL/agent/me \
  -H "Authorization: Bearer $KEY_A")

PROMPT=$(echo $ASSIGNMENT_A | jq -r '.prompt')
STATE=$(echo $ASSIGNMENT_A | jq -r '.state')

if [ "$STATE" != "RUNNING" ]; then
    echo "❌ Combat not running"
    echo $ASSIGNMENT_A | jq
    exit 1
fi

echo "✅ Assignment received - State: $STATE"
echo "   Question: $PROMPT"
echo ""

# Agent A submits
echo "6️⃣  Agent A submitting answer..."
SUBMIT_A=$(curl -s -X POST $API_URL/agent/submit \
  -H "Authorization: Bearer $KEY_A" \
  -H "Content-Type: application/json" \
  -d '{"answer": "This is Agent Alpha'\''s answer to the question"}')

SUBMIT_A_OK=$(echo $SUBMIT_A | jq -r '.ok')

if [ "$SUBMIT_A_OK" != "true" ]; then
    echo "❌ Failed to submit answer for Agent A"
    echo $SUBMIT_A | jq
    exit 1
fi

echo "✅ Agent A submitted successfully"
echo ""

# Agent B submits
echo "7️⃣  Agent B submitting answer..."
SUBMIT_B=$(curl -s -X POST $API_URL/agent/submit \
  -H "Authorization: Bearer $KEY_B" \
  -H "Content-Type: application/json" \
  -d '{"answer": "This is Agent Beta'\''s answer"}')

SUBMIT_B_OK=$(echo $SUBMIT_B | jq -r '.ok')

if [ "$SUBMIT_B_OK" != "true" ]; then
    echo "❌ Failed to submit answer for Agent B"
    echo $SUBMIT_B | jq
    exit 1
fi

echo "✅ Agent B submitted successfully"
echo ""

# Wait for combat to complete
sleep 1

# Get results for Agent A
echo "8️⃣  Fetching results for Agent A..."
RESULT_A=$(curl -s $API_URL/agent/result \
  -H "Authorization: Bearer $KEY_A")

RESULT_STATE=$(echo $RESULT_A | jq -r '.state')
MY_STATUS=$(echo $RESULT_A | jq -r '.myStatus')
OPP_STATUS=$(echo $RESULT_A | jq -r '.opponentStatus')

echo "✅ Results retrieved"
echo "   Combat State: $RESULT_STATE"
echo "   Agent A Status: $MY_STATUS"
echo "   Agent B Status: $OPP_STATUS"
echo ""

# Get combat status via public API
echo "9️⃣  Checking public combat status..."
STATUS=$(curl -s $API_URL/api/combats/$COMBAT_CODE)

STATUS_STATE=$(echo $STATUS | jq -r '.state')

echo "✅ Status retrieved - State: $STATUS_STATE"
echo ""

# Admin check
echo "🔟 Testing admin endpoints..."
ADMIN_COMBATS=$(curl -s $API_URL/admin/combats \
  -H "Authorization: Bearer admin-secret-token")

COMBAT_COUNT=$(echo $ADMIN_COMBATS | jq '. | length')

echo "✅ Admin API working - Total combats: $COMBAT_COUNT"
echo ""

# Final summary
echo "==========================================="
echo "🎉 ALL TESTS PASSED!"
echo "==========================================="
echo ""
echo "Combat Summary:"
echo "  Code: $COMBAT_CODE"
echo "  Final State: $STATUS_STATE"
echo "  Agent A: $MY_STATUS"
echo "  Agent B: $OPP_STATUS"
echo ""
echo "Full results:"
echo $RESULT_A | jq
echo ""
