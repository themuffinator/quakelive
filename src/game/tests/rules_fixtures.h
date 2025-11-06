#ifndef GAME_TESTS_RULES_FIXTURES_H
#define GAME_TESTS_RULES_FIXTURES_H

#include "fixture_runner.h"

// Sample suite demonstrating the harness plumbing.
game_fixture_result_t GT_RunSampleRulesFixtures(void);

// Item-centric suite covering pickup metadata and proximity checks.
game_fixture_result_t GT_RunItemRulesFixtures(void);

#endif // GAME_TESTS_RULES_FIXTURES_H
