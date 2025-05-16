from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum, TIMESTAMP
from app.core.database import Base
from sqlalchemy.sql import func
import enum

class UserStatusEnum(enum.Enum):
    enabled = 'enabled'
    disabled = 'disabled'
    banned = 'banned'

class UserRoleEnum(enum.Enum):
    user = 'user'
    admin = 'admin'
    moderator = 'moderator'

class UserOrm(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='用户 ID')
    username = Column(String(100), nullable=False, index=True, comment='用户名')
    email = Column(String(200), nullable=False, index=True, comment='邮箱')
    hashed_password = Column(String(255), nullable=False, comment='加密后的密码')
    nickname = Column(String(100), nullable=False, comment='昵称')
    avatar_id = Column(Integer, nullable=True, comment='头像ID')
    gender = Column(String(10), nullable=True, comment='性别')
    birth_date = Column(DateTime, nullable=True, comment='出生日期')
    country = Column(String(100), nullable=True, comment='国家')
    status = Column(Enum(UserStatusEnum), default=UserStatusEnum.enabled, comment='账户状态')
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.user, comment='用户角色')
    reset_token = Column(String(255), nullable=True, comment='密码重置 Token')
    last_login = Column(DateTime, nullable=True, comment='最后登录时间')
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), comment='创建时间')
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True, comment='删除时间')

    def __repr__(self):
        return f"<UserOrm(username={self.username}, role={self.role})>"
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None
    
if __name__ == "__main__":
    from app.core.database import engine
    from loguru import logger
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    logger.info("用户表创建成功")

