from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from typing import Optional
from app.config.jwt import jwt_settings
import uuid
from fastapi.security import OAuth2PasswordBearer

# 秘钥
SECRET_KEY=jwt_settings.JWT_SECRET_KEY
# JWT算法
ALGORITHM = jwt_settings.JWT_ALGORITHM
# 过期时间配置
ACCESS_TOKEN_EXPIRE_MINUTES =jwt_settings.JWT_EXPIRATION
# 定义 token 的 URL 路径
TOKEN_URL = "/auth/token"  

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    # 添加标准安全声明
    to_encode.update({
        "exp": expire,                 # 过期时间
        "iat": now,                    # 签发时间
        "jti": str(uuid.uuid4())       # 唯一标识符
    })
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise ValueError(f"Token验证失败: {e}")
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)
