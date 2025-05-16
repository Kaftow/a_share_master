from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config.database import database_settings
from typing import Generator, AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi import HTTPException
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
DB_URL = database_settings.db_url
ASYNC_DB_URL = database_settings.async_db_url
engine = create_engine(DB_URL, echo=False)
async_engine = create_async_engine(ASYNC_DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
AsyncSessionLocal=async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"同步数据库连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail="数据库连接失败，请稍后再试")
    except Exception as e:
        logger.error(f"同步数据库出现未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="未知数据库错误")
    finally:
        db.close()
    
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            logger.error(f"异步数据库连接失败: {str(e)}")
            raise HTTPException(status_code=500, detail="数据库连接失败，请稍后再试")
        except Exception as e:
            logger.error(f"异步数据库出现未知错误: {str(e)}")
            raise HTTPException(status_code=500, detail="未知数据库错误")
        finally:
            await session.close()

if __name__ == "__main__":
    import asyncio
    # 测试数据库连接
    def test_connection():
        try:
            with engine.connect() as connection:
                logger.info("同步数据库连接成功")
        except Exception as e:
            logger.info(f"同步数据库连接失败: {e}")

    async def test_async_connection():
        try:
            async with async_engine.connect() as conn:
                await conn.run_sync(lambda conn: logger.info("异步数据库连接成功"))
                logger.info("异步数据库连接成功")
        except Exception as e:
            logger.info(f"异步数据库连接失败: {e}")
        finally:
            await async_engine.dispose()

    def drop_all_tables():
        try:
            Base.metadata.drop_all(bind=engine)
            logger.info("所有表格已删除")
        except Exception as e:
            logger.info(f"删除表格时出错: {e}")
    
    test_connection()
    asyncio.run(test_async_connection())
    drop_all_tables()
