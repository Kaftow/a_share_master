from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime, date
from app.models.user_orm import UserStatusEnum, UserRoleEnum

# 用户登录请求模型
class UserLoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

# 用户注册请求模型
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=8, description="密码")
    nickname: Optional[str] = Field(None, description="昵称")
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('密码长度至少为8位')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        if not any(c.isalpha() for c in v):
            raise ValueError('密码必须包含至少一个字母')
        return v

# 用户信息更新请求模型
class UserUpdateRequest(BaseModel):
    nickname: Optional[str] = Field(None, description="昵称")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    avatar_id: Optional[int] = Field(None, description="头像ID")
    gender: Optional[str] = Field(None, description="性别")
    birth_date: Optional[date] = Field(None, description="出生日期")
    country: Optional[str] = Field(None, description="国家")

# 用户密码重置请求模型
class PasswordChangeRequest(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, description="新密码")
    
    @field_validator('new_password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少为8位')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        if not any(c.isalpha() for c in v):
            raise ValueError('密码必须包含至少一个字母')
        return v

# 用户基础模型
class UserBase(BaseModel):
    username: str = Field(..., description="用户名")
    email: Optional[EmailStr] = Field(..., description="邮箱")
    nickname: Optional[str] = Field(..., description="昵称")
    avatar_id: Optional[int] = Field(None, description="头像ID")
    gender: Optional[str] = Field(None, description="性别")
    birth_date: Optional[date] = Field(None, description="出生日期")
    country: Optional[str] = Field(None, description="国家")
    status: UserStatusEnum = Field(None, description="账户状态")
    role: UserRoleEnum = Field(None, description="用户角色")

# 用户创建模型
class UserItem(UserBase):
    hashed_password: str = Field(..., description="加密后的密码")
    
    def to_orm(self):
        from app.models.user_orm import UserOrm
        """
        将 Pydantic 模型转换为 ORM 模型
        """
        return UserOrm(**self.model_dump())

# 用户响应模型
class UserResponseItem(UserBase):
    username: str = Field(..., description="用户名")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True

# 登录成功响应
class UserLoginResponse(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="令牌有效期(秒)")
    user: UserResponseItem = Field(..., description="用户信息")