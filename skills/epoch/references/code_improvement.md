# Skill: Code Improvement

**Goal**: Improve algorithm correctness and performance through iterative test-driven optimization

**Optimization Target**: Test passing rate (correctness phase), then execution time/memory (performance phase)

**Version**: Single-agent optimized (all workflows inlined)

---

## Overview

This skill improves code through test-driven optimization. Unlike other tasks, there is **no train/eval split**—all tests are visible. Optimization proceeds in two phases: correctness first (100% tests passing), then performance (optimize speed/memory).

**Key Principles:**
- ✅ Phase 1: Establish baseline (test infrastructure + initial implementation)
- ✅ Phase 2: Multi-round optimization (Stage 1: Correctness → Stage 2: Performance)
- ✅ All tests visible (no TRAIN/EVAL split)
- ❌ Never modify or remove tests
- ❌ Never hardcode test outputs

---

## Orchestrator: Multi-Round Coordination

### Universal Rules

1. **Config source of truth**: All settings from `epoch_run.yaml`
2. **Acceptance criteria**:
   - Correctness: More tests pass, no regressions
   - Performance: All tests pass + speed/memory improves >= 5%
3. **Retry logic**: One branch per round; retries on same branch; exceed max → close PR
4. **Phase transition**: Automatically switch Correctness → Performance at 100% pass rate

### Conventions

**Run ID**: `run-YYYYMMDD-HHMM`
**Branch**: `epoch/<project_slug>/<run_id>/round-<N>`

**PR Titles:**
- Round 1: `[Round 1] (Baseline: 85/100 tests) Initial implementation`
- Correctness: `[Round N] (tests: 85/100 → 92/100) Fix edge cases`
- Performance: `[Round N] (perf: 5234ms → 1456ms) Optimize with hash map`

### Workflow (same structure, phase-aware decisions)

---

## Phase 1: Baseline Establishment (Round 1)

### Seed Planner (Design)

**Task**: Design algorithm and test structure

**Deliverables:**
1. Algorithm design:
   - Problem description, constraints
   - Input/output interface
   - Core approach (brute force initially)
   - Expected complexity

2. Test structure:
   - Framework (pytest, unittest, LeetCode format)
   - Categories (basic, edge cases, performance)
   - Organization and coverage

3. Baseline: Correctness first, document limitations

### Baseline Executor (Implementation)

**Task**: Implement algorithm and test infrastructure

**Steps:**
1. Create algorithm in `projects/<slug>/`:
   - Core logic, validation, output formatting
   - Entry point matches `evaluation.cmd` from config
2. Create tests in `projects/<slug>/tests/`:
   - Test files matching `evaluation.test_cmd` from config
3. Run `test_cmd` to establish baseline metrics (tests_passed, tests_failed, execution_time)
4. Save baseline results to `<run_id>/baseline_metrics.json`

---

## Phase 2: Multi-Round Optimization (Rounds 2+)

### Optimization Strategy

**Code improvement follows a two-stage strategy within multi-round optimization:**

**Stage 1: Correctness** (if pass_rate < 100%)
- **Focus**: Get all tests passing
- **Investigation**: Analyze test failures
- **Implementation**: Fix bugs
- **Acceptance**: More tests pass, no regressions

**Stage 2: Performance** (if pass_rate == 100%)
- **Focus**: Improve speed/memory
- **Investigation**: Profile bottlenecks
- **Implementation**: Optimize algorithm
- **Acceptance**: All tests still pass + performance improves >= 5%

**Auto-Transition**: Switch from Stage 1 → Stage 2 when tests_passed == tests_total

---

### Investigation

**Task**: Analyze failures (Stage 1: Correctness) or bottlenecks (Stage 2: Performance)

#### Stage 1: Correctness Investigation

**Process:**
1. Run test suite via `evaluation.test_cmd` from config
2. Review failed_tests
3. Sample N failures (investigation.samples)
4. For each failure:
   - Input, expected, actual/error
   - Trace execution to find bug
   - Identify type (edge case, logic error, off-by-one, etc.)
5. Propose code fixes

**Common Bug Patterns:**
- Empty input handling
- Boundary errors (off-by-one, index out of bounds)
- Sign handling (negative numbers, abs() issues)
- Type errors (string/int confusion)
- Logic errors (wrong operators, reversed conditions)

**Investigation Report (Correctness):**
```markdown
## Investigation Report - Round N (Stage 1: Correctness)

**Tests Analyzed**: 10 failing tests
**Investigation Rounds**: 3

### Current Status
- Tests passed: 85/100 (85%)
- Execution time: 1234ms

### Failure Analysis

**Failing Test 1: test_empty_list**
- Input: []
- Expected: 0
- Got: IndexError: list index out of range
- Root cause: Line 42 accesses nums[0] without checking empty
- Fix: Add `if not nums: return 0` at start

**Failing Test 2: test_negative_numbers**
- Input: [-5, -3, -1]
- Expected: -9
- Got: 9
- Root cause: Line 55 incorrectly uses abs() on all numbers
- Fix: Remove abs(), handle negatives directly

**Pattern Summary:**
- Pattern 1: Empty input (3 tests) - Missing null/empty checks
- Pattern 2: Negative numbers (4 tests) - Incorrect abs() usage
- Pattern 3: Off-by-one (3 tests) - Index boundary issues

### Proposed Changes

**File**: src/solution.py

```python
def twoSum(nums, target):
-   result = []
+   # Fix 1: Handle empty
+   if not nums:
+       return []
+
+   result = []
    # Fix 3: Correct loop range
    for i in range(len(nums)-1):  # Was: range(len(nums))
-       val = abs(nums[i])  # Fix 2: Don't use abs
+       val = nums[i]
        if val + nums[i+1] == target:
            result.append([i, i+1])
    return result
```

### Expected Impact
- Tests passed: 85/100 → 92/100 (+7)
- All Patterns 1, 2, 3 fixed
```

#### Stage 2: Performance Investigation

**Process (when all tests pass):**
1. Profile algorithm execution
2. Sample N slowest tests
3. Analyze time/space complexity
4. Identify bottlenecks:
   - Inefficient data structures (list → set/dict)
   - Nested loops (O(n²) → O(n log n))
   - Redundant computations
   - Excessive memory allocations

**Common Optimization Patterns:**
- Data structure swap: list → set (O(n) → O(1) lookups)
- Hash map: Replace nested loop with lookup
- Algorithm change: Brute force → DP/greedy
- In-place operations: Eliminate copies
- Early termination: Add break conditions

**Investigation Report (Performance):**
```markdown
## Investigation Report - Round N (Stage 2: Performance)

**Tests Analyzed**: 10 slowest tests
**Investigation Rounds**: 3

### Current Status
- Tests passed: 100/100 (100%)
- Execution time: 5234ms
- Memory: 120.5MB

### Bottleneck Analysis

**Bottleneck 1: Nested loop in findPairs()**
- Time: 3200ms (61% of total)
- Current complexity: O(n²)
- Issue: Checking all pairs with nested loop
- Optimization: Use hash map for O(1) lookups
- New complexity: O(n)
- Expected speedup: ~60-70% reduction

**Bottleneck 2: Repeated list copies in process()**
- Time: 1500ms (29% of total)
- Current complexity: O(n) per copy, 10 copies = O(10n)
- Issue: Creating full list copy each iteration
- Optimization: In-place modifications
- New complexity: O(1) per iteration
- Expected speedup: ~25-30% reduction

### Proposed Changes

**File**: src/solution.py

```python
# Current - O(n²)
def findPairs(nums, target):
    pairs = []
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] + nums[j] == target:
                pairs.append([i, j])
    return pairs

# Proposed - O(n)
def findPairs(nums, target):
    seen = {}
    pairs = []
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            pairs.append([seen[complement], i])
        seen[num] = i
    return pairs
```

### Expected Impact
- Tests passed: 100/100 (maintain)
- Execution time: 5234ms → ~1500ms (-71%)
- Memory: 120.5MB → ~125MB (+4MB, acceptable)
```

**Constraints:**
- ✅ All tests visible
- ❌ No test modification/removal
- ❌ No output hardcoding

---

### Implementation

**Task**: Modify code and commit

**Process:**
1. Read investigation report
2. Apply changes to source files
3. Verify no test modifications
4. Run tests via `evaluation.test_cmd` from config
5. Confirm improvement
6. Commit and push

**Allowed:**
- ✅ Bug fixes (edge cases, logic errors)
- ✅ Performance optimizations (data structures, algorithms)
- ✅ Code refactoring (readability)

**Forbidden:**
- ❌ Hardcoding test outputs
- ❌ Removing/modifying tests
- ❌ Changing test expectations

**Commit Format:**
```
Round N{, Retry M}: {Brief summary}

- Fixed {bug}: {description}
- Optimized {function}: {what improved}

Based on investigation: {brief findings}
```

---

### Evaluation

**Task**: Run tests and decide with evidence

**Process:**
1. Run `evaluation.test_cmd` from config and capture results (tests passed/failed, execution time)
2. Compare against baseline or previous round metrics from `<run_id>/baseline_metrics.json`
3. Calculate deltas
3. Apply phase-specific decision logic
4. Generate delta and PR body

**Decision Logic:**

#### Stage 1: Correctness

**ACCEPT if:**
- new_tests_passed >= previous_tests_passed (no regressions)
- AND new_tests_passed > previous_tests_passed (progress)

**REJECT if:**
- new_tests_passed < previous_tests_passed (regression)
- OR new_tests_passed == previous_tests_passed (no progress)

#### Stage 2: Performance

**ACCEPT if:**
- new_tests_passed == tests_total (still 100% correct)
- AND (execution_time < previous * 0.95 OR memory < previous * 0.95)

**REJECT if:**
- new_tests_passed < tests_total (broke correctness)
- OR no performance improvement >= 5%

**CRITICAL: Evidence Required**

**1. Metrics table:**
| Metric | Baseline | Proposed | Delta | Threshold | Status |
|--------|----------|----------|-------|-----------|--------|
| Tests Passed | 85/100 | 92/100 | +7 | >0 | ✅ |
| Execution Time | 1234ms | 1250ms | +16ms | - | - |

**2. Test-level evidence (if rejection):**
- Which tests regressed
- Pattern description

**3. Root cause:**
- Why regression occurred
- Which code change caused it

**4. Retry recommendation:**
- What NOT to try
- Suggested fix approach

**Output Files:**

**delta_round_N.json:**
```json
{
  "round": 2,
  "phase": "correctness",
  "baseline": {
    "tests_passed": 85, "tests_failed": 15, "pass_rate": 0.85,
    "execution_time_ms": 1234, "memory_mb": 45.2
  },
  "proposed": {
    "tests_passed": 92, "tests_failed": 8, "pass_rate": 0.92,
    "execution_time_ms": 1250, "memory_mb": 46.0
  },
  "deltas": {
    "tests_passed": 7, "pass_rate": 0.07,
    "execution_time_ms": 16, "memory_mb": 0.8
  },
  "verdict": "ACCEPT",
  "rationale": "7 more tests passing, no regressions. Slight perf regression acceptable in correctness phase."
}
```

**pr_body.md (Correctness):**
```markdown
## Round N: Correctness Debugging

### Changes
- Fixed empty list handling (line 42)
- Fixed negative number handling (removed abs())
- Fixed off-by-one loop range

### Test Results

| Metric | Baseline | Proposed | Delta |
|--------|----------|----------|-------|
| Tests Passed | 85/100 | 92/100 | +7 |
| Pass Rate | 85% | 92% | +7% |

### Phase: Correctness

### Verdict: ✅ ACCEPT

7 more tests passing, no regressions.
Continue debugging remaining 8 failures in next round.
```

**pr_body.md (Performance):**
```markdown
## Round N: Performance Optimization

### Changes
- Optimized findPairs() from O(n²) to O(n) with hash map
- Eliminated list copies in process()

### Test Results

| Metric | Baseline | Proposed | Delta |
|--------|----------|----------|-------|
| Tests Passed | 100/100 | 100/100 | 0 |
| Execution Time | 5234ms | 1456ms | -3778ms (-72%) |
| Memory | 120.5MB | 124.8MB | +4.3MB |

### Phase: Performance

### Verdict: ✅ ACCEPT

All tests still pass. Execution time improved 72%.
Minor memory increase (+4MB) acceptable for massive speedup.
```

---

## Success Criteria

A round succeeds when:

**Stage 1 (Correctness):**
- More tests pass than before
- No test regressions
- Root causes identified and fixed

**Stage 2 (Performance):**
- All tests still pass (100%)
- Speed or memory improves >= 5%
- Optimizations are algorithmic (not hardcoded)

---

## Notes

- **No previous run checks**: Do NOT check git branches, git log, or remote state for previous runs at startup. Each invocation starts fresh from the config — read the yaml, set up the project, and begin Round 1.
- **No train/eval split**: All tests visible
- **Phase transition**: Automatic at 100% pass rate
- **Deterministic**: Use committed results
- **Performance threshold**: 5% filters noise
- **Correctness first**: Never sacrifice correctness for performance
- **Targeted edits only**: When modifying config files (pyproject.toml, etc.), use Edit to change specific lines instead of Write to rewrite the whole file. Rewriting risks dropping sections (e.g., `[build-system]`) that weren't related to the fix.
- **Respect `max_per_test_time_out`**: If `evaluation.max_per_test_time_out` is set in the config, use it as the per-test timeout (e.g., `pytest --timeout=<value>` with pytest-timeout). This prevents hanging on naive implementations that can't handle large inputs.
- **Write efficient test cases**: Tests should import and call functions directly instead of spawning subprocesses. Subprocess-per-test adds significant overhead (process startup, Python interpreter boot) and makes timeout control harder. Use `subprocess` only for CLI integration tests — correctness and performance tests should call the function in-process. Keep per-test subprocess timeouts aligned with `max_time_out` from config to fail fast on naive implementations.
