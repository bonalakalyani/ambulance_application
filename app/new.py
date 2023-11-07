import secrets


def generate_otp(length=6):
    """Generates a random OTP of the specified length."""
    return secrets.token_hex(length // 2 + 1)[:length]

otp = generate_otp()
print(f"Generated OTP: {otp}")