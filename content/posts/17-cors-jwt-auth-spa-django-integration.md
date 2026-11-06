---
title: CORS and JWT Auth for SPA and Django Integration
category: Authentication
status: published
---
## Two origins, one API
A React SPA served from one origin and a Django API served from another are different sites to the browser. Every request that carries credentials or custom headers must pass a CORS check. Without the correct headers the browser blocks the response even when Django itself returns 200.

Django needs the django-cors-headers package. The allowed origins list must contain the exact SPA origin, including the port used in development. Wildcard origins are acceptable only for public, unauthenticated endpoints. Once cookies or Authorization headers are involved, the origin must be explicit and credentials must be allowed.

## JWT placement and cookies
Access tokens are short-lived and can travel in the Authorization header. Refresh tokens should not. Place the refresh token in an httpOnly, Secure, SameSite cookie. The SPA never reads it; the browser sends it automatically on requests to the API origin.

Because the cookie is cross-origin, SameSite must be None (or Lax if the top-level navigation rules fit) and Secure must be true in production. The CORS configuration must set `CORS_ALLOW_CREDENTIALS = True` and must not use a wildcard origin. The SPA’s fetch or axios calls must include `credentials: "include"`.

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://app.example.com",
]
CORS_ALLOW_CREDENTIALS = True

# simplejwt / cookie settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}
```

## Preflight and header allow-lists
A request that uses the Authorization header or a non-simple content type triggers a preflight OPTIONS request. Django must answer that preflight with the correct Access-Control-Allow-Origin, Access-Control-Allow-Credentials, and Access-Control-Allow-Headers values. django-cors-headers does this once the settings above are in place.

Keep the allowed headers list minimal: Authorization, Content-Type, and any custom header you actually send. Extra headers increase the attack surface and can cause preflight failures if they are missing from the allow list.

## Token refresh flow
When the access token expires, the SPA calls the refresh endpoint. The browser attaches the httpOnly refresh cookie automatically. Django validates the cookie, issues a new access token (and optionally rotates the refresh cookie), and returns the access token in the JSON body. The SPA stores the new access token in memory and retries the original request.

Logout clears the refresh cookie by setting an expired cookie on the API domain. No localStorage cleanup is required for the refresh token because it was never stored there.

## What good looks like
The SPA can log in, receive an access token, and make authenticated requests without CORS errors. A page reload does not lose the session because the refresh cookie is still present. Logging out on one tab ends the session for subsequent requests. If the browser console shows a CORS error on a credentialed request, or if the refresh token appears in localStorage or in JavaScript-readable storage, the origin list, the cookie flags, or the credentials setting needs another look.