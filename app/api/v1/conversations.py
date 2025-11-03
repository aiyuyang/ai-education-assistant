"""
Conversations API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.dependencies import get_current_active_user
from app.core.exceptions import NotFoundError, ValidationError
from app.db.database import get_db
from app.models.models import User, Conversation, Message, MessageRole, ContentType
from app.schemas.request import ConversationCreateRequest, MessageCreateRequest, PaginationRequest
from app.schemas.response import BaseResponse, ConversationResponse, MessageResponse, PaginatedResponse

router = APIRouter()


@router.post("/", response_model=BaseResponse[ConversationResponse])
async def create_conversation(
    conversation_data: ConversationCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation"""
    
    # Check if user has reached maximum conversations limit
    max_conversations = 100  # This should come from system config
    current_conversations_count = db.query(Conversation).filter(
        Conversation.user_id == current_user.id,
        Conversation.is_active == True
    ).count()
    
    if current_conversations_count >= max_conversations:
        raise ValidationError(f"Maximum conversations limit ({max_conversations}) reached")
    
    # Create conversation
    conversation = Conversation(
        user_id=current_user.id,
        title=conversation_data.title or "New Conversation",
        subject=conversation_data.subject,
        difficulty_level=conversation_data.difficulty_level,
        is_public=conversation_data.is_public,
        is_active=True
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return BaseResponse(
        code=0,
        message="Conversation created successfully",
        data=ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            subject=conversation.subject,
            difficulty_level=conversation.difficulty_level,
            is_public=conversation.is_public,
            summary=conversation.summary,
            is_active=conversation.is_active,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat()
        )
    )


@router.get("/", response_model=BaseResponse[List[ConversationResponse]])
async def get_my_conversations(
    is_active: Optional[bool] = None,
    pagination: PaginationRequest = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's conversations"""
    
    query = db.query(Conversation).filter(Conversation.user_id == current_user.id)
    
    if is_active is not None:
        query = query.filter(Conversation.is_active == is_active)
    
    # Apply pagination
    offset = (pagination.page - 1) * pagination.per_page
    conversations = query.offset(offset).limit(pagination.per_page).all()
    
    conversation_responses = [
        ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            subject=conv.subject,
            difficulty_level=conv.difficulty_level,
            is_public=conv.is_public,
            summary=conv.summary,
            is_active=conv.is_active,
            created_at=conv.created_at.isoformat(),
            updated_at=conv.updated_at.isoformat()
        )
        for conv in conversations
    ]
    
    return BaseResponse(
        code=0,
        message="Conversations retrieved successfully",
        data=conversation_responses
    )


@router.get("/{conversation_id}", response_model=BaseResponse[ConversationResponse])
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation"""
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    return BaseResponse(
        code=0,
        message="Conversation retrieved successfully",
        data=ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            summary=conversation.summary,
            is_active=conversation.is_active,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat()
        )
    )


@router.put("/{conversation_id}", response_model=BaseResponse[ConversationResponse])
async def update_conversation(
    conversation_id: int,
    title: Optional[str] = None,
    summary: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a conversation"""
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Update fields
    if title is not None:
        conversation.title = title
    
    if summary is not None:
        conversation.summary = summary
    
    if is_active is not None:
        conversation.is_active = is_active
    
    db.commit()
    db.refresh(conversation)
    
    return BaseResponse(
        code=0,
        message="Conversation updated successfully",
        data=ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            summary=conversation.summary,
            is_active=conversation.is_active,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat()
        )
    )


@router.delete("/{conversation_id}", response_model=BaseResponse[None])
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Soft delete by marking as inactive
    conversation.is_active = False
    db.commit()
    
    return BaseResponse(
        code=0,
        message="Conversation deleted successfully",
        data=None
    )


# Message endpoints

@router.post("/{conversation_id}/messages", response_model=BaseResponse[MessageResponse])
async def create_message(
    conversation_id: int,
    message_data: MessageCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new message in a conversation"""
    
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
        Conversation.is_active == True
    ).first()
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Check conversation length limit
    max_messages = 100  # This should come from system config
    current_messages_count = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).count()
    
    if current_messages_count >= max_messages:
        raise ValidationError(f"Maximum messages limit ({max_messages}) reached for this conversation")
    
    # Create message
    # Map role string to MessageRole enum
    role_map = {
        'user': MessageRole.USER,
        'assistant': MessageRole.ASSISTANT,
        'system': MessageRole.SYSTEM
    }
    message = Message(
        conversation_id=conversation_id,
        role=role_map.get(message_data.role, MessageRole.USER),
        content=message_data.content,
        content_type=ContentType(message_data.content_type),
        metadata_json=message_data.metadata_json
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return BaseResponse(
        code=0,
        message="Message created successfully",
        data=MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role.value,
            content=message.content,
            content_type=message.content_type.value,
            metadata=message.metadata,
            tokens_used=message.tokens_used,
            created_at=message.created_at.isoformat()
        )
    )


@router.get("/{conversation_id}/messages", response_model=BaseResponse[List[MessageResponse]])
async def get_conversation_messages(
    conversation_id: int,
    pagination: PaginationRequest = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get messages for a conversation"""
    
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Get messages
    query = db.query(Message).filter(Message.conversation_id == conversation_id)
    
    # Apply pagination
    offset = (pagination.page - 1) * pagination.per_page
    messages = query.offset(offset).limit(pagination.per_page).all()
    
    message_responses = [
        MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role.value,
            content=msg.content,
            content_type=msg.content_type.value,
            metadata_json=msg.metadata_json,
            tokens_used=msg.tokens_used,
            created_at=msg.created_at.isoformat()
        )
        for msg in messages
    ]
    
    return BaseResponse(
        code=0,
        message="Messages retrieved successfully",
        data=message_responses
    )


@router.post("/{conversation_id}/messages/{message_id}/ai-response", response_model=BaseResponse[MessageResponse])
async def generate_ai_response(
    conversation_id: int,
    message_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate AI response for a message"""
    
    # Verify conversation exists and belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
        Conversation.is_active == True
    ).first()
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Verify message exists
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.conversation_id == conversation_id,
        Message.role == MessageRole.USER
    ).first()
    
    if not message:
        raise NotFoundError("Message not found")
    
    # In a real implementation, this would call the AI service
    # For now, we'll create a mock response
    ai_response = Message(
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT,
        content="This is a mock AI response. In a real implementation, this would be generated by calling an external AI service.",
        content_type=ContentType.TEXT,
        tokens_used=50  # Mock token count
    )
    
    db.add(ai_response)
    db.commit()
    db.refresh(ai_response)
    
    return BaseResponse(
        code=0,
        message="AI response generated successfully",
        data=MessageResponse(
            id=ai_response.id,
            conversation_id=ai_response.conversation_id,
            role=ai_response.role.value,
            content=ai_response.content,
            content_type=ai_response.content_type.value,
            metadata_json=ai_response.metadata_json,
            tokens_used=ai_response.tokens_used,
            created_at=ai_response.created_at.isoformat()
        )
    )


@router.get("/stats/summary", response_model=BaseResponse[dict])
async def get_conversation_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get conversation statistics"""
    
    total_conversations = db.query(Conversation).filter(Conversation.user_id == current_user.id).count()
    active_conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id,
        Conversation.is_active == True
    ).count()
    
    total_messages = db.query(Message).join(Conversation).filter(
        Conversation.user_id == current_user.id
    ).count()
    
    user_messages = db.query(Message).join(Conversation).filter(
        Conversation.user_id == current_user.id,
        Message.role == MessageRole.USER
    ).count()
    
    ai_messages = db.query(Message).join(Conversation).filter(
        Conversation.user_id == current_user.id,
        Message.role == MessageRole.ASSISTANT
    ).count()
    
    stats = {
        "total_conversations": total_conversations,
        "active_conversations": active_conversations,
        "total_messages": total_messages,
        "user_messages": user_messages,
        "ai_messages": ai_messages,
        "average_messages_per_conversation": round(total_messages / total_conversations, 2) if total_conversations > 0 else 0
    }
    
    return BaseResponse(
        code=0,
        message="Conversation statistics retrieved successfully",
        data=stats
    )
