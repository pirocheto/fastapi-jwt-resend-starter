"""
Message constants used across the application, following the naming convention:
- SUCCESS_[ENTITY]_[ACTION]
- ERROR_[ENTITY]_[CAUSE]
"""

SUCCESS_USER_REGISTERED = "User registered successfully."
SUCCESS_USER_LOGGED_IN = "Login successful."
SUCCESS_USER_LOGGED_OUT = "Logout successful."
SUCCESS_PASSWORD_UPDATED = "Password updated successfully."
SUCCESS_PASSWORD_RESET_LINK_SENT = "Password reset link sent successfully."
SUCCESS_EMAIL_VERIFICATION_LINK_SENT = "Email verification link sent successfully."
SUCCESS_PASSWORD_RESET = "Password has been reset successfully."
SUCCESS_USER_VERIFIED = "User verified successfully."
SUCCESS_PROFILE_UPDATED = "Profile updated successfully."
SUCCESS_USER_DELETED = "User account deleted successfully."

"""
Error Messages
These constants represent various error messages that can be returned by the application.
"""
ERROR_INVALID_CREDENTIALS = "Invalid credentials provided."
ERROR_USER_NOT_FOUND = "User not found."
ERROR_USER_INACTIVE = "Inactive user."
ERROR_EMAIL_NOT_VERIFIED = "Email not verified."
ERROR_USER_ALREADY_EXISTS = "User with this email already exists."
ERROR_PASSWORD_RESET_TOKEN_INVALID = "Invalid or expired password reset token."
ERROR_PASSWORD_RESET_TOKEN_MISSING = "Password reset token is missing."
ERROR_VERIFICATION_TOKEN_INVALID = "Invalid or expired verification token."
ERROR_VERIFICATION_TOKEN_MISSING = "Verification token is missing."
ERROR_EMAIL_ALREADY_VERIFIED = "Email is already verified."
ERROR_UNAUTHORIZED = "Unauthorized access."
ERROR_FORBIDDEN = "Forbidden."
ERROR_NOT_ACCEPTABLE = "Request not acceptable."
ERROR_CONFLICT = "Conflict occurred."
ERROR_BAD_REQUEST = "Bad request."
ERROR_INTERNAL_SERVER = "An internal server error occurred. Please try again later."
