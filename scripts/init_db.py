"""
Database initialization script
"""
import asyncio
from sqlalchemy import text
from app.db.database import engine, create_tables
# Ensure all ORM models are imported so Base.metadata is populated
from app import models as _models_pkg  # noqa: F401
from app.models import models as _models  # noqa: F401
from app.core.config import settings


async def init_database():
    """Initialize database with tables and initial data"""
    try:
        # Create all tables
        create_tables()
        print("✅ Database tables created successfully")
        
        # Insert initial system configurations
        with engine.connect() as conn:
            # Check if configs already exist
            result = conn.execute(text("SELECT COUNT(*) FROM system_configs"))
            count = result.scalar()
            
            if count == 0:
                # Insert default configurations
                configs = [
                    ("max_conversation_length", "100", "单次对话最大消息数量"),
                    ("max_file_size", "10485760", "最大文件上传大小（字节）"),
                    ("rate_limit_per_minute", "60", "每分钟API请求限制"),
                    ("ai_model_default", "gpt-3.5-turbo", "默认AI模型"),
                    ("conversation_timeout", "1800", "会话超时时间（秒）"),
                    ("max_study_plans_per_user", "50", "每用户最大学习计划数"),
                    ("max_error_logs_per_user", "1000", "每用户最大错题数"),
                    ("max_conversations_per_user", "100", "每用户最大会话数"),
                ]
                
                for key, value, description in configs:
                    conn.execute(text("""
                        INSERT INTO system_configs (`key`, `value`, `description`, `is_active`)
                        VALUES (:key, :value, :description, :is_active)
                    """), {
                        "key": key,
                        "value": value,
                        "description": description,
                        "is_active": True
                    })
                
                conn.commit()
                print("✅ Default system configurations inserted")
            else:
                print("ℹ️ System configurations already exist")
        
        print("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(init_database())

