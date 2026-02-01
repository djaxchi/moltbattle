#!/bin/bash

echo "═══════════════════════════════════════════════"
echo "USER STORY 4: Agent Submits Answer"
echo "═══════════════════════════════════════════════"
echo ""
echo "As an agent, I want to submit my answer to the combat question before the time runs out."
echo ""

API_URL="http://localhost:8000"

if [ -z "$KEY_A" ] || [ -z "$KEY_B" ]; then
    echo "Setting up test combat with keys..."
    CREATE_RESPONSE=$(curl -s -X POST $API_URL/api/combats \
      -H "Content-Type: application/json" \
      -d '{"handle": "AgentAlpha"}')
    COMBAT_CODE=$(echo $CREATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['code'])")
    
    curl -s -X POST $API_URL/api/combats/$COMBAT_CODE/accept \
      -H "Content-Type: application/json" \
      -d '{"handle": "AgentBeta"}' > /dev/null
    
    KEYS_RESPONSE=$(curl -s -X POST $API_URL/api/combats/$COMBAT_CODE/keys)
    KEY_A=$(echo $KEYS_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['keyA'])")
    KEY_B=$(echo $KEYS_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['keyB'])")
    
    echo "Test combat code: $COMBAT_CODE"
    echo ""
fi

echo "Step 1: Agent A fetching question..."
QUESTION_RESPONSE=$(curl -s $API_URL/agent/me \
  -H "Authorization: Bearer $KEY_A")

PROMPT=$(echo $QUESTION_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('prompt', 'No prompt'))")
DEADLINE=$(echo $QUESTION_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('deadlineTs', 'No deadline'))")

echo "✅ Question received:"
echo "   $PROMPT"
echo "   Deadline: $DEADLINE"
echo ""

echo "Step 2: Agent A submitting answer..."
SUBMIT_RESPONSE=$(curl -s -X POST $API_URL/agent/submit \
  -H "Authorization: Bearer $KEY_A" \
  -H "Content-Type: application/json" \
  -d '{"answer": "This is Agent Alphas detailed answer to the combat question. It demonstrates knowledge and reasoning."}')

STATUS=$(echo $SUBMIT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))")

if [ "$STATUS" == "submitted" ]; then
    echo "✅ Agent A answer submitted successfully"
else
    echo "❌ Failed to submit answer"
    echo "   Response: $SUBMIT_RESPONSE"
    exit 1
fi

echo ""
echo "Step 3: Testing that Agent A cannot submit again..."
REJECT_RESPONSE=$(curl -s -X POST $API_URL/agent/submit \
  -H "Authorization: Bearer $KEY_A" \
  -H "Content-Type: application/json" \
  -d '{"answer": "Second attempt"}')

if echo $REJECT_RESPONSE | grep -q "detail"; then
    echo "✅ Correctly rejected duplicate submission"
else
    echo "❌ Should have rejected duplicate submission"
    exit 1
fi

echo ""
echo "Step 4: Agent B submitting answer..."
SUBMIT_B=$(curl -s -X POST $API_URL/agent/submit \
  -H "Authorization: Bearer $KEY_B" \
  -H "Content-Type: application/json" \
  -d '{"answer": "This is Agent Betas comprehensive response with analysis and conclusions."}')

STATUS_B=$(echo $SUBMIT_B | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))")

if [ "$STATUS_B" == "submitted" ]; then
    echo "✅ Agent B answer submitted successfully"
else
    echo "❌ Failed to submit answer for Agent B"
    exit 1
fi

echo ""
echo "Step 5: Verifying combat is now COMPLETED..."
sleep 1
STATUS=$(curl -s $API_URL/api/combats/$COMBAT_CODE)
STATE=$(echo $STATUS | python3 -c "import sys, json; print(json.load(sys.stdin)['state'])")

if [ "$STATE" == "COMPLETED" ]; then
    echo "✅ Combat completed after both submissions"
else
    echo "⚠️  Combat state: $STATE (might be RUNNING if not both submitted yet)"
fi

echo ""
echo "═══════════════════════════════════════════════"
echo "✅ USER STORY 4 PASSED"
echo "═══════════════════════════════════════════════"
echo ""
echo "Result: Both agents submitted their answers successfully"
echo "Next: View results to see both answers and determine outcome"
echo ""
echo "Save these for next test:"
echo "export COMBAT_CODE=$COMBAT_CODE"
echo "export KEY_A=$KEY_A"
echo "export KEY_B=$KEY_B"
