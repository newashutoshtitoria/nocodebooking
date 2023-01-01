from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime

def get_tokens_for_user(user, schema_name):
    refresh = RefreshToken.for_user(user)
    refresh.payload['sub']=user.id
    # refresh.payload['iat']=datetime.now()
    refresh.payload['schema_name'] = schema_name
    refresh.access_token.payload['sub']=user.id
    # refresh.access_token.payload['iat']=datetime.now()
    refresh.access_token.payload['schema_name'] = schema_name
    return str(refresh), str(refresh.access_token)