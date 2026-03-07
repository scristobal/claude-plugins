# Consensus Code Review: auth.js

**THREAD_ID:** `019cc885-9185-7ab2-8872-5bb4f8702cbc`
**ROUNDS:** 2 (initial + 1 deliberation)
**VERDICT:** Request Changes -- this code must not be merged in its current state. It contains multiple critical security vulnerabilities that would expose the application to trivial exploitation.

---

## Agreed Findings

### Critical

1. **SQL Injection** -- `auth.js:16`, `auth.js:29`
   Both the `/register` and `/login` queries use string interpolation (`${username}`, `${password}`, `${email}`) to build SQL. This allows trivial SQL injection, including authentication bypass via payloads like `' OR 1=1 --`.
   **Fix:** Use parameterized queries with `?` placeholders and pass values as an array to `db.query()`.

2. **Plaintext Password Storage** -- `auth.js:16`, `auth.js:29`
   Passwords are inserted and compared as plaintext. A database breach would expose every user's password. The login query compares raw password text, which also prevents constant-time comparison.
   **Fix:** Hash passwords on registration using `bcrypt` or `argon2`. On login, fetch the user by username only, then verify the password with a constant-time hash comparison.

3. **Sensitive Data Leakage via SELECT * and Response** -- `auth.js:29`, `auth.js:36-37`
   `SELECT *` returns the entire user row including the password column. This full record is stored in the session (`req.session.user = results[0]`) and returned to the client in the JSON response (`user: results[0]`), exposing the password.
   **Fix:** Select only necessary columns (e.g., `id`, `username`, `email`). Store only a minimal identifier in the session. Never return password data to the client.

### Warning

4. **Hardcoded Database Credentials** -- `auth.js:5-9`
   The database connection uses hardcoded credentials (`root` / `admin123`). Secrets in source code will be committed to version control. Using the `root` MySQL account also violates the principle of least privilege.
   **Fix:** Load credentials from environment variables or a secret manager. Use a dedicated database user with only the permissions this application requires.

5. **No Input Validation** -- `auth.js:13`, `auth.js:27`
   There is no validation of `username`, `password`, or `email` before use. Empty, missing, or malformed values will be inserted as bad data or cause opaque database errors.
   **Fix:** Validate required fields, enforce length and format constraints, and return `400 Bad Request` for invalid input.

6. **Single Database Connection, No Pool** -- `auth.js:5`
   `mysql.createConnection()` creates a single connection with no reconnection logic. A dropped connection breaks authentication until process restart, and a single connection is a throughput bottleneck under concurrent requests.
   **Fix:** Use `mysql.createPool()` (or switch to `mysql2`) with proper error handling.

7. **Internal Error Messages Exposed to Client** -- `auth.js:19`, `auth.js:32`
   `err.message` from MySQL is returned directly in the JSON response. This can leak internal details such as table names, column names, and query structure to an attacker.
   **Fix:** Log the real error server-side and return a generic error message (e.g., `"Internal server error"`) to the client.

8. **No Rate Limiting on Login** -- `auth.js:26-41`
   The `/login` endpoint has no protection against brute-force attacks. An attacker can make unlimited login attempts to guess credentials.
   **Fix:** Implement rate limiting (e.g., `express-rate-limit`), per-IP or per-user throttling, and consider account lockout or step-up verification after repeated failures.

### Suggestion

9. **Session Middleware Dependency Not Verified** -- `auth.js:36`
   The code uses `req.session.user` but this file does not configure `express-session`. If session middleware is not mounted before this router in the main app, `req.session` will be `undefined` and the login handler will throw at runtime.
   **Fix:** Confirm that `express-session` is properly configured in the main application. Consider adding a guard or documenting the middleware dependency.

---

## Resolved Disagreements

- **Rate limiting severity:** Initially suggested as `suggestion`; after deliberation, both reviewers agreed `warning` is appropriate for a public-facing authentication endpoint.
- **Session middleware severity:** Codex noted this is conditional on the broader application configuration. Both reviewers agreed to keep it as `suggestion` since session middleware could be configured elsewhere, but flagged it as important to verify.

## Unresolved Disagreements

None. Full consensus was reached.
