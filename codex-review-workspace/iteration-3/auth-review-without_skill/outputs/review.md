# Code Review: User Authentication for Express App

## Summary

This review covers a new Express router module that adds user registration and login endpoints backed by a MySQL database. The code has multiple **critical security vulnerabilities** that must be resolved before merging. In its current state, the module is exploitable and unsafe for any environment, including development.

---

## Findings

### Critical

#### 1. SQL Injection in `/register` and `/login`

**Lines affected:** query construction in both route handlers.

User-supplied values (`username`, `password`, `email`) are interpolated directly into SQL strings using template literals:

```javascript
const query = `INSERT INTO users (username, password, email) VALUES ('${username}', '${password}', '${email}')`;
```

```javascript
const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
```

An attacker can trivially bypass authentication or dump/modify/delete the entire database. This is the single most exploited web vulnerability (OWASP A03:2021 -- Injection).

**Fix:** Use parameterized queries (placeholders):

```javascript
const query = 'INSERT INTO users (username, password, email) VALUES (?, ?, ?)';
db.query(query, [username, hashedPassword, email], (err, result) => { ... });
```

---

#### 2. Passwords Stored in Plain Text

Passwords are inserted into the database exactly as received and compared as raw strings during login. If the database is ever compromised, every user's password is immediately exposed.

**Fix:** Hash passwords with a strong adaptive algorithm such as `bcrypt`:

```javascript
const bcrypt = require('bcrypt');
const saltRounds = 12;

// Registration
const hashedPassword = await bcrypt.hash(password, saltRounds);

// Login
const match = await bcrypt.compare(password, user.passwordHash);
```

---

#### 3. Hardcoded Database Credentials

```javascript
const db = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: 'admin123',
  database: 'myapp'
});
```

The root user with a weak, hardcoded password is embedded in source code. If this file is committed (it is), the credentials are permanently in version history.

**Fix:** Load credentials from environment variables or a secrets manager, and never use `root` for application connections:

```javascript
const db = mysql.createConnection({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME
});
```

---

#### 4. Full User Record (Including Password) Returned on Login

```javascript
req.session.user = results[0];
res.json({ message: 'Login successful', user: results[0] });
```

`SELECT *` retrieves every column, including the password. That password is then stored in the session object and sent back to the client in the JSON response.

**Fix:** Select only the columns you need, and never return the password field:

```javascript
const query = 'SELECT id, username, email FROM users WHERE username = ?';
```

---

### Warning

#### 5. No Input Validation or Sanitization

There is no check that `username`, `password`, or `email` are present, non-empty, of acceptable length, or of the correct type. Missing fields will produce cryptic SQL errors or `undefined` values in queries.

**Fix:** Validate inputs before processing. Consider a validation library such as `express-validator` or `joi`:

```javascript
if (!username || !password || !email) {
  return res.status(400).json({ error: 'All fields are required' });
}
```

---

#### 6. No Connection Pooling

`mysql.createConnection()` creates a single connection. If it drops (network blip, server restart, idle timeout), all subsequent queries fail permanently. Under concurrent load, a single connection also serializes all queries.

**Fix:** Use `mysql.createPool()` for automatic reconnection and concurrency:

```javascript
const pool = mysql.createPool({
  connectionLimit: 10,
  host: process.env.DB_HOST,
  ...
});
```

---

#### 7. Internal Error Details Leaked to Client

```javascript
res.status(500).json({ error: err.message });
```

Database error messages can reveal table names, column names, SQL syntax, and server version -- all useful to an attacker.

**Fix:** Log the full error server-side and return a generic message to the client:

```javascript
console.error('DB error:', err);
res.status(500).json({ error: 'Internal server error' });
```

---

#### 8. Session Handling Assumed but Not Configured

`req.session.user` is used, but there is no `express-session` middleware configured or imported in this module. If session middleware is not set up upstream, this will throw a runtime error.

**Fix:** Ensure `express-session` is properly configured in the main app file, or document this as a prerequisite. Consider using signed JWTs as an alternative for stateless authentication.

---

### Suggestion

#### 9. Use `async/await` With Promises Instead of Callbacks

The callback style makes error handling verbose and nested. The `mysql2` package (drop-in replacement for `mysql`) supports promises natively:

```javascript
const mysql = require('mysql2/promise');
const [rows] = await pool.execute('SELECT id, username, email FROM users WHERE username = ?', [username]);
```

---

#### 10. Add Rate Limiting to Auth Endpoints

Login and registration endpoints are prime targets for brute-force and credential-stuffing attacks. Without rate limiting, an attacker can make unlimited attempts.

**Fix:** Apply rate limiting middleware such as `express-rate-limit`:

```javascript
const rateLimit = require('express-rate-limit');
const authLimiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 15 });
router.use(authLimiter);
```

---

#### 11. Use HTTPS and Secure Cookie Settings

If session cookies are transmitted over plain HTTP or without the `Secure` and `HttpOnly` flags, they can be intercepted or accessed by client-side scripts.

---

## Verdict: REJECT

This code must not be merged. It contains four critical security vulnerabilities -- SQL injection, plain-text password storage, hardcoded credentials, and password leakage in API responses. Any one of these on its own would be grounds for rejection. The issues are fundamental and require a substantial rewrite of both route handlers rather than incremental patches.
