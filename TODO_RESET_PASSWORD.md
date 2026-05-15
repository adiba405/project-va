# Password reset (forgot password via email)

## Implemented
- [x] SMTP email sender helper (`backend/utils/email_utils.py`)
- [x] Password reset controller (`backend/controllers/password_reset_controller.py`)
- [x] Password reset routes (`backend/routes/password_reset_routes.py`)
- [x] Registered password reset routes in Flask app (`backend/app.py`)
- [x] Frontend forgot-password page (`frontend/forgot-password.html`)
- [x] Reset page already existed (`frontend/reset-password.html`)
- [x] Updated login page link to forgot-password (`frontend/login.html`)

## How it works
1. POST `/api/auth/forgot-password` with `{ email }`
   - If user exists, creates an expiring token in `password_resets` collection and emails a link.
   - Always returns a generic success message.
2. User opens `/reset-password.html?token=...`
   - Page sends POST `/api/auth/reset-password` with `{ token, new_password }`
   - Backend verifies token and updates the user password.

## Required env vars
- SMTP_HOST
- SMTP_PORT
- SMTP_USERNAME
- SMTP_PASSWORD
- SMTP_FROM

Optional:
- SMTP_USE_TLS=true
- SMTP_SUBJECT_PREFIX
- APP_BASE_URL (used to build reset link; defaults to http://localhost:5000)
- PASSWORD_RESET_EXPIRY_MINUTES (default 45)

