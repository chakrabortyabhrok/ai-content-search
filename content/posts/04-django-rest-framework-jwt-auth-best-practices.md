---
title: Django REST Framework JWT Auth Best Practices
category: Authentication
status: published
---
## Short-lived access, long-lived refresh
An access token should expire in minutes, not hours. Five to fifteen minutes is normal. The refresh token can live for days or weeks. When the access token dies, the client silently exchanges the refresh token for a new one. This keeps the window for a stolen access token small.

Never put the refresh token in localStorage. Store it in an httpOnly, secure, same-site cookie. The access token can live in memory. If the browser is compromised the refresh token is still harder to steal than a token sitting in JavaScript-accessible storage.

## Rotate and revoke
Every time a refresh token is used, issue a new one and invalidate the old one. A stolen refresh token then works only once. Keep a simple blacklist or store the refresh token’s jti in the database so you can revoke it on logout or password change. Blacklisting every access token is unnecessary; their short life already limits damage.

## Claims and validation
Put only what the client needs in the token. User id and a short list of roles are enough. Do not embed email, permissions that change often, or any secret. Validate the token on every request with the library’s default checks plus an explicit audience and issuer check if you have more than one service.

## What good looks like
A user stays logged in across page reloads without ever seeing a raw refresh token in the browser. Logging out on one device does not require waiting for the access token to expire. If a refresh token appears in localStorage or an access token lasts longer than thirty minutes, the setup needs another look.