#!/bin/bash
# Run All User Story Tests

echo "╔═══════════════════════════════════════════════╗"
echo "║   AGENT FIGHT CLUB - USER STORY TEST SUITE   ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend is not running!"
    echo "   Please start the backend first:"
    echo "   cd backend && python3 main.py"
    exit 1
fi

echo "✅ Backend is running"
echo ""

TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
PASSED=0
FAILED=0

run_test() {
    TEST_NAME=$1
    TEST_SCRIPT=$2
    
    echo ""
    echo "▶️  Running: $TEST_NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if bash "$TESTS_DIR/$TEST_SCRIPT"; then
        ((PASSED++))
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ $TEST_NAME PASSED"
    else
        ((FAILED++))
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "❌ $TEST_NAME FAILED"
    fi
    
    sleep 1
}

# Run all user story tests
run_test "User Story 1: Create Combat" "user_story_1_create_combat.sh"
run_test "User Story 2: Accept Combat" "user_story_2_accept_combat.sh"
run_test "User Story 3: Generate Keys" "user_story_3_generate_keys.sh"
run_test "User Story 4: Submit Answer" "user_story_4_submit_answer.sh"
run_test "User Story 5: View Results" "user_story_5_view_results.sh"
run_test "User Story 6: Timeout Handling" "user_story_6_timeout.sh"

echo ""
echo "📝 Note: User Story 7 (Timeout Redirect) takes ~60s and is skipped in quick suite."
echo "   Run manually: ./user_story_7_timeout_redirect.sh"
echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║            TEST SUITE SUMMARY                 ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
echo "Total Tests: $((PASSED + FAILED))"
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED!"
    exit 0
else
    echo "⚠️  SOME TESTS FAILED"
    exit 1
fi
