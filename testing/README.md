# Testing

End-to-end user story tests for combat flows.

## Prerequisites

Backend running on `http://localhost:8000`

## Run All Tests

```bash
./run_all_tests.sh
```

## Individual Tests

```bash
./user_story_1_create_combat.sh
./user_story_2_accept_combat.sh
./user_story_3_generate_keys.sh
./user_story_4_submit_answer.sh
./user_story_5_view_results.sh
./user_story_6_timeout.sh
./user_story_7_timeout_redirect.sh  # Takes ~60s
```

## Coverage

- Combat creation & acceptance
- API key generation
- Answer submission
- Results retrieval
- Timeout handling
- UI timeout redirect
