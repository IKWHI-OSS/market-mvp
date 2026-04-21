from app.core.security import hash_password, verify_password, create_access_token, decode_token


def test_password_hash_and_verify():
    hashed = hash_password("mysecret")
    assert hashed != "mysecret"
    assert verify_password("mysecret", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_create_and_decode_token():
    payload = {"user_id": "user_001", "role": "consumer"}
    token = create_access_token(payload)
    decoded = decode_token(token)
    assert decoded["user_id"] == "user_001"
    assert decoded["role"] == "consumer"


def test_expired_token_raises():
    from datetime import timedelta
    from jose import JWTError
    import pytest
    token = create_access_token({"user_id": "x"}, expires_delta=timedelta(seconds=-1))
    with pytest.raises(JWTError):
        decode_token(token)
