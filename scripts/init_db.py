"""
Database initialization script
"""
import asyncio
from sqlalchemy import text
from sqlalchemy.engine import Engine
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

        # Ensure study_plans has extended columns (for MySQL deployments)
        def ensure_study_plans_columns(conn: Engine):
            try:
                # Only run for MySQL where INFORMATION_SCHEMA is available
                dialect_name = conn.dialect.name
                if dialect_name != "mysql":
                    return

                existing_cols = set(
                    row[0]
                    for row in conn.execute(
                        text(
                            """
                            SELECT COLUMN_NAME
                            FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_SCHEMA = :db AND TABLE_NAME = 'study_plans'
                            """
                        ),
                        {"db": settings.database_name},
                    ).fetchall()
                )

                # Columns to add: subject, difficulty_level, estimated_duration, is_public, is_ai_generated
                alters = []
                if "subject" not in existing_cols:
                    alters.append("ADD COLUMN `subject` VARCHAR(50) NULL COMMENT '科目'")
                if "difficulty_level" not in existing_cols:
                    alters.append("ADD COLUMN `difficulty_level` VARCHAR(20) NULL COMMENT '难度'")
                if "estimated_duration" not in existing_cols:
                    alters.append("ADD COLUMN `estimated_duration` INT NULL COMMENT '预计时长(天)'")
                if "is_public" not in existing_cols:
                    alters.append("ADD COLUMN `is_public` BOOLEAN DEFAULT FALSE COMMENT '是否公开'")
                if "is_ai_generated" not in existing_cols:
                    alters.append("ADD COLUMN `is_ai_generated` BOOLEAN DEFAULT FALSE COMMENT '是否AI生成'")

                if alters:
                    alter_sql = f"ALTER TABLE `study_plans` {', '.join(alters)};"
                    conn.execute(text(alter_sql))
                    conn.commit()
                    print("✅ study_plans 表已更新，新增列: " + ", ".join([
                        s.split('`')[1] for s in alters
                    ]))
                else:
                    print("ℹ️ study_plans 表列已符合最新模型，无需更新")
            except Exception as e:
                print(f"⚠️ 校验/更新 study_plans 表列失败: {e}")

        # Insert initial system configurations
        with engine.connect() as conn:
            # Ensure columns
            ensure_study_plans_columns(conn)

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

