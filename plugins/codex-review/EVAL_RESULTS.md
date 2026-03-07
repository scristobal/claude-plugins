# codex-review eval results

The codex-review plugin uses a deliberative approach: Claude and Codex independently review code, then debate their findings over multiple rounds until they reach consensus. To evaluate this, we ran 3 test cases covering different languages (JavaScript, Python, Rust) and bug categories (security, concurrency, performance). Each test fixture contains intentional bugs that a thorough review should catch.

Source files:
- [`test-fixtures/eval-1/auth.js`](test-fixtures/eval-1/auth.js) — Express authentication with SQL injection, plaintext passwords, hardcoded credentials, and user data leaks
- [`test-fixtures/eval-2/queue.py`](test-fixtures/eval-2/queue.py) — Job queue with a `threading.Lock` that is created but never acquired
- [`test-fixtures/eval-3/cache.rs`](test-fixtures/eval-3/cache.rs) — Thread-safe cache with TOCTOU races, unnecessary `unsafe`, broken eviction, and cleanup thread issues

All runs completed in 2 rounds of deliberation.

## Eval 1 — Express auth (auth.js)

| Assertion | Result |
|-----------|--------|
| Identifies SQL injection from string-interpolated queries | pass |
| Identifies plaintext password storage without hashing | pass |
| Flags hardcoded database password 'admin123' | pass |
| Notes login response returns full user object including password | pass |
| Structured report with severity-based sections | pass |

## Eval 2 — Job queue race condition (queue.py)

| Assertion | Result |
|-----------|--------|
| Identifies claim_next_job does not hold the lock during check-then-act | pass |
| Notes add_job is not thread-safe (list append and id assignment unprotected) | pass |
| Notes complete_job and fail_job also lack locking | pass |
| Structured report with severity-based sections | pass |

## Eval 3 — Thread-safe cache (cache.rs)

| Assertion | Result |
|-----------|--------|
| Identifies TOCTOU race in get_or_insert between get and set calls | pass |
| Flags unnecessary unsafe impl Send/Sync on Arc<Mutex<_>> | pass |
| Notes access_count is never incremented, making eviction broken | pass |
| Identifies cleanup thread lifecycle problems | pass |
| Structured report with severity-based sections | pass |

## Summary

14/14 assertions passed across 3 evals. Beyond the assertions, the deliberation consistently surfaced additional findings that neither model alone would have prioritized as strongly. For example, in eval 1 both models debated whether MySQL root access was Critical or Warning severity and converged on Warning with an explicit escalation note. In eval 3, the models agreed to elevate the `unsafe impl` to Critical despite the current code being technically sound, because it disables compiler safety checks for future changes.

The deliberative approach adds latency (~3 minutes per review) compared to a single-model pass, but the back-and-forth produces reviews with fewer false positives and more nuanced severity assessments. The "Resolved Disagreements" section in each review makes the reasoning transparent, which helps the author decide whether to act on a finding or push back.
