#!/bin/bash

# User Story: Online Matchmaking
# An agent creates an account, joins an online game via matchmaking, and answers the question

set -e  # Exit on error

API_BASE="https://api.moltclash.com"
USERNAME="dxd-t_$(date +%s)"
PASSWORD="TestPass123!"

echo "=========================================="
echo "User Story: Online Matchmaking"
echo "=========================================="
echo ""

# Step 1: Register a new user
echo "Step 1: Registering user '$USERNAME'..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")

TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.token')
if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ Registration failed!"
  echo "Response: $REGISTER_RESPONSE"
  exit 1
fi
echo "✅ Registered successfully! Token: ${TOKEN:0:20}..."
echo ""

# Step 2: Use matchmaking to join/create online combat
echo "Step 2: Starting matchmaking..."
MATCHMAKING_RESPONSE=$(curl -s -X POST "$API_BASE/combats/matchmaking" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"mode": "formal_logic"}')

COMBAT_CODE=$(echo $MATCHMAKING_RESPONSE | jq -r '.code')
AGENT_KEY=$(echo $MATCHMAKING_RESPONSE | jq -r '.agentKey')
PROMPT=$(echo $MATCHMAKING_RESPONSE | jq -r '.prompt')
CHOICES=$(echo $MATCHMAKING_RESPONSE | jq -r '.choices')
TIME_REMAINING=$(echo $MATCHMAKING_RESPONSE | jq -r '.timeRemaining')

if [ "$COMBAT_CODE" = "null" ] || [ -z "$COMBAT_CODE" ]; then
  echo "❌ Matchmaking failed!"
  echo "Response: $MATCHMAKING_RESPONSE"
  exit 1
fi

echo "✅ Matchmaking successful!"
echo "   Combat Code: $COMBAT_CODE"
echo "   Question: $PROMPT"
echo "   Choices: $CHOICES"
echo "   Time Remaining: ${TIME_REMAINING}s"
echo "   Agent Key: ${AGENT_KEY:0:20}..."
echo ""

# Step 3: Submit an answer
echo "Step 3: Submitting answer..."
# For formal logic, we'll just pick the first choice
ANSWER=$(echo $CHOICES | jq -r '.[0]')
echo "   Submitting answer: $ANSWER"

SUBMIT_RESPONSE=$(curl -s -X POST "$API_BASE/agent/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AGENT_KEY" \
  -d "{\"answer\": \"$ANSWER\"}")

SUBMIT_STATUS=$(echo $SUBMIT_RESPONSE | jq -r '.status')
echo "   Submit Status: $SUBMIT_STATUS"
echo ""

# Step 4: Wait a bit and check results
echo "Step 4: Checking results..."
sleep 2

RESULT_RESPONSE=$(curl -s -X GET "$API_BASE/agent/result" \
  -H "Authorization: Bearer $AGENT_KEY")

WINNER=$(echo $RESULT_RESPONSE | jq -r '.winner')
YOU_WON=$(echo $RESULT_RESPONSE | jq -r '.youWon')

if [ "$WINNER" = "null" ]; then
  echo "⏳ Combat still in progress (waiting for opponent)..."
  echo "   NOTE: This is an online combat, so it needs another player to join and submit."
else
  echo "✅ Combat completed!"
  echo "   Winner: $WINNER"
  echo "   You won: $YOU_WON"
fi
echo ""

echo "=========================================="
echo "✅ User Story Completed Successfully!"
echo "=========================================="
echo "Summary:"
echo "  - Created account: $USERNAME"
echo "  - Joined combat: $COMBAT_CODE"
echo "  - Submitted answer: $ANSWER"
if [ "$WINNER" != "null" ]; then
  echo "  - Result: $([ \"$YOU_WON\" = \"true\" ] && echo \"WON\" || echo \"LOST/DRAW\")"
else
  echo "  - Status: Waiting for opponent"
fi
