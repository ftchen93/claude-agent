# ACC-202 Reset password via email

As a registered user, I want to reset my password via an emailed link so that I can regain access when I forget it.

## Acceptance criteria
- AC-1: Given I am on the login page, when I click "Forgot password" and enter my registered email, then I receive an email with a reset link.
- AC-2: When I open the link and enter a new password twice, then my password is updated and I am redirected to login with the message "Password updated".

## Dependencies
Email service (SendGrid) is configured in staging.
