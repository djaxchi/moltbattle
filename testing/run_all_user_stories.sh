#!/bin/bash

# Run all user story test scripts
# This script executes all three user story tests sequentially

echo "=========================================="
echo "Running All User Story Tests"
echo "=========================================="
echo ""

# Track results
PASSED=0
FAILED=0

# Array of test scripts
TESTS=(
  "user_story_online_matchmaking.sh"
  "user_story_versus_combat.sh"
  "user_story_profile_management.sh"
)

# Run each test
for test in "${TESTS[@]}"; do
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Running: $test"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  if ./$test; then
    echo ""
    echo "✅ $test PASSED"
    ((PASSED++))
  else
    echo ""
    echo "❌ $test FAILED"
    ((FAILED++))
  fi
  
  echo ""
  # Small pause between tests
  sleep 2
done

# Summary
echo ""
echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
echo "Total tests: ${#TESTS[@]}"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
  echo "✅ All tests passed!"
  exit 0
else
  echo "❌ Some tests failed!"
  exit 1
fi
