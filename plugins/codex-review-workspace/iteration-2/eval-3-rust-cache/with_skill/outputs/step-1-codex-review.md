# Step 1: Codex Review

**Thread ID:** 019ccec8-5b26-77b1-9751-4c3b347587e0

## Codex Findings

1. **Severity: critical**
   **Location:** cache.rs:42-49
   **Issue:** `set()` evicts when `map.len() >= max_size` *before* checking whether `key` already exists. Updating an existing key at capacity can evict an unrelated entry unnecessarily. Also, `max_size == 0` still allows insertion, violating size constraints.
   **Fix:**
   - If `key` already exists, replace in place without eviction.
   - If `max_size == 0`, either reject inserts or return early.
   - Only evict when inserting a new key and capacity is full.

2. **Severity: warning**
   **Location:** cache.rs:130-131
   **Issue:** Manual `unsafe impl Send/Sync` is unnecessary and risky. `Cache` is already auto-`Send`/`Sync` from its fields; forcing this with `unsafe` can become unsound if fields change later.
   **Fix:** Remove both `unsafe impl` blocks and rely on auto traits.

3. **Severity: warning**
   **Location:** cache.rs:99-113
   **Issue:** `get_or_insert()` is not atomic (check-then-act race). Concurrent callers can compute the same value multiple times and overwrite each other.
   **Fix:** Perform existence check + insert decision under one lock, or use an entry-style API/singleflight mechanism so only one computation occurs per key.

4. **Severity: warning**
   **Location:** cache.rs:24-35, 54-68
   **Issue:** `access_count` is never incremented, so eviction by "lowest count" is effectively meaningless and iteration-order dependent.
   **Fix:** In `get()`, lock mutably and increment `entry.access_count` on hit (non-expired), or remove `access_count` and implement a clear policy (LRU/LFU/FIFO).

5. **Severity: warning**
   **Location:** cache.rs:86-96
   **Issue:** `start_cleanup_thread()` can be called multiple times, spawning unbounded detached threads with no stop/join mechanism.
   **Fix:** Store a `JoinHandle`/shutdown flag (or use a single background worker) and prevent duplicate cleanup threads.

6. **Severity: warning**
   **Location:** cache.rs:27, 79, 93
   **Issue:** Expiration boundary is inconsistent: `get()` treats `expires_at == now` as valid (`< now`), but cleanup thread removes entries when `expires_at <= now` (`retain > now`).
   **Fix:** Pick one policy and apply consistently (`<= now` expired is common).

7. **Severity: suggestion**
   **Location:** cache.rs:25, 40, 75, 91, 123
   **Issue:** Repeated `lock().unwrap()` means a poisoned mutex will panic all cache operations.
   **Fix:** Handle poisoning explicitly (`lock().unwrap_or_else(|e| e.into_inner())`) or return `Result` from public APIs.

8. **Severity: suggestion**
   **Location:** cache.rs:25-35
   **Issue:** `get()` does not remove expired entries on read, so stale entries accumulate until periodic cleanup/manual cleanup runs.
   **Fix:** Use mutable access in `get()` and remove expired entries eagerly on hit-check. This improves memory behavior and keeps `stats()` meaningful.
