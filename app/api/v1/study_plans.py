"""
Study plans API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.dependencies import get_current_active_user
from app.core.exceptions import NotFoundError, ValidationError, ExternalServiceError
from app.db.database import get_db
from app.models.models import User, StudyPlan, StudyTask, PlanStatus, TaskStatus, TaskPriority
from app.schemas.request import (
    StudyPlanCreateRequest, StudyPlanUpdateRequest, 
    StudyTaskCreateRequest, StudyTaskUpdateRequest,
    StudyPlanGenerateRequest, PaginationRequest
)
from app.schemas.response import BaseResponse, StudyPlanResponse, PaginatedResponse, AIStudyPlanResponse
from app.services.ai_service import ai_service
from app.db.redis import get_redis
import json
import logging
from datetime import datetime
from pydantic import ValidationError as PydanticValidationError

router = APIRouter()
logger = logging.getLogger(__name__)


def _normalize_ai_study_plan(plan_data: dict) -> dict:
    """Ensure required fields exist and have correct types for AIStudyPlanResponse."""
    # Required top-level fields with sensible defaults
    plan_data.setdefault("plan_title", "学习计划")
    plan_data.setdefault("overview", "本学习计划由系统自动生成，并已规范化以保证结构完整。")
    plan_data.setdefault("learning_objectives", [])
    plan_data.setdefault("weekly_schedule", [])
    plan_data.setdefault("milestones", [])
    plan_data.setdefault("resources", [])
    plan_data.setdefault("tips", [])

    # Type corrections
    if not isinstance(plan_data["learning_objectives"], list):
        plan_data["learning_objectives"] = [str(plan_data["learning_objectives"])]
    if not isinstance(plan_data["weekly_schedule"], list):
        plan_data["weekly_schedule"] = []
    if not isinstance(plan_data["milestones"], list):
        plan_data["milestones"] = []
    if not isinstance(plan_data["resources"], list):
        plan_data["resources"] = []
    if not isinstance(plan_data["tips"], list):
        plan_data["tips"] = []

    # Normalize weekly_schedule items
    normalized_schedule = []
    for item in plan_data["weekly_schedule"]:
        if not isinstance(item, dict):
            continue
        week = item.get("week", 1)
        focus = item.get("focus", "学习")
        tasks = item.get("tasks", [])
        if not isinstance(tasks, list):
            tasks = []
        # Ensure each task has required fields
        norm_tasks = []
        for t in tasks:
            if not isinstance(t, dict):
                continue
            norm_tasks.append({
                "title": t.get("title", "任务"),
                "description": t.get("description", ""),
                "estimated_hours": int(t.get("estimated_hours", 1)),
                "priority": t.get("priority", "medium"),
                "resources": t.get("resources", []) if isinstance(t.get("resources", []), list) else []
            })
        normalized_schedule.append({
            "week": int(week),
            "focus": str(focus),
            "tasks": norm_tasks
        })
    plan_data["weekly_schedule"] = normalized_schedule

    # Normalize milestones
    normalized_milestones = []
    for m in plan_data["milestones"]:
        if not isinstance(m, dict):
            continue
        normalized_milestones.append({
            "week": int(m.get("week", 1)),
            "milestone": m.get("milestone", "阶段目标"),
            "assessment": m.get("assessment", "阶段性自测")
        })
    plan_data["milestones"] = normalized_milestones

    # Normalize resources and tips to strings
    plan_data["resources"] = [str(r) for r in plan_data["resources"]]
    plan_data["tips"] = [str(t) for t in plan_data["tips"]]

    return plan_data


@router.post("/generate", response_model=BaseResponse[AIStudyPlanResponse])
async def generate_ai_study_plan(
    plan_request: StudyPlanGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered personalized study plan"""
    
    try:
        # Generate cache key for this request
        cache_key = f"study_plan:{current_user.id}:{hash(str(plan_request.dict()))}"
        
        # Check Redis cache first
        try:
            redis_client = await get_redis()
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached study plan for user {current_user.id}")
                cached_data = json.loads(cached_result)
                cached_data["generated_at"] = datetime.now().isoformat()
                return BaseResponse(
                    code=0,
                    message="AI study plan generated successfully (from cache)",
                    data=AIStudyPlanResponse(**cached_data)
                )
        except Exception as e:
            logger.warning(f"Redis cache check failed: {e}")
        
        # Generate new study plan using AI
        logger.info(f"Generating new AI study plan for user {current_user.id}")
        ai_response = await ai_service.generate_ai_study_plan(
            subject=plan_request.subject,
            time_frame=plan_request.time_frame,
            learning_goals=plan_request.learning_goals,
            current_level=plan_request.current_level,
            study_hours_per_week=plan_request.study_hours_per_week
        )
        
        # Extract content from AI response
        ai_content = ai_service.extract_content(ai_response)
        tokens_used = ai_service.extract_tokens_used(ai_response)
        
        # Log the actual AI response for debugging
        logger.info(f"AI response content (first 500 chars): {ai_content[:500]}")
        
        # Try to extract JSON from markdown code blocks if present
        import re
        
        # First, try to extract JSON from markdown code blocks
        json_match = re.search(r'```json\s*(.*?)\s*```', ai_content, re.DOTALL)
        if json_match:
            ai_content = json_match.group(1)
        else:
            # Remove markdown code block markers if present
            ai_content = re.sub(r'```json\s*', '', ai_content)
            ai_content = re.sub(r'```\s*$', '', ai_content, flags=re.MULTILINE)
            ai_content = ai_content.strip()
        
        # Try to find JSON object in the text
        json_match = re.search(r'\{.*\}', ai_content, re.DOTALL)
        if json_match:
            ai_content = json_match.group(0)

        # Normalize smart quotes and common unicode artifacts
        ai_content = (
            ai_content
            .replace('\u201c', '"').replace('\u201d', '"')
            .replace('\u2018', '"').replace('\u2019', '"')
            .replace('“', '"').replace('”', '"')
            .replace('‘', '"').replace('’', '"')
        )

        # Remove single-line comments that may appear in JSON-like output
        ai_content = re.sub(r'//.*', '', ai_content)

        # Remove trailing commas before } or ]
        ai_content = re.sub(r',\s*([}\]])', r'\1', ai_content)
        
        # Parse JSON response from AI
        try:
            plan_data = json.loads(ai_content)
        except json.JSONDecodeError as e:
            logger.warning(f"AI response was not valid JSON: {e}")
            logger.warning(f"Full AI response (first 2000 chars): {ai_content[:2000]}")
            # 尝试使用AI进行一次自动修复为合法JSON
            try:
                repaired_text = await ai_service.repair_json_output(ai_content)
                plan_data = json.loads(repaired_text)
                logger.info("AI JSON repair succeeded")
            except Exception as repair_err:
                logger.error(f"AI JSON repair failed: {repair_err}")
                # 不再进行兜底模板生成，直接返回错误，便于定位问题
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        f"AI响应不是有效JSON: {e}. 自动修复失败: {repair_err}."
                        f" 原始内容(截断1000字): {ai_content[:1000]}"
                    )
                )
        
        # Normalize and add metadata
        plan_data = _normalize_ai_study_plan(plan_data)
        plan_data["generated_at"] = datetime.now().isoformat()
        plan_data["tokens_used"] = tokens_used
        
        # Cache the result in Redis (expire in 1 hour)
        try:
            redis_client = await get_redis()
            cache_data = plan_data.copy()
            cache_data.pop("generated_at", None)  # Don't cache timestamp
            await redis_client.setex(cache_key, 3600, json.dumps(cache_data))
            logger.info(f"Cached study plan for user {current_user.id}")
        except Exception as e:
            logger.warning(f"Failed to cache study plan: {e}")
        
        # Save to database as a study plan
        saved_plan_id = None
        try:
            study_plan = StudyPlan(
                user_id=current_user.id,
                title=plan_data["plan_title"],
                description=plan_data["overview"],
                subject=plan_request.subject,
                difficulty_level=plan_request.current_level,
                estimated_duration=plan_request.study_hours_per_week,
                is_public=False,
                is_ai_generated=True,
                status=PlanStatus.ONGOING
            )
            db.add(study_plan)
            db.commit()
            db.refresh(study_plan)
            saved_plan_id = study_plan.id
            
            # Save weekly tasks as StudyTask records
            for week_data in plan_data.get("weekly_schedule", []):
                week_num = week_data.get("week", 1)
                week_focus = week_data.get("focus", "学习")
                
                for task_data in week_data.get("tasks", []):
                    task = StudyTask(
                        study_plan_id=study_plan.id,
                        title=f"第{week_num}周: {task_data.get('title', '学习任务')}",
                        description=f"{week_focus} - {task_data.get('description', '')}",
                        task_type="ai_generated",
                        difficulty_level=task_data.get("priority", "medium"),
                        estimated_duration=task_data.get("estimated_hours", 1),
                        priority=TaskPriority.HIGH if task_data.get("priority") == "high" else 
                                TaskPriority.MEDIUM if task_data.get("priority") == "medium" else 
                                TaskPriority.LOW,
                        status=TaskStatus.PENDING
                    )
                    db.add(task)
            
            db.commit()
            logger.info(f"Saved study plan to database with ID {study_plan.id} and {len([t for w in plan_data.get('weekly_schedule', []) for t in w.get('tasks', [])])} tasks")
        except Exception as e:
            logger.error(f"Failed to save study plan to database: {e}")
            db.rollback()
            # Continue without failing the request, but log the error
        
        # Add saved plan ID to response
        plan_data["saved_plan_id"] = saved_plan_id
        
        # 在返回前执行严格的Schema校验，若失败则返回422并报告原因
        try:
            response_obj = AIStudyPlanResponse(**plan_data)
        except PydanticValidationError as ve:
            logger.error(f"Study plan schema validation failed: {ve}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "学习计划结构校验失败",
                    "details": ve.errors(),
                }
            )

        return BaseResponse(
            code=0,
            message="AI study plan generated successfully",
            data=response_obj
        )
        
    except ExternalServiceError as e:
        logger.error(f"External AI service error in study plan generation: {e}")
        # 不使用兜底模板，直接返回外部服务错误详情
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"外部AI服务错误: {str(e)}"
        )
    except HTTPException as e:
        # 让之前设置好的HTTP错误码与详细信息直接透传，不被500覆盖
        raise e
    except Exception as e:
        logger.error(f"Error generating AI study plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成学习计划失败: {str(e)}"
        )


@router.post("/", response_model=BaseResponse[StudyPlanResponse])
async def create_study_plan(
    plan_data: StudyPlanCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new study plan"""
    
    # Check if user has reached maximum study plans limit
    max_plans = 50  # This should come from system config
    current_plans_count = db.query(StudyPlan).filter(
        StudyPlan.user_id == current_user.id,
        StudyPlan.status != PlanStatus.ARCHIVED
    ).count()
    
    if current_plans_count >= max_plans:
        raise ValidationError(f"Maximum study plans limit ({max_plans}) reached")
    
    # Create study plan
    study_plan = StudyPlan(
        user_id=current_user.id,
        title=plan_data.title,
        description=plan_data.description,
        subject=getattr(plan_data, "subject", None),
        difficulty_level=getattr(plan_data, "difficulty_level", None),
        estimated_duration=getattr(plan_data, "estimated_duration", None),
        is_public=getattr(plan_data, "is_public", False),
        start_date=plan_data.start_date,
        end_date=plan_data.end_date,
        status=PlanStatus.ONGOING
    )
    
    db.add(study_plan)
    db.commit()
    db.refresh(study_plan)
    
    return BaseResponse(
        code=0,
        message="Study plan created successfully",
        data=StudyPlanResponse(
            id=study_plan.id,
            user_id=study_plan.user_id,
            title=study_plan.title,
            description=study_plan.description,
            # include extended fields
            subject=getattr(study_plan, "subject", None),
            difficulty_level=getattr(study_plan, "difficulty_level", None),
            estimated_duration=getattr(study_plan, "estimated_duration", None),
            is_public=getattr(study_plan, "is_public", False),
            is_ai_generated=getattr(study_plan, "is_ai_generated", False),
            status=study_plan.status.value,
            start_date=study_plan.start_date.isoformat() if study_plan.start_date else None,
            end_date=study_plan.end_date.isoformat() if study_plan.end_date else None,
            created_at=study_plan.created_at.isoformat(),
            updated_at=study_plan.updated_at.isoformat()
        )
    )


@router.get("/list", response_model=BaseResponse[List[StudyPlanResponse]])
async def get_study_plans_list(
    status: Optional[str] = None,
    subject: Optional[str] = None,
    pagination: PaginationRequest = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's study plans with filtering"""
    
    query = db.query(StudyPlan).filter(StudyPlan.user_id == current_user.id)
    
    if status:
        try:
            norm = status.strip().upper()
            plan_status = PlanStatus[norm]
            query = query.filter(StudyPlan.status == plan_status)
        except Exception:
            raise ValidationError("Invalid status value")
    
    if subject:
        query = query.filter(StudyPlan.subject.ilike(f"%{subject}%"))
    
    # Apply pagination
    offset = (pagination.page - 1) * pagination.per_page
    study_plans = query.order_by(StudyPlan.created_at.desc()).offset(offset).limit(pagination.per_page).all()
    
    plan_responses = [
        StudyPlanResponse(
            id=plan.id,
            user_id=plan.user_id,
            title=plan.title,
            description=plan.description,
            subject=getattr(plan, "subject", None),
            difficulty_level=getattr(plan, "difficulty_level", None),
            estimated_duration=getattr(plan, "estimated_duration", None),
            is_public=getattr(plan, "is_public", False),
            status=plan.status.value,
            start_date=plan.start_date.isoformat() if plan.start_date else None,
            end_date=plan.end_date.isoformat() if plan.end_date else None,
            created_at=plan.created_at.isoformat(),
            updated_at=plan.updated_at.isoformat()
        )
        for plan in study_plans
    ]
    
    return BaseResponse(
        code=0,
        message="Study plans retrieved successfully",
        data=plan_responses
    )


@router.get("/", response_model=BaseResponse[List[StudyPlanResponse]])
async def get_my_study_plans(
    status: Optional[str] = None,
    pagination: PaginationRequest = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's study plans"""
    
    query = db.query(StudyPlan).filter(StudyPlan.user_id == current_user.id)
    
    if status:
        try:
            norm = status.strip().upper()
            plan_status = PlanStatus[norm]
            query = query.filter(StudyPlan.status == plan_status)
        except Exception:
            raise ValidationError("Invalid status value")
    
    # Apply pagination
    offset = (pagination.page - 1) * pagination.per_page
    study_plans = query.offset(offset).limit(pagination.per_page).all()
    
    plan_responses = [
        StudyPlanResponse(
            id=plan.id,
            user_id=plan.user_id,
            title=plan.title,
            description=plan.description,
            subject=getattr(plan, "subject", None),
            difficulty_level=getattr(plan, "difficulty_level", None),
            estimated_duration=getattr(plan, "estimated_duration", None),
            is_public=getattr(plan, "is_public", False),
            status=plan.status.value,
            start_date=plan.start_date.isoformat() if plan.start_date else None,
            end_date=plan.end_date.isoformat() if plan.end_date else None,
            created_at=plan.created_at.isoformat(),
            updated_at=plan.updated_at.isoformat()
        )
        for plan in study_plans
    ]
    
    return BaseResponse(
        code=0,
        message="Study plans retrieved successfully",
        data=plan_responses
    )


@router.get("/{plan_id}", response_model=BaseResponse[StudyPlanResponse])
async def get_study_plan(
    plan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific study plan"""
    
    study_plan = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()
    
    if not study_plan:
        raise NotFoundError("Study plan not found")
    
    return BaseResponse(
        code=0,
        message="Study plan retrieved successfully",
        data=StudyPlanResponse(
            id=study_plan.id,
            user_id=study_plan.user_id,
            title=study_plan.title,
            description=study_plan.description,
            subject=getattr(study_plan, "subject", None),
            difficulty_level=getattr(study_plan, "difficulty_level", None),
            estimated_duration=getattr(study_plan, "estimated_duration", None),
            is_public=getattr(study_plan, "is_public", False),
            is_ai_generated=getattr(study_plan, "is_ai_generated", False),
            status=study_plan.status.value,
            start_date=study_plan.start_date.isoformat() if study_plan.start_date else None,
            end_date=study_plan.end_date.isoformat() if study_plan.end_date else None,
            created_at=study_plan.created_at.isoformat(),
            updated_at=study_plan.updated_at.isoformat()
        )
    )


@router.put("/{plan_id}", response_model=BaseResponse[StudyPlanResponse])
async def update_study_plan(
    plan_id: int,
    plan_data: StudyPlanUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a study plan"""
    
    study_plan = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()
    
    if not study_plan:
        raise NotFoundError("Study plan not found")
    
    # Update fields
    if plan_data.title is not None:
        study_plan.title = plan_data.title
    
    if plan_data.description is not None:
        study_plan.description = plan_data.description

    # Extended fields
    if getattr(plan_data, "subject", None) is not None:
        study_plan.subject = plan_data.subject
    if getattr(plan_data, "difficulty_level", None) is not None:
        study_plan.difficulty_level = plan_data.difficulty_level
    if getattr(plan_data, "estimated_duration", None) is not None:
        study_plan.estimated_duration = plan_data.estimated_duration
    if getattr(plan_data, "is_public", None) is not None:
        study_plan.is_public = plan_data.is_public
    
    if plan_data.status is not None:
        try:
            study_plan.status = PlanStatus(plan_data.status)
        except ValueError:
            raise ValidationError("Invalid status value")
    
    if plan_data.start_date is not None:
        study_plan.start_date = plan_data.start_date
    
    if plan_data.end_date is not None:
        study_plan.end_date = plan_data.end_date
    
    db.commit()
    db.refresh(study_plan)
    
    return BaseResponse(
        code=0,
        message="Study plan updated successfully",
        data=StudyPlanResponse(
            id=study_plan.id,
            user_id=study_plan.user_id,
            title=study_plan.title,
            description=study_plan.description,
            subject=getattr(study_plan, "subject", None),
            difficulty_level=getattr(study_plan, "difficulty_level", None),
            estimated_duration=getattr(study_plan, "estimated_duration", None),
            is_public=getattr(study_plan, "is_public", False),
            status=study_plan.status.value,
            start_date=study_plan.start_date.isoformat() if study_plan.start_date else None,
            end_date=study_plan.end_date.isoformat() if study_plan.end_date else None,
            created_at=study_plan.created_at.isoformat(),
            updated_at=study_plan.updated_at.isoformat()
        )
    )


@router.delete("/{plan_id}", response_model=BaseResponse[None])
async def delete_study_plan(
    plan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a study plan"""
    
    study_plan = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()
    
    if not study_plan:
        raise NotFoundError("Study plan not found")
    
    # Archive instead of hard delete
    study_plan.status = PlanStatus.ARCHIVED
    db.commit()
    
    return BaseResponse(
        code=0,
        message="Study plan deleted successfully",
        data=None
    )


# Study Tasks endpoints

@router.post("/{plan_id}/tasks", response_model=BaseResponse[dict])
async def create_study_task(
    plan_id: int,
    task_data: StudyTaskCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new study task"""
    
    # Verify plan exists and belongs to user
    study_plan = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()
    
    if not study_plan:
        raise NotFoundError("Study plan not found")
    
    # Create study task
    study_task = StudyTask(
        study_plan_id=plan_id,
        title=task_data.title,
        description=task_data.description,
        priority=TaskPriority(task_data.priority),
        due_date=task_data.due_date,
        status=TaskStatus.PENDING
    )
    
    db.add(study_task)
    db.commit()
    db.refresh(study_task)
    
    return BaseResponse(
        code=0,
        message="Study task created successfully",
        data={
            "id": study_task.id,
            "plan_id": study_task.study_plan_id,
            "title": study_task.title,
            "description": study_task.description,
            "status": study_task.status.value,
            "priority": study_task.priority.value,
            "due_date": study_task.due_date.isoformat() if study_task.due_date else None,
            "created_at": study_task.created_at.isoformat()
        }
    )


@router.get("/{plan_id}/tasks", response_model=BaseResponse[List[dict]])
async def get_study_tasks(
    plan_id: int,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get study tasks for a plan"""
    
    # Verify plan exists and belongs to user
    study_plan = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()
    
    if not study_plan:
        raise NotFoundError("Study plan not found")
    
    query = db.query(StudyTask).filter(StudyTask.study_plan_id == plan_id)
    
    if status:
        try:
            task_status = TaskStatus(status)
            query = query.filter(StudyTask.status == task_status)
        except ValueError:
            raise ValidationError("Invalid status value")
    
    study_tasks = query.all()
    
    task_responses = [
        {
            "id": task.id,
            "plan_id": task.study_plan_id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority.value,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "created_at": task.created_at.isoformat()
        }
        for task in study_tasks
    ]
    
    return BaseResponse(
        code=0,
        message="Study tasks retrieved successfully",
        data=task_responses
    )


@router.put("/{plan_id}/tasks/{task_id}", response_model=BaseResponse[dict])
async def update_study_task(
    plan_id: int,
    task_id: int,
    task_data: StudyTaskUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a study task"""
    
    # Verify plan exists and belongs to user
    study_plan = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()
    
    if not study_plan:
        raise NotFoundError("Study plan not found")
    
    # Get task
    study_task = db.query(StudyTask).filter(
        StudyTask.id == task_id,
        StudyTask.study_plan_id == plan_id
    ).first()
    
    if not study_task:
        raise NotFoundError("Study task not found")
    
    # Update fields
    if task_data.title is not None:
        study_task.title = task_data.title
    
    if task_data.description is not None:
        study_task.description = task_data.description
    
    if task_data.status is not None:
        try:
            study_task.status = TaskStatus(task_data.status)
            if task_data.status == TaskStatus.COMPLETED.value:
                study_task.completed_at = func.now()
        except ValueError:
            raise ValidationError("Invalid status value")
    
    if task_data.priority is not None:
        try:
            study_task.priority = TaskPriority(task_data.priority)
        except ValueError:
            raise ValidationError("Invalid priority value")
    
    if task_data.due_date is not None:
        study_task.due_date = task_data.due_date
    
    db.commit()
    db.refresh(study_task)
    
    return BaseResponse(
        code=0,
        message="Study task updated successfully",
        data={
            "id": study_task.id,
            "plan_id": study_task.study_plan_id,
            "title": study_task.title,
            "description": study_task.description,
            "status": study_task.status.value,
            "priority": study_task.priority.value,
            "due_date": study_task.due_date.isoformat() if study_task.due_date else None,
            "completed_at": study_task.completed_at.isoformat() if study_task.completed_at else None,
            "created_at": study_task.created_at.isoformat()
        }
    )


@router.delete("/{plan_id}/tasks/{task_id}", response_model=BaseResponse[None])
async def delete_study_task(
    plan_id: int,
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a study task"""
    
    # Verify plan exists and belongs to user
    study_plan = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()
    
    if not study_plan:
        raise NotFoundError("Study plan not found")
    
    # Get task
    study_task = db.query(StudyTask).filter(
        StudyTask.id == task_id,
        StudyTask.study_plan_id == plan_id
    ).first()
    
    if not study_task:
        raise NotFoundError("Study task not found")
    
    db.delete(study_task)
    db.commit()
    
    return BaseResponse(
        code=0,
        message="Study task deleted successfully",
        data=None
    )


@router.post("/test-ai-api", response_model=BaseResponse[dict])
async def test_ai_api(
    current_user: User = Depends(get_current_active_user)
):
    """Test OpenAI API connection and response"""
    
    try:
        logger.info(f"Testing AI API for user {current_user.id}")
        
        # Test with a simple prompt
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant. Please respond with a simple greeting."},
            {"role": "user", "content": "Hello! Please say 'AI API test successful' and provide a brief status."}
        ]
        
        # Call AI service directly
        response = await ai_service.generate_response(
            messages=test_messages,
            max_tokens=100,
            temperature=0.7
        )
        
        # Extract content
        content = ai_service.extract_content(response)
        tokens_used = ai_service.extract_tokens_used(response)
        
        logger.info(f"AI API test successful for user {current_user.id}")
        
        return BaseResponse(
            code=0,
            message="AI API test successful",
            data={
                "status": "success",
                "response": content,
                "tokens_used": tokens_used,
                "api_key_configured": bool(ai_service.api_key),
                "api_key_prefix": ai_service.api_key[:10] + "..." if ai_service.api_key else "None",
                "model": ai_service.model
            }
        )
        
    except ExternalServiceError as e:
        logger.error(f"AI API test failed for user {current_user.id}: {e}")
        return BaseResponse(
            code=1,
            message=f"AI API test failed: {str(e)}",
            data={
                "status": "error",
                "error": str(e),
                "api_key_configured": bool(ai_service.api_key),
                "api_key_prefix": ai_service.api_key[:10] + "..." if ai_service.api_key else "None",
                "model": ai_service.model
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in AI API test for user {current_user.id}: {e}")
        return BaseResponse(
            code=1,
            message=f"Unexpected error: {str(e)}",
            data={
                "status": "error",
                "error": str(e),
                "api_key_configured": bool(ai_service.api_key),
                "api_key_prefix": ai_service.api_key[:10] + "..." if ai_service.api_key else "None",
                "model": ai_service.model
            }
        )


@router.post("/test-gemini-sdk", response_model=BaseResponse[dict])
async def test_gemini_sdk():
    """Test Gemini API using the official SDK (no auth required)"""
    
    try:
        logger.info("Testing Gemini API with SDK (no auth)")
        
        # Test with SDK
        result = await ai_service.test_gemini_sdk()
        
        logger.info("Gemini SDK test successful")
        
        return BaseResponse(
            code=0,
            message="Gemini SDK test successful",
            data={
                **result,
                "api_key_configured": bool(ai_service.api_key),
                "api_key_prefix": ai_service.api_key[:10] + "..." if ai_service.api_key else "None",
                "model": ai_service.model
            }
        )
        
    except ExternalServiceError as e:
        logger.error(f"Gemini SDK test failed: {e}")
        return BaseResponse(
            code=1,
            message=f"Gemini SDK test failed: {str(e)}",
            data={
                "status": "error",
                "error": str(e),
                "api_key_configured": bool(ai_service.api_key),
                "api_key_prefix": ai_service.api_key[:10] + "..." if ai_service.api_key else "None",
                "model": ai_service.model,
                "is_real_ai": False
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in Gemini SDK test: {e}")
        return BaseResponse(
            code=1,
            message=f"Unexpected error: {str(e)}",
            data={
                "status": "error",
                "error": str(e),
                "api_key_configured": bool(ai_service.api_key),
                "api_key_prefix": ai_service.api_key[:10] + "..." if ai_service.api_key else "None",
                "model": ai_service.model,
                "is_real_ai": False
            }
        )


@router.post("/test-ai-api-direct", response_model=BaseResponse[dict])
async def test_ai_api_direct():
    """Test Gemini API directly without fallback mechanism (no auth required)"""
    
    try:
        logger.info("Testing Gemini API directly (no auth)")
        
        # Use the Gemini SDK test method directly
        result = await ai_service.test_gemini_sdk()
        
        logger.info("Direct Gemini API test successful")
        
        return BaseResponse(
            code=0,
            message="Direct Gemini API test successful",
            data={
                **result,
                "api_key_configured": bool(ai_service.api_key),
                "api_key_prefix": ai_service.api_key[:10] + "..." if ai_service.api_key else "None",
                "model": ai_service.model
            }
        )
    
    except ExternalServiceError as e:
        logger.error(f"Direct Gemini API test failed: {e}")
        return BaseResponse(
            code=1,
            message=f"Direct Gemini API test failed: {str(e)}",
            data={
                "status": "error",
                "error": str(e),
                "api_key_configured": bool(ai_service.api_key),
                "api_key_prefix": ai_service.api_key[:10] + "..." if ai_service.api_key else "None",
                "model": ai_service.model,
                "is_real_ai": False
            }
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in direct Gemini API test: {e}")
        return BaseResponse(
            code=1,
            message=f"Unexpected error: {str(e)}",
            data={
                "status": "error",
                "error": str(e),
                "api_key_configured": bool(ai_service.api_key),
                "api_key_prefix": ai_service.api_key[:10] + "..." if ai_service.api_key else "None",
                "model": ai_service.model,
                "is_real_ai": False
            }
        )

