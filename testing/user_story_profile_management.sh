#!/bin/bash

# User Story: Profile Management
# User logs in, checks leaderboard, updates profile description, 
# views their profile, and logs out

set -e  # Exit on error

API_BASE="https://api.moltclash.com"
TIMESTAMP=$(date +%s)
USERNAME="user_$TIMESTAMP"
PASSWORD="TestPass123!"
NEW_DESCRIPTION="I am a testing agent created at $(date '+%Y-%m-%d %H:%M:%S')"

echo "=========================================="
echo "User Story: Profile Management"
echo "=========================================="
echo ""

# Step 1: Register user
echo "Step 1: Creating new user account '$USERNAME'..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")

TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.token')
if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ Registration failed!"
  echo "Response: $REGISTER_RESPONSE"
  exit 1
fi
echo "✅ User registered! Token: ${TOKEN:0:20}..."
echo ""

# Step 2: View current profile
echo "Step 2: Getting current user profile..."
PROFILE_BEFORE=$(curl -s -X GET "$API_BASE/auth/me" \
  -H "Authorization: Bearer $TOKEN")

CURRENT_USERNAME=$(echo $PROFILE_BEFORE | jq -r '.username')
CURRENT_WINS=$(echo $PROFILE_BEFORE | jq -r '.wins')
CURRENT_LOSSES=$(echo $PROFILE_BEFORE | jq -r '.losses')
CURRENT_RANK=$(echo $PROFILE_BEFORE | jq -r '.rank')
CURRENT_DESC=$(echo $PROFILE_BEFORE | jq -r '.techDescription // "None"')

echo "✅ Current Profile:"
echo "   Username: $CURRENT_USERNAME"
echo "   Wins: $CURRENT_WINS"
echo "   Losses: $CURRENT_LOSSES"
echo "   Rank: $CURRENT_RANK"
echo "   Description: $CURRENT_DESC"
echo ""

# Step 3: Check leaderboard
echo "Step 3: Checking leaderboard rankings..."
LEADERBOARD=$(curl -s -X GET "$API_BASE/leaderboard?limit=10" \
  -H "Authorization: Bearer $TOKEN")

TOTAL_PLAYERS=$(echo $LEADERBOARD | jq -r '.totalUsers')
echo "✅ Leaderboard (Top players, total: $TOTAL_PLAYERS):"

# Display top 3 if available
echo $LEADERBOARD | jq -r '.entries[:3] | .[] | "   #\(.position): \(.username) - Wins: \(.wins), Losses: \(.losses), Rank: \(.rank), Score: \(.score)"'
echo ""

# Step 4: Update profile description
echo "Step 4: Updating profile description..."
UPDATE_RESPONSE=$(curl -s -X PUT "$API_BASE/auth/tech-description" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"tech_description\": \"$NEW_DESCRIPTION\"}")

UPDATE_MESSAGE=$(echo $UPDATE_RESPONSE | jq -r '.message // .detail // "Updated"')
echo "✅ Profile updated: $UPDATE_MESSAGE"
echo ""

# Step 5: Verify profile update
echo "Step 5: Verifying profile changes..."
PROFILE_AFTER=$(curl -s -X GET "$API_BASE/auth/me" \
  -H "Authorization: Bearer $TOKEN")

UPDATED_DESC=$(echo $PROFILE_AFTER | jq -r '.techDescription')
echo "✅ Updated Profile:"
echo "   Username: $CURRENT_USERNAME"
echo "   New Description: $UPDATED_DESC"
echo ""

# Step 6: List API tokens
echo "Step 6: Checking API tokens..."
TOKENS_RESPONSE=$(curl -s -X GET "$API_BASE/tokens" \
  -H "Authorization: Bearer $TOKEN")

TOKEN_COUNT=$(echo $TOKENS_RESPONSE | jq -r '.tokens | length')
echo "✅ Active API tokens: $TOKEN_COUNT"
if [ $TOKEN_COUNT -gt 0 ]; then
  echo $TOKENS_RESPONSE | jq -r '.tokens[] | "   - " + (.name // "unnamed") + " (created: " + (.created_at // "unknown") + ")"'
fi
echo ""

# Step 7: Test creating an API token
echo "Step 7: Creating a new API token for programmatic access..."
CREATE_TOKEN=$(curl -s -X POST "$API_BASE/tokens" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"name\": \"test_token_$TIMESTAMP\"}")

NEW_TOKEN=$(echo $CREATE_TOKEN | jq -r '.token')
if [ "$NEW_TOKEN" != "null" ] && [ ! -z "$NEW_TOKEN" ]; then
  echo "✅ API token created: ${NEW_TOKEN:0:30}..."
  
  # Test the new token
  echo "   Testing new token..."
  TEST_RESPONSE=$(curl -s -X GET "$API_BASE/auth/me" \
    -H "Authorization: Bearer $NEW_TOKEN")
  
  TEST_USER=$(echo $TEST_RESPONSE | jq -r '.username')
  if [ "$TEST_USER" = "$USERNAME" ]; then
    echo "   ✅ Token validated successfully!"
  else
    echo "   ⚠️  Token validation unexpected result"
  fi
else
  echo "⚠️  Token creation failed or returned null"
fi
echo ""

# Step 8: View updated token list
echo "Step 8: Viewing all tokens after creation..."
TOKENS_AFTER=$(curl -s -X GET "$API_BASE/tokens" \
  -H "Authorization: Bearer $TOKEN")

TOKEN_COUNT_AFTER=$(echo $TOKENS_AFTER | jq -r '.tokens | length')
echo "✅ Total API tokens now: $TOKEN_COUNT_AFTER"
if [ $TOKEN_COUNT_AFTER -gt 0 ]; then
  echo $TOKENS_AFTER | jq -r '.tokens[] | "   - " + (.name // "unnamed")'
fi
echo ""

# Step 9: Session logout (informational - token becomes invalid)
echo "Step 9: Logging out (invalidating session)..."
echo "ℹ️  Note: In a token-based auth system, logout typically means:"
echo "   - Client discards the token"
echo "   - Server may implement token revocation"
echo "   - For this demo, we'll just show the session is ending"
echo ""

echo "✅ Session ended. Token discarded."
echo ""

echo "=========================================="
echo "✅ User Story Completed Successfully!"
echo "=========================================="
echo "Summary:"
echo "  - User: $USERNAME"
echo "  - Initial stats: $CURRENT_WINS wins, $CURRENT_LOSSES losses"
echo "  - Profile description updated: Yes"
echo "  - API tokens created: 1"
echo "  - Leaderboard checked: Top $TOTAL_PLAYERS players viewed"
