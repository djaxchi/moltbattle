#!/bin/bash

echo "═══════════════════════════════════════════════"
echo "USER STORY 3: Generate API Keys & Start Combat"
echo "═══════════════════════════════════════════════"
echo ""
echo "As a combat participant, I want to generate API keys so that both agents can connect and compete."
echo ""

API_URL="http://localhost:8000"

if [ -z "$1" ]; then
    echo "Setting up test combat..."
    CREATE_RESPONSE=$(curl -s -X POST $API_URL/api/combats \
      -H "Content-Type: application/json" \
      -d '{"handle": "AgentAlpha"}')
    COMBAT_CODE=$(echo $CREATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['code'])")
    
    curl -s -X POST $API_URL/api/combats/$COMBAT_CODE/accept \
      -H "Content-Type: application/json" \
      -d '{"handle": "AgentBeta"}' > /dev/null
    echo "Test combat code: $COMBAT_CODE"
    echo ""
else
    COMBAT_CODE=$1
fi

echo "Step 1: Generating API keys for combat $COMBAT_CODE..."
KEYS_RESPONSE=$(curl -s -X POST $API_URL/api/combats/$COMBAT_CODE/keys)

KEY_A=$(echo $KEYS_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['keyA'])")
KEY_B=$(echo $KEYS_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['keyB'])")

if [ -z "$KEY_A" ] || [ -z "$KEY_B" ]; then
    echo "❌ Failed to generate keys"
    echo "   Response: $KEYS_RESPONSE"
    exit 1
fi

echo "✅ API keys generated successfully!"
echo "   Key A (AgentAlpha): ${KEY_A:0:30}..."
echo "   Key B (AgentBeta):  ${KEY_B:0:30}..."
echo ""

echo "Step 2: Verifying combat has started..."
sleep 1
STATUS=$(curl -s $API_URL/api/combats/$COMBAT_CODE)
STATE=$(echo $STATUS | python3 -c "import sys, json; print(json.load(sys.stdin)['state'])")
QUESTION=$(echo $STATUS | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('question', {}).get('prompt', 'None'))")

if [ "$STATE" == "RUNNING" ]; then
    echo "✅ Combat is RUNNING"
    echo "   Question assigned: $QUESTION"
else
    echo "❌ Combat not in RUNNING state: $STATE"
    exit 1
fi

echo ""
echo "Step 3: Testing that keys cannot be issued again..."
REJECT_RESPONSE=$(curl -s -X POST $API_URL/api/combats/$COMBAT_CODE/keys)

if echo $REJECT_RESPONSE | grep -q "detail"; then
    echo "✅ Correctly rejected duplicate key generation"
else
    echo "❌ Should have rejected duplicate key generation"
    exit 1
fi

echo ""
echo "Step 4: Verifying agents can authenticate..."
ME_RESPONSE=$(curl -s $API_URL/agent/me \
  -H "Authorization: Bearer $KEY_A")

if echo $ME_RESPONSE | grep -q "prompt"; then
    echo "✅ Agent A authenticated successfully"
else
    echo "❌ Agent A authentication failed"
    exit 1
fi

ME_RESPONSE_B=$(curl -s $API_URL/agent/me \
  -H "Authorization: Bearer $KEY_B")

if echo $ME_RESPONSE_B | grep -q "prompt"; then
    echo "✅ Agent B authenticated successfully"
else
    echo "❌ Agent B authentication failed"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════"
echo "✅ USER STORY 3 PASSED"
echo "═══════════════════════════════════════════════"
echo ""
echo "Result: Combat $COMBAT_CODE is RUNNING with API keys issued"
echo "Next: Agents can now submit their answers"
echo ""
echo "Save these for next test:"
echo "export COMBAT_CODE=$COMBAT_CODE"
echo "export KEY_A=$KEY_A"
echo "export KEY_B=$KEY_B"
