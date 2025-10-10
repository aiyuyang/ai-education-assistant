"""
External AI service integration module
"""
import httpx
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from app.core.config import settings
from app.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class AIService:
    """AI service client for external API integration"""
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.base_url = settings.openai_base_url
        self.model = settings.openai_model
        self.timeout = 30.0
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate AI response from messages"""
        
        if not self.api_key:
            raise ExternalServiceError("AI service API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    logger.error(f"AI service error: {response.status_code} - {response.text}")
                    raise ExternalServiceError(f"AI service returned status {response.status_code}")
                
                result = response.json()
                
                if "error" in result:
                    logger.error(f"AI service error: {result['error']}")
                    raise ExternalServiceError(f"AI service error: {result['error']['message']}")
                
                return result
                
        except httpx.TimeoutException:
            logger.error("AI service request timeout")
            raise ExternalServiceError("AI service request timeout")
        except httpx.RequestError as e:
            logger.error(f"AI service request error: {e}")
            raise ExternalServiceError(f"AI service request error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected AI service error: {e}")
            raise ExternalServiceError(f"Unexpected error: {str(e)}")
    
    async def generate_conversation_response(
        self,
        conversation_history: List[Dict[str, str]],
        user_message: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate response for a conversation"""
        
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return await self.generate_response(messages)
    
    async def generate_study_plan(
        self,
        subject: str,
        level: str,
        duration: str,
        goals: List[str]
    ) -> Dict[str, Any]:
        """Generate a personalized study plan"""
        
        system_prompt = """You are an AI education assistant specialized in creating personalized study plans. 
        Create detailed, structured study plans that are practical and achievable."""
        
        user_prompt = f"""
        Create a study plan for:
        - Subject: {subject}
        - Level: {level}
        - Duration: {duration}
        - Goals: {', '.join(goals)}
        
        Please provide a structured plan with specific tasks, timelines, and learning objectives.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self.generate_response(messages, max_tokens=1500)
    
    async def explain_error(
        self,
        question: str,
        user_answer: str,
        correct_answer: str,
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """Explain an error and provide learning guidance"""
        
        system_prompt = """You are an AI education assistant specialized in explaining errors and providing 
        educational guidance. Help students understand their mistakes and learn from them."""
        
        user_prompt = f"""
        Please explain this error and provide learning guidance:
        
        Question: {question}
        Student's Answer: {user_answer}
        Correct Answer: {correct_answer}
        Subject: {subject or 'Not specified'}
        
        Provide:
        1. Explanation of why the student's answer is incorrect
        2. Step-by-step solution
        3. Key concepts to review
        4. Similar practice suggestions
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self.generate_response(messages, max_tokens=1200)
    
    async def generate_quiz_questions(
        self,
        topic: str,
        difficulty: str,
        count: int = 5,
        question_type: str = "multiple_choice"
    ) -> Dict[str, Any]:
        """Generate quiz questions for a topic"""
        
        system_prompt = """You are an AI education assistant specialized in creating educational quiz questions. 
        Create high-quality questions that test understanding and knowledge."""
        
        user_prompt = f"""
        Create {count} {question_type} questions about {topic} at {difficulty} level.
        
        For each question, provide:
        - The question text
        - Multiple choice options (if applicable)
        - Correct answer
        - Explanation
        
        Format the response as JSON.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self.generate_response(messages, max_tokens=2000)
    
    async def summarize_conversation(
        self,
        conversation_messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Summarize a conversation"""
        
        system_prompt = """You are an AI assistant that creates concise summaries of educational conversations. 
        Extract key topics, learning objectives, and important insights."""
        
        # Truncate conversation if too long
        if len(conversation_messages) > 20:
            conversation_messages = conversation_messages[-20:]
        
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in conversation_messages
        ])
        
        user_prompt = f"""
        Please summarize this educational conversation:
        
        {conversation_text}
        
        Provide:
        1. Main topics discussed
        2. Key learning points
        3. Questions answered
        4. Suggested follow-up topics
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self.generate_response(messages, max_tokens=800)
    
    def extract_tokens_used(self, response: Dict[str, Any]) -> int:
        """Extract token usage from AI response"""
        try:
            usage = response.get("usage", {})
            return usage.get("total_tokens", 0)
        except Exception:
            return 0
    
    def extract_content(self, response: Dict[str, Any]) -> str:
        """Extract content from AI response"""
        try:
            choices = response.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""
        except Exception:
            return ""


# Global AI service instance
ai_service = AIService()


# Utility functions for common AI operations
async def generate_ai_response_for_message(
    conversation_history: List[Dict[str, str]],
    user_message: str,
    context: Optional[str] = None
) -> str:
    """Generate AI response for a user message"""
    
    system_prompt = """You are an AI education assistant. Help students learn by providing clear, 
    accurate explanations and guidance. Be encouraging and supportive."""
    
    if context:
        system_prompt += f"\n\nContext: {context}"
    
    try:
        response = await ai_service.generate_conversation_response(
            conversation_history=conversation_history,
            user_message=user_message,
            system_prompt=system_prompt
        )
        
        return ai_service.extract_content(response)
        
    except ExternalServiceError as e:
        logger.error(f"AI service error: {e}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again later."
    except Exception as e:
        logger.error(f"Unexpected error in AI response generation: {e}")
        return "I apologize, but I encountered an unexpected error. Please try again later."


async def generate_study_plan_suggestions(
    subject: str,
    level: str,
    duration: str,
    goals: List[str]
) -> str:
    """Generate study plan suggestions"""
    
    try:
        response = await ai_service.generate_study_plan(
            subject=subject,
            level=level,
            duration=duration,
            goals=goals
        )
        
        return ai_service.extract_content(response)
        
    except ExternalServiceError as e:
        logger.error(f"AI service error in study plan generation: {e}")
        return "I apologize, but I'm having trouble generating a study plan right now. Please try again later."
    except Exception as e:
        logger.error(f"Unexpected error in study plan generation: {e}")
        return "I apologize, but I encountered an unexpected error. Please try again later."


async def explain_error_with_guidance(
    question: str,
    user_answer: str,
    correct_answer: str,
    subject: Optional[str] = None
) -> str:
    """Explain an error and provide learning guidance"""
    
    try:
        response = await ai_service.explain_error(
            question=question,
            user_answer=user_answer,
            correct_answer=correct_answer,
            subject=subject
        )
        
        return ai_service.extract_content(response)
        
    except ExternalServiceError as e:
        logger.error(f"AI service error in error explanation: {e}")
        return "I apologize, but I'm having trouble explaining this error right now. Please try again later."
    except Exception as e:
        logger.error(f"Unexpected error in error explanation: {e}")
        return "I apologize, but I encountered an unexpected error. Please try again later."

