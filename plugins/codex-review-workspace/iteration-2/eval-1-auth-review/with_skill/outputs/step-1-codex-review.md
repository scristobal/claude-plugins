# Step 1: Codex Review

**Thread ID:** 019ccec7-d09f-7052-9e08-27320f9ed043

## Codex Findings

1. **Severity: critical**
   **File:** auth.js:15, 28
   **Issue:** SQL queries are built with string interpolation from user input. This is vulnerable to SQL injection in both `/register` and `/login`.
   **Fix:** Use parameterized queries/placeholders. Example:
   `db.query('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', [username, hashedPassword, email], ...)` and
   `db.query('SELECT id, username, email, password_hash FROM users WHERE username = ?', [username], ...)`.

2. **Severity: critical**
   **File:** auth.js:15, 28
   **Issue:** Passwords are stored and compared in plaintext. This is a major security vulnerability.
   **Fix:** Hash passwords with a strong password KDF (`bcrypt`/`argon2`) on register, and verify with `bcrypt.compare` on login. Never store raw passwords.

3. **Severity: critical**
   **File:** auth.js:35
   **Issue:** Entire DB user record is stored in session and returned to client (`user: results[0]`), likely including password. This leaks sensitive data and increases session risk.
   **Fix:** Store only minimal identity in session (e.g., `userId`, role). Return a sanitized user DTO (e.g., `{id, username, email}`), never password/hash.

4. **Severity: warning**
   **File:** auth.js:6-10
   **Issue:** Database credentials are hardcoded (`root` / `admin123`). This is insecure and inflexible across environments.
   **Fix:** Load secrets from environment variables or a secret manager, use least-privilege DB user, and rotate credentials.

5. **Severity: warning**
   **File:** auth.js:13, 26
   **Issue:** No input validation for `username`, `password`, `email`. Invalid/missing inputs can cause incorrect behavior and security issues.
   **Fix:** Validate and normalize inputs (presence, type, length, email format) before DB operations; return `400` on invalid input.

6. **Severity: warning**
   **File:** auth.js:35
   **Issue:** `req.session` is used without any guard. If session middleware is missing/misconfigured, this throws at runtime.
   **Fix:** Ensure session middleware is configured before this router; optionally guard with a clear server error if `req.session` is unavailable.

7. **Severity: warning**
   **File:** auth.js:5
   **Issue:** Uses a single `mysql.createConnection` without pooling. Under load, this can become a bottleneck and less resilient to dropped connections.
   **Fix:** Use `createPool` (or `mysql2/promise` pool) with proper error handling.

8. **Severity: suggestion**
   **File:** auth.js:16-19, 29-33
   **Issue:** Raw DB error messages are returned to clients (`err.message`), which can leak internal details.
   **Fix:** Log detailed errors server-side, return generic client-safe messages (`"Internal server error"`).

9. **Severity: suggestion**
   **File:** auth.js:28
   **Issue:** `SELECT *` fetches unnecessary columns and couples API behavior to schema changes.
   **Fix:** Select only required columns explicitly (and never password/hash for response objects).
