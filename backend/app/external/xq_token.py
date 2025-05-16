import requests
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger

class XueqiuTokenProvider:
    def __init__(self, user_agent: Optional[str] = None, ttl_minutes: int = 30):
        self.user_agent = user_agent or "Mozilla"
        self.ttl = timedelta(minutes=ttl_minutes)  # token 有效期
        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

    def get_token(self) -> Optional[str]:
        # 如果 token 有效，直接返回
        if self._token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._token
        # 否则请求新的 token
        try:
            response = requests.get("https://xueqiu.com/hq", headers={"User-Agent": self.user_agent})
            token = response.cookies.get("xq_a_token")
            if not token:
                logger.error("未能从 cookies 获取 xq_a_token")
                raise ValueError("未能从 cookies 获取 xq_a_token")

            self._token = token
            self._token_expiry = datetime.now() + self.ttl
            return token
        except Exception as e:
            logger.error(f"获取雪球 token 失败: {e}")
            return None
