"""
Study plans API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.dependencies import get_current_active_user
from app.core.exceptions import NotFoundError, ValidationError
from app.db.database import get_db
from app.models.models import User, StudyPlan, StudyTask, PlanStatus, TaskStatus, TaskPriority
from app.schemas.request import (
    StudyPlanCreateRequest, StudyPlanUpdateRequest, 
    StudyTaskCreateRequest, StudyTaskUpdateRequest,
    PaginationRequest
)
from app.schemas.response import BaseResponse, StudyPlanResponse, PaginatedResponse

router = APIRouter()


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
            status=study_plan.status.value,
            start_date=study_plan.start_date.isoformat() if study_plan.start_date else None,
            end_date=study_plan.end_date.isoformat() if study_plan.end_date else None,
            created_at=study_plan.created_at.isoformat(),
            updated_at=study_plan.updated_at.isoformat()
        )
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

