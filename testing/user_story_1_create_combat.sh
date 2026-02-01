#!/bin/bash

echo "═══════════════════════════════════════════════"
echo "USER STORY 1: Create Combat"
echo "═══════════════════════════════════════════════"
echo ""
echo "As a user, I want to create a new combat so that I can invite another agent to compete."
echo ""

API_URL="http://localhost:8000"

echo "Step 1: Creating combat as AgentAlpha..."
RESPONSE=$(curl -s -X POST $API_URL/api/combats \
  -H "Content-Type: application/json" \
  -d '{"handle": "AgentAlpha"}')

COMBAT_CODE=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['code'])")
COMBAT_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['combatId'])")
INVITE_URL=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['inviteUrl'])")

echo ""
echo "✅ Combat created successfully!"
echo "   Combat Code: $COMBAT_CODE"
echo "   Combat ID: $COMBAT_ID"
echo "   Invite URL: $INVITE_URL"
echo ""

echo "Step 2: Verifying combat status..."
STATUS=$(curl -s $API_URL/api/combats/$COMBAT_CODE)
STATE=$(echo $STATUS | python3 -c "import sys, json; print(json.load(sys.stdin)['state'])")

if [ "$STATE" == "CREATED" ]; then
    echo "✅ Combat is in CREATED state"
else
    echo "❌ Unexpected state: $STATE"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════"
echo "✅ USER STORY 1 PASSED"
echo "═══════════════════════════════════════════════"
echo ""
echo "Result: Combat created with code $COMBAT_CODE"
echo "Next: Share this code with another user to accept the combat"
echo ""
echo "Save this for next test:"
echo "export COMBAT_CODE=$COMBAT_CODE"
