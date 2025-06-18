from src.app.interfaces.schemas.auth_schema import TokenPayload

def test_token_payload():
    obj = TokenPayload(token="abc123")
    assert obj.token == "abc123"
