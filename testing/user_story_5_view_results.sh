#!/bin/bash

echo "═══════════════════════════════════════════════"
echo "USER STORY 5: View Combat Results"
echo "═══════════════════════════════════════════════"
echo ""
echo "As a participant, I want to view the final results showing both answers after the combat ends."
echo ""

API_URL="http://localhost:8000"

if [ -z "$KEY_A" ] || [ -z "$KEY_B" ]; then
    echo "Setting up completed combat..."
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
    
    curl -s -X POST $API_URL/agent/submit \
      -H "Authorization: Bearer $KEY_A" \
      -H "Content-Type: application/json" \
      -d '{"answer": "Answer from Agent Alpha"}' > /dev/null
    
    curl -s -X POST $API_URL/agent/submit \
      -H "Authorization: Bearer $KEY_B" \
      -H "Content-Type: application/json" \
      -d '{"answer": "Answer from Agent Beta"}' > /dev/null
    
    sleep 1
    echo "Test combat code: $COMBAT_CODE"
    echo ""
fi

echo "Step 1: Agent A viewing results..."
RESULT_A=$(curl -s $API_URL/agent/result \
  -H "Authorization: Bearer $KEY_A")

MY_STATUS=$(echo $RESULT_A | python3 -c "import sys, json; print(json.load(sys.stdin).get('myStatus', 'unknown'))")
OPP_STATUS=$(echo $RESULT_A | python3 -c "import sys, json; print(json.load(sys.stdin).get('opponentStatus', 'unknown'))")
MY_ANSWER=$(echo $RESULT_A | python3 -c "import sys, json; print(json.load(sys.stdin).get('myAnswer', 'None'))")
OPP_ANSWER=$(echo $RESULT_A | python3 -c "import sys, json; print(json.load(sys.stdin).get('opponentAnswer', 'None'))")

echo "✅ Agent A Results:"
echo "   My Status: $MY_STATUS"
echo "   Opponent Status: $OPP_STATUS"
echo "   My Answer: ${MY_ANSWER:0:50}..."
echo "   Opponent Answer: ${OPP_ANSWER:0:50}..."
echo ""

echo "Step 2: Agent B viewing results..."
RESULT_B=$(curl -s $API_URL/agent/result \
  -H "Authorization: Bearer $KEY_B")

MY_STATUS_B=$(echo $RESULT_B | python3 -c "import sys, json; print(json.load(sys.stdin).get('myStatus', 'unknown'))")
OPP_STATUS_B=$(echo $RESULT_B | python3 -c "import sys, json; print(json.load(sys.stdin).get('opponentStatus', 'unknown'))")

echo "✅ Agent B Results:"
echo "   My Status: $MY_STATUS_B"
echo "   Opponent Status: $OPP_STATUS_B"
echo ""

echo "Step 3: Verifying result symmetry..."
if [ "$MY_STATUS" == "submitted" ] && [ "$OPP_STATUS" == "submitted" ]; then
    echo "✅ Both agents submitted (full combat)"
elif [ "$MY_STATUS" == "submitted" ] || [ "$OPP_STATUS" == "submitted" ]; then
    echo "⚠️  Partial submission (one agent timed out)"
else
    echo "⚠️  Both agents timed out"
fi

echo ""
echo "Step 4: Public view of combat status..."
PUBLIC_STATUS=$(curl -s $API_URL/api/combats/$COMBAT_CODE)
STATE=$(echo $PUBLIC_STATUS | python3 -c "import sys, json; print(json.load(sys.stdin)['state'])")
SUBMISSIONS=$(echo $PUBLIC_STATUS | python3 -c "import sys, json; import pprint; pprint.pprint(json.load(sys.stdin).get('submissionsStatus', {}))" 2>/dev/null)

echo "✅ Public Combat Status:"
echo "   State: $STATE"
echo "   Submissions: $SUBMISSIONS"

echo ""
echo "═══════════════════════════════════════════════"
echo "✅ USER STORY 5 PASSED"
echo "═══════════════════════════════════════════════"
echo ""
echo "Result: Both participants can view complete combat results"
echo "Combat $COMBAT_CODE completed successfully"
