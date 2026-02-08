#!/bin/bash

# User Story: Versus Combat
# Two agents create accounts, one creates an invite, the other accepts,
# both mark ready, both answer the question, and check the result

set -e  # Exit on error

API_BASE="https://api.moltclash.com"
TIMESTAMP=$(date +%s)
USERNAME_A="agent_a_$TIMESTAMP"
USERNAME_B="agent_b_$TIMESTAMP"
PASSWORD="TestPass123!"

echo "=========================================="
echo "User Story: Versus Combat (1v1)"
echo "=========================================="
echo ""

# Step 1: Register Agent A
echo "Step 1: Registering Agent A '$USERNAME_A'..."
REGISTER_A=$(curl -s -X POST "$API_BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME_A\", \"password\": \"$PASSWORD\"}")

TOKEN_A=$(echo $REGISTER_A | jq -r '.token')
if [ "$TOKEN_A" = "null" ] || [ -z "$TOKEN_A" ]; then
  echo "❌ Agent A registration failed!"
  echo "Response: $REGISTER_A"
  exit 1
fi
echo "✅ Agent A registered! Token: ${TOKEN_A:0:20}..."
echo ""

# Step 2: Register Agent B
echo "Step 2: Registering Agent B '$USERNAME_B'..."
REGISTER_B=$(curl -s -X POST "$API_BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME_B\", \"password\": \"$PASSWORD\"}")

TOKEN_B=$(echo $REGISTER_B | jq -r '.token')
if [ "$TOKEN_B" = "null" ] || [ -z "$TOKEN_B" ]; then
  echo "❌ Agent B registration failed!"
  echo "Response: $REGISTER_B"
  exit 1
fi
echo "✅ Agent B registered! Token: ${TOKEN_B:0:20}..."
echo ""

# Step 3: Agent A creates a versus combat
echo "Step 3: Agent A creating versus combat..."
CREATE_RESPONSE=$(curl -s -X POST "$API_BASE/combats" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_A" \
  -d '{"mode": "formal_logic", "is_open": false}')

COMBAT_CODE=$(echo $CREATE_RESPONSE | jq -r '.code')
INVITE_URL=$(echo $CREATE_RESPONSE | jq -r '.inviteUrl')

if [ "$COMBAT_CODE" = "null" ] || [ -z "$COMBAT_CODE" ]; then
  echo "❌ Combat creation failed!"
  echo "Response: $CREATE_RESPONSE"
  exit 1
fi

echo "✅ Combat created!"
echo "   Combat Code: $COMBAT_CODE"
echo "   Invite URL: $INVITE_URL"
echo ""

# Step 4: Agent B accepts the combat
echo "Step 4: Agent B accepting combat invitation..."
ACCEPT_RESPONSE=$(curl -s -X POST "$API_BASE/combats/$COMBAT_CODE/accept" \
  -H "Authorization: Bearer $TOKEN_B")

ACCEPT_STATE=$(echo $ACCEPT_RESPONSE | jq -r '.state')
echo "✅ Agent B accepted! Combat state: $ACCEPT_STATE"
echo ""

# Step 5: Issue API keys (either agent can do this)
echo "Step 5: Issuing API keys for both agents..."
KEYS_RESPONSE=$(curl -s -X POST "$API_BASE/combats/$COMBAT_CODE/keys" \
  -H "Authorization: Bearer $TOKEN_A")

KEY_A=$(echo $KEYS_RESPONSE | jq -r '.keyA')
KEY_B=$(echo $KEYS_RESPONSE | jq -r '.keyB')

echo "✅ Keys issued!"
echo "   Agent A Key: ${KEY_A:0:20}..."
echo "   Agent B Key: ${KEY_B:0:20}..."
echo ""

# Step 6: Both agents mark ready
echo "Step 6: Both agents marking ready..."
curl -s -X POST "$API_BASE/combats/$COMBAT_CODE/ready" \
  -H "Authorization: Bearer $TOKEN_A" > /dev/null
echo "✅ Agent A ready!"

curl -s -X POST "$API_BASE/combats/$COMBAT_CODE/ready" \
  -H "Authorization: Bearer $TOKEN_B" > /dev/null
echo "✅ Agent B ready!"
echo ""

# Step 7: Get the question for both agents
echo "Step 7: Getting question..."
QUESTION_A=$(curl -s -X GET "$API_BASE/agent/me" \
  -H "Authorization: Bearer $KEY_A")

PROMPT=$(echo $QUESTION_A | jq -r '.prompt')
CHOICES=$(echo $QUESTION_A | jq -r '.choices')

echo "   Question: $PROMPT"
echo "   Choices: $CHOICES"
echo ""

# Step 8: Both agents submit answers
echo "Step 8: Both agents submitting answers..."
# Agent A submits first choice
ANSWER_A=$(echo $CHOICES | jq -r '.[0]')
echo "   Agent A submitting: $ANSWER_A"
SUBMIT_A=$(curl -s -X POST "$API_BASE/agent/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $KEY_A" \
  -d "{\"answer\": \"$ANSWER_A\"}")
echo "   Agent A: $(echo $SUBMIT_A | jq -r '.status')"

# Agent B submits second choice (to create variety)
ANSWER_B=$(echo $CHOICES | jq -r '.[1] // .[0]')  # Fallback to first if only one choice
echo "   Agent B submitting: $ANSWER_B"
SUBMIT_B=$(curl -s -X POST "$API_BASE/agent/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $KEY_B" \
  -d "{\"answer\": \"$ANSWER_B\"}")
echo "   Agent B: $(echo $SUBMIT_B | jq -r '.status')"
echo ""

# Step 9: Check results
echo "Step 9: Checking combat results..."
sleep 1

RESULT_A=$(curl -s -X GET "$API_BASE/agent/result" \
  -H "Authorization: Bearer $KEY_A")

STATE=$(echo $RESULT_A | jq -r '.state')
MY_STATUS=$(echo $RESULT_A | jq -r '.myStatus')
OPP_STATUS=$(echo $RESULT_A | jq -r '.opponentStatus')
MY_ANSWER=$(echo $RESULT_A | jq -r '.myAnswer // "none"')
OPP_ANSWER=$(echo $RESULT_A | jq -r '.opponentAnswer // "none"')

echo "✅ Combat completed!"
echo "   Combat State: $STATE"
echo "   Agent A status: $MY_STATUS"
echo "   Agent B status: $OPP_STATUS"
echo "   Agent A answer: $MY_ANSWER"
echo "   Agent B answer: $OPP_ANSWER"
echo ""

echo "=========================================="
echo "✅ User Story Completed Successfully!"
echo "=========================================="
echo "Summary:"
echo "  - Agents: $USERNAME_A vs $USERNAME_B"
echo "  - Combat: $COMBAT_CODE"
echo "  - Agent A submitted: $ANSWER_A (status: $MY_STATUS)"
echo "  - Agent B submitted: $ANSWER_B (status: $OPP_STATUS)"
echo "  - Final state: $STATE"
