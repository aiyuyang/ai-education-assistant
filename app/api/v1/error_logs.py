"""
Error logs API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.dependencies import get_current_active_user
from app.core.exceptions import NotFoundError, ValidationError
from app.db.database import get_db
from app.models.models import User, ErrorLog, ErrorLogStatus, ErrorLogDifficulty
from app.schemas.request import ErrorLogCreateRequest, ErrorLogUpdateRequest, PaginationRequest
from app.schemas.response import BaseResponse, ErrorLogResponse, PaginatedResponse

router = APIRouter()


@router.post("/", response_model=BaseResponse[ErrorLogResponse])
async def create_error_log(
    error_data: ErrorLogCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new error log"""
    
    # Check if user has reached maximum error logs limit
    max_logs = 1000  # This should come from system config
    current_logs_count = db.query(ErrorLog).filter(ErrorLog.user_id == current_user.id).count()
    
    if current_logs_count >= max_logs:
        raise ValidationError(f"Maximum error logs limit ({max_logs}) reached")
    
    # Create error log
    error_log = ErrorLog(
        user_id=current_user.id,
        subject=error_data.subject,
        topic=error_data.topic,
        question_content=error_data.question_content or error_data.question,
        question_image_url=error_data.question_image_url,
        correct_answer=error_data.correct_answer,
        explanation=error_data.explanation,
        difficulty=ErrorLogDifficulty(error_data.difficulty),
        status=ErrorLogStatus.UNRESOLVED,
        review_count=0,
        user_answer=error_data.user_answer,
    )
    
    db.add(error_log)
    db.commit()
    db.refresh(error_log)
    
    return BaseResponse(
        code=0,
        message="Error log created successfully",
        data=ErrorLogResponse(
            id=error_log.id,
            user_id=error_log.user_id,
            subject=error_log.subject,
            topic=error_log.topic,
            question=error_log.question_content,
            question_content=error_log.question_content,
            question_image_url=error_log.question_image_url,
            correct_answer=error_log.correct_answer,
            explanation=error_log.explanation,
            difficulty=error_log.difficulty.value,
            status=error_log.status.value,
            review_count=error_log.review_count,
            last_reviewed_at=error_log.last_reviewed_at.isoformat() if error_log.last_reviewed_at else None,
            created_at=error_log.created_at.isoformat(),
            updated_at=error_log.updated_at.isoformat()
        )
    )


@router.get("/", response_model=BaseResponse[List[ErrorLogResponse]])
async def get_my_error_logs(
    subject: Optional[str] = None,
    status: Optional[str] = None,
    difficulty: Optional[str] = None,
    pagination: PaginationRequest = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's error logs"""
    
    query = db.query(ErrorLog).filter(ErrorLog.user_id == current_user.id)
    
    if subject:
        query = query.filter(ErrorLog.subject == subject)
    
    if status:
        try:
            error_status = ErrorLogStatus(status)
            query = query.filter(ErrorLog.status == error_status)
        except ValueError:
            raise ValidationError("Invalid status value")
    
    if difficulty:
        try:
            error_difficulty = ErrorLogDifficulty(difficulty)
            query = query.filter(ErrorLog.difficulty == error_difficulty)
        except ValueError:
            raise ValidationError("Invalid difficulty value")
    
    # Apply pagination
    offset = (pagination.page - 1) * pagination.per_page
    error_logs = query.offset(offset).limit(pagination.per_page).all()
    
    log_responses = [
        ErrorLogResponse(
            id=log.id,
            user_id=log.user_id,
            subject=log.subject,
            topic=log.topic,
            question=log.question_content,
            question_content=log.question_content,
            question_image_url=log.question_image_url,
            correct_answer=log.correct_answer,
            explanation=log.explanation,
            difficulty=log.difficulty.value,
            status=log.status.value,
            review_count=log.review_count,
            last_reviewed_at=log.last_reviewed_at.isoformat() if log.last_reviewed_at else None,
            created_at=log.created_at.isoformat(),
            updated_at=log.updated_at.isoformat()
        )
        for log in error_logs
    ]
    
    return BaseResponse(
        code=0,
        message="Error logs retrieved successfully",
        data=log_responses
    )


@router.get("/{log_id}", response_model=BaseResponse[ErrorLogResponse])
async def get_error_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific error log"""
    
    error_log = db.query(ErrorLog).filter(
        ErrorLog.id == log_id,
        ErrorLog.user_id == current_user.id
    ).first()
    
    if not error_log:
        raise NotFoundError("Error log not found")
    
    return BaseResponse(
        code=0,
        message="Error log retrieved successfully",
        data=ErrorLogResponse(
            id=error_log.id,
            user_id=error_log.user_id,
            subject=error_log.subject,
            topic=error_log.topic,
            question=error_log.question_content,
            question_content=error_log.question_content,
            question_image_url=error_log.question_image_url,
            correct_answer=error_log.correct_answer,
            explanation=error_log.explanation,
            difficulty=error_log.difficulty.value,
            status=error_log.status.value,
            review_count=error_log.review_count,
            last_reviewed_at=error_log.last_reviewed_at.isoformat() if error_log.last_reviewed_at else None,
            created_at=error_log.created_at.isoformat(),
            updated_at=error_log.updated_at.isoformat()
        )
    )


@router.put("/{log_id}", response_model=BaseResponse[ErrorLogResponse])
async def update_error_log(
    log_id: int,
    log_data: ErrorLogUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an error log"""
    
    error_log = db.query(ErrorLog).filter(
        ErrorLog.id == log_id,
        ErrorLog.user_id == current_user.id
    ).first()
    
    if not error_log:
        raise NotFoundError("Error log not found")
    
    # Update fields
    if log_data.subject is not None:
        error_log.subject = log_data.subject
    
    if log_data.topic is not None:
        error_log.topic = log_data.topic
    
    if log_data.question_content is not None:
        error_log.question_content = log_data.question_content
    
    if log_data.question_image_url is not None:
        error_log.question_image_url = log_data.question_image_url
    
    if log_data.correct_answer is not None:
        error_log.correct_answer = log_data.correct_answer
    
    if log_data.explanation is not None:
        error_log.explanation = log_data.explanation
    
    if log_data.difficulty is not None:
        try:
            error_log.difficulty = ErrorLogDifficulty(log_data.difficulty)
        except ValueError:
            raise ValidationError("Invalid difficulty value")
    
    if log_data.status is not None:
        try:
            error_log.status = ErrorLogStatus(log_data.status)
        except ValueError:
            raise ValidationError("Invalid status value")
    
    db.commit()
    db.refresh(error_log)
    
    return BaseResponse(
        code=0,
        message="Error log updated successfully",
        data=ErrorLogResponse(
            id=error_log.id,
            user_id=error_log.user_id,
            subject=error_log.subject,
            topic=error_log.topic,
            question_content=error_log.question_content,
            question_image_url=error_log.question_image_url,
            correct_answer=error_log.correct_answer,
            explanation=error_log.explanation,
            difficulty=error_log.difficulty.value,
            status=error_log.status.value,
            review_count=error_log.review_count,
            last_reviewed_at=error_log.last_reviewed_at.isoformat() if error_log.last_reviewed_at else None,
            created_at=error_log.created_at.isoformat(),
            updated_at=error_log.updated_at.isoformat()
        )
    )


@router.delete("/{log_id}", response_model=BaseResponse[None])
async def delete_error_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an error log"""
    
    error_log = db.query(ErrorLog).filter(
        ErrorLog.id == log_id,
        ErrorLog.user_id == current_user.id
    ).first()
    
    if not error_log:
        raise NotFoundError("Error log not found")
    
    db.delete(error_log)
    db.commit()
    
    return BaseResponse(
        code=0,
        message="Error log deleted successfully",
        data=None
    )


@router.post("/{log_id}/review", response_model=BaseResponse[ErrorLogResponse])
async def review_error_log(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark an error log as reviewed"""
    
    error_log = db.query(ErrorLog).filter(
        ErrorLog.id == log_id,
        ErrorLog.user_id == current_user.id
    ).first()
    
    if not error_log:
        raise NotFoundError("Error log not found")
    
    # Update review information
    error_log.review_count += 1
    error_log.last_reviewed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(error_log)
    
    return BaseResponse(
        code=0,
        message="Error log marked as reviewed",
        data=ErrorLogResponse(
            id=error_log.id,
            user_id=error_log.user_id,
            subject=error_log.subject,
            topic=error_log.topic,
            question_content=error_log.question_content,
            question_image_url=error_log.question_image_url,
            correct_answer=error_log.correct_answer,
            explanation=error_log.explanation,
            difficulty=error_log.difficulty.value,
            status=error_log.status.value,
            review_count=error_log.review_count,
            last_reviewed_at=error_log.last_reviewed_at.isoformat() if error_log.last_reviewed_at else None,
            created_at=error_log.created_at.isoformat(),
            updated_at=error_log.updated_at.isoformat()
        )
    )


@router.post("/upload-image", response_model=BaseResponse[str])
async def upload_error_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload image for error log"""
    
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise ValidationError("Only JPEG, PNG, and GIF images are allowed")
    
    # Validate file size (10MB max)
    max_size = 10 * 1024 * 1024  # 10MB
    content = await file.read()
    if len(content) > max_size:
        raise ValidationError("File size exceeds 10MB limit")
    
    # In a real implementation, you would upload to a cloud storage service
    # For now, we'll just return a placeholder URL
    image_url = f"https://example.com/error-images/{current_user.id}_{file.filename}"
    
    return BaseResponse(
        code=0,
        message="Image uploaded successfully",
        data=image_url
    )


@router.get("/subjects/list", response_model=BaseResponse[List[str]])
async def get_subjects_list(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of subjects from user's error logs"""
    
    subjects = db.query(ErrorLog.subject).filter(
        ErrorLog.user_id == current_user.id,
        ErrorLog.subject.isnot(None)
    ).distinct().all()
    
    subject_list = [subject[0] for subject in subjects if subject[0]]
    
    return BaseResponse(
        code=0,
        message="Subjects retrieved successfully",
        data=subject_list
    )


@router.get("/stats/summary", response_model=BaseResponse[dict])
async def get_error_log_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get error log statistics"""
    
    total_logs = db.query(ErrorLog).filter(ErrorLog.user_id == current_user.id).count()
    unresolved_logs = db.query(ErrorLog).filter(
        ErrorLog.user_id == current_user.id,
        ErrorLog.status == ErrorLogStatus.UNRESOLVED
    ).count()
    resolved_logs = db.query(ErrorLog).filter(
        ErrorLog.user_id == current_user.id,
        ErrorLog.status == ErrorLogStatus.RESOLVED
    ).count()
    mastered_logs = db.query(ErrorLog).filter(
        ErrorLog.user_id == current_user.id,
        ErrorLog.status == ErrorLogStatus.MASTERED
    ).count()
    
    # Get difficulty distribution
    easy_logs = db.query(ErrorLog).filter(
        ErrorLog.user_id == current_user.id,
        ErrorLog.difficulty == ErrorLogDifficulty.EASY
    ).count()
    medium_logs = db.query(ErrorLog).filter(
        ErrorLog.user_id == current_user.id,
        ErrorLog.difficulty == ErrorLogDifficulty.MEDIUM
    ).count()
    hard_logs = db.query(ErrorLog).filter(
        ErrorLog.user_id == current_user.id,
        ErrorLog.difficulty == ErrorLogDifficulty.HARD
    ).count()
    
    stats = {
        "total_logs": total_logs,
        "unresolved_logs": unresolved_logs,
        "resolved_logs": resolved_logs,
        "mastered_logs": mastered_logs,
        "difficulty_distribution": {
            "easy": easy_logs,
            "medium": medium_logs,
            "hard": hard_logs
        },
        "resolution_rate": round((resolved_logs + mastered_logs) / total_logs * 100, 2) if total_logs > 0 else 0
    }
    
    return BaseResponse(
        code=0,
        message="Error log statistics retrieved successfully",
        data=stats
    )

