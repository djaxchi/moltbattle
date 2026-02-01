#!/bin/bash

echo "═══════════════════════════════════════════════"
echo "USER STORY 2: Accept Combat Invitation"
echo "═══════════════════════════════════════════════"
echo ""
echo "As a second user, I want to accept a combat invitation so that I can compete against the creator."
echo ""

API_URL="http://localhost:8000"

if [ -z "$1" ]; then
    echo "Creating test combat first..."
    CREATE_RESPONSE=$(curl -s -X POST $API_URL/api/combats \
      -H "Content-Type: application/json" \
      -d '{"handle": "AgentAlpha"}')
    COMBAT_CODE=$(echo $CREATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['code'])")
    echo "Test combat code: $COMBAT_CODE"
    echo ""
else
    COMBAT_CODE=$1
fi

echo "Step 1: Accepting combat $COMBAT_CODE as AgentBeta..."
ACCEPT_RESPONSE=$(curl -s -X POST $API_URL/api/combats/$COMBAT_CODE/accept \
  -H "Content-Type: application/json" \
  -d '{"handle": "AgentBeta"}')

STATE=$(echo $ACCEPT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['state'])")

if [ "$STATE" == "ACCEPTED" ]; then
    echo "✅ Combat accepted successfully!"
    echo "   State: $STATE"
else
    echo "❌ Failed to accept combat"
    echo "   Response: $ACCEPT_RESPONSE"
    exit 1
fi

echo ""
echo "Step 2: Verifying both participants are registered..."
STATUS=$(curl -s $API_URL/api/combats/$COMBAT_CODE)
USER_A=$(echo $STATUS | python3 -c "import sys, json; print(json.load(sys.stdin)['userAHandle'])")
USER_B=$(echo $STATUS | python3 -c "import sys, json; print(json.load(sys.stdin)['userBHandle'])")

echo "   User A: $USER_A"
echo "   User B: $USER_B"

if [ "$USER_A" == "AgentAlpha" ] && [ "$USER_B" == "AgentBeta" ]; then
    echo "✅ Both participants verified"
else
    echo "❌ Participant verification failed"
    exit 1
fi

echo ""
echo "Step 3: Testing that combat cannot be accepted again..."
REJECT_RESPONSE=$(curl -s -X POST $API_URL/api/combats/$COMBAT_CODE/accept \
  -H "Content-Type: application/json" \
  -d '{"handle": "AgentGamma"}')

if echo $REJECT_RESPONSE | grep -q "detail"; then
    echo "✅ Correctly rejected duplicate acceptance"
else
    echo "❌ Should have rejected duplicate acceptance"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════"
echo "✅ USER STORY 2 PASSED"
echo "═══════════════════════════════════════════════"
echo ""
echo "Result: Combat $COMBAT_CODE accepted by AgentBeta"
echo "Next: Generate API keys to start the combat"
echo ""
echo "Save this for next test:"
echo "export COMBAT_CODE=$COMBAT_CODE"
