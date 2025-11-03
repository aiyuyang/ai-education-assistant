"""
External AI service integration module (Gemini)
"""
import httpx
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import google.generativeai as genai

from app.core.config import settings
from app.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class AIService:
    """AI service client for external API integration"""
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        # Increase timeout to better accommodate long JSON outputs
        self.timeout = 60.0
        
        # Configure Gemini API
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate AI response from messages using Gemini"""
        
        if not self.api_key:
            raise ExternalServiceError("Gemini API key not configured")
        
        try:
            # Convert messages to Gemini format
            prompt = self._convert_messages_to_prompt(messages)
            
            # Generate content using Gemini
            response = self.client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )
            )
            
            # Convert Gemini response to OpenAI-like format
            result = {
                "choices": [
                    {
                        "message": {
                            "content": response.text
                        }
                    }
                ],
                "usage": {
                    "total_tokens": len(response.text.split()) * 2,  # Rough estimate
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(response.text.split())
                }
            }
            
            return result
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            # If quota exceeded or other API errors, fall back to mock data
            if "quota" in str(e).lower() or "429" in str(e):
                logger.warning("Gemini API quota exceeded, falling back to mock data")
                return self._generate_mock_response()
            raise ExternalServiceError(f"Gemini API error: {str(e)}")
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI messages format to Gemini prompt format"""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts)
    
    async def test_gemini_sdk(self, test_input: str = "Hello! Please say 'Gemini API test successful' and provide a brief status.") -> Dict[str, Any]:
        """Test Gemini API using the official SDK"""
        
        if not self.api_key:
            raise ExternalServiceError("Gemini API key not configured")
        
        try:
            logger.info("Testing Gemini API using official SDK")
            
            # Test with Gemini SDK
            response = self.client.generate_content(
                test_input,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=100,
                    temperature=0.7,
                )
            )
            
            logger.info("Gemini API test successful")
            return {
                "status": "success",
                "response": response.text,
                "tokens_used": len(response.text.split()) * 2,  # Rough estimate
                "model": self.model,
                "api_format": "gemini",
                "is_real_ai": True
            }
                
        except Exception as e:
            logger.error(f"Gemini SDK test failed: {e}")
            raise ExternalServiceError(f"Gemini SDK test failed: {str(e)}")
    
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
    
    async def generate_ai_study_plan(
        self,
        subject: str,
        time_frame: str,
        learning_goals: List[str],
        current_level: str = "beginner",
        study_hours_per_week: int = 10
    ) -> Dict[str, Any]:
        """Generate AI-powered personalized study plan with detailed structure"""
        
        # 检查API密钥配置，如果没有配置则使用模拟数据
        logger.info(f"Gemini API Key configured: {bool(self.api_key)}")
        if not self.api_key:
            raise ExternalServiceError("Gemini API key not configured. Please set GEMINI_API_KEY in environment.")
        
        system_prompt = """你是一位专业的教育AI助手，专门为学生创建个性化学习计划。请根据学生的学科、时间安排和学习目标，生成详细、实用且可执行的学习计划。

严格的格式要求：
- 只输出合法的 JSON（可被 JSON.parse 解析）。
- 不要输出任何解释性文字或 Markdown 代码块标记。
- 所有字符串中不得包含未转义的双引号；如需包含，请使用单引号或使用 \\" 进行转义。

请按照以下JSON格式返回学习计划：
{
    "plan_title": "学习计划标题",
    "overview": "计划概述",
    "learning_objectives": ["目标1", "目标2", "目标3"],
    "weekly_schedule": [
        {
            "week": 1,
            "focus": "本周重点",
            "tasks": [
                {
                    "title": "任务标题",
                    "description": "任务描述",
                    "estimated_hours": 2,
                    "priority": "high|medium|low",
                    "resources": ["资源1", "资源2"]
                }
            ]
        }
    ],
    "milestones": [
        {
            "week": 2,
            "milestone": "里程碑描述",
            "assessment": "评估方式"
        }
    ],
    "resources": ["推荐资源1", "推荐资源2"],
    "tips": ["学习建议1", "学习建议2"]
}"""
        
        user_prompt = f"""请为以下学习需求创建个性化学习计划：
        
学科：{subject}
学习时间：{time_frame}
当前水平：{current_level}
每周学习时间：{study_hours_per_week}小时
学习目标：{', '.join(learning_goals)}

请确保计划：
1. 符合时间安排和学习目标
2. 任务分解合理，难度递进
3. 包含具体的学习资源和评估方式
4. 提供实用的学习建议"""

        # Use REST API directly (more reliable than SDK for newer models)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        try:
            # Use REST API directly for better compatibility
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
            
            headers = {
                "x-goog-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": full_prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    # Use a higher token limit to avoid truncation on long plans
                    "maxOutputTokens": 8192,
                    "temperature": 0.2,
                    "responseMimeType": "application/json",
                    # Strongly enforce the expected JSON shape to reduce invalid outputs
                    "responseSchema": {
                        "type": "object",
                        "properties": {
                            "plan_title": {"type": "string"},
                            "overview": {"type": "string", "pattern": '^[^"]*$'},
                            "learning_objectives": {
                                "type": "array",
                                "items": {"type": "string", "pattern": '^[^"]*$'}
                            },
                            "weekly_schedule": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "week": {"type": "integer"},
                                        "focus": {"type": "string", "pattern": '^[^"]*$'},
                                        "tasks": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "title": {"type": "string", "pattern": '^[^"]*$'},
                                                    "description": {"type": "string", "pattern": '^[^"]*$'},
                                                    "estimated_hours": {"type": "number"},
                                                    "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                                                    "resources": {
                                                        "type": "array",
                                                        "items": {"type": "string", "pattern": '^[^"]*$'}
                                                    }
                                                },
                                                "required": ["title", "description", "estimated_hours", "priority", "resources"]
                                            }
                                        }
                                    },
                                    "required": ["week", "focus", "tasks"]
                                }
                            },
                            "milestones": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "week": {"type": "integer"},
                                        "milestone": {"type": "string", "pattern": '^[^"]*$'},
                                        "assessment": {"type": "string", "pattern": '^[^"]*$'}
                                    },
                                    "required": ["week", "milestone", "assessment"]
                                }
                            },
                            "resources": {"type": "array", "items": {"type": "string", "pattern": '^[^"]*$'}},
                            "tips": {"type": "array", "items": {"type": "string", "pattern": '^[^"]*$'}}
                        },
                        "required": ["plan_title", "overview", "learning_objectives", "weekly_schedule"]
                    }
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                rest_response = await client.post(api_url, headers=headers, json=payload)
                rest_response.raise_for_status()
                rest_data = rest_response.json()
                
                # Check if response contains candidates
                if "candidates" not in rest_data or not rest_data["candidates"]:
                    error_msg = rest_data.get("error", {}).get("message", "No candidates in response")
                    logger.error(f"Gemini API returned no candidates: {rest_data}")
                    raise ExternalServiceError(f"Gemini API error: {error_msg}")
                
                candidate = rest_data["candidates"][0]
                
                # Check finish reason
                finish_reason = candidate.get("finishReason", "")
                
                # Check if there's content with parts (even if finish reason is MAX_TOKENS, we might still have content)
                if "content" not in candidate or "parts" not in candidate["content"]:
                    if finish_reason == "SAFETY":
                        logger.warning("Response blocked by safety filters, trying with relaxed settings")
                        # Try again with more relaxed safety settings
                        payload["safetySettings"] = [
                            {
                                "category": "HARM_CATEGORY_HARASSMENT",
                                "threshold": "BLOCK_ONLY_HIGH"
                            },
                            {
                                "category": "HARM_CATEGORY_HATE_SPEECH",
                                "threshold": "BLOCK_ONLY_HIGH"
                            },
                            {
                                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                                "threshold": "BLOCK_ONLY_HIGH"
                            },
                            {
                                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                                "threshold": "BLOCK_ONLY_HIGH"
                            }
                        ]
                        rest_response = await client.post(api_url, headers=headers, json=payload)
                        rest_response.raise_for_status()
                        rest_data = rest_response.json()
                        candidate = rest_data["candidates"][0]
                    else:
                        error_msg = f"No content in response. Finish reason: {finish_reason}"
                        logger.error(f"Gemini API error: {error_msg}")
                        raise ExternalServiceError(f"Gemini API error: {error_msg}")
                
                # Extract text from REST API response
                parts = candidate["content"]["parts"]
                if not parts or "text" not in parts[0]:
                    error_msg = f"No text in response parts. Finish reason: {finish_reason}"
                    logger.error(f"Gemini API error: {error_msg}")
                    raise ExternalServiceError(f"Gemini API error: {error_msg}")
                
                response_text = parts[0]["text"]
                
                # Log finish reason for debugging
                if finish_reason == "MAX_TOKENS":
                    logger.warning(f"Response hit MAX_TOKENS limit but content is available ({len(response_text)} chars)")
                    
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("error", {}).get("message", str(e))
            except:
                error_detail = str(e)
            logger.error(f"Gemini REST API HTTP error: {error_detail}")
            raise ExternalServiceError(f"Gemini API HTTP error: {error_detail}")
        except Exception as rest_error:
            logger.error(f"Gemini REST API error in study plan generation: {rest_error}")
            raise ExternalServiceError(f"Gemini API error: {str(rest_error)}")
        
        # Convert Gemini response to OpenAI-like format
        result = {
            "choices": [
                {
                    "message": {
                        "content": response_text
                    }
                }
            ],
            "usage": {
                "total_tokens": len(response_text.split()) * 2,  # Rough estimate
                "prompt_tokens": len(full_prompt.split()),
                "completion_tokens": len(response_text.split())
            }
        }
        
        return result

    async def repair_json_output(self, raw_text: str) -> str:
        """Attempt to repair near-JSON text to valid JSON using the model with schema enforcement."""
        if not self.api_key:
            raise ExternalServiceError("Gemini API key not configured")

        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        repair_prompt = (
            "下面是一段接近 JSON 但不合法的文本。请修复为合法、可被 JSON.parse 解析的 JSON。\n"
            "严格遵循此前学习计划的 schema 字段与类型，仅输出 JSON，不要额外说明或注释。\n\n"
            f"原始文本：\n{raw_text}"
        )

        payload = {
            "contents": [{"parts": [{"text": repair_prompt}]}],
            "generationConfig": {
                # Increase repair budget to handle large near-JSON texts
                "maxOutputTokens": 8192,
                "temperature": 0.1,
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "object",
                    "properties": {
                        "plan_title": {"type": "string", "pattern": '^[^"]*$'},
                        "overview": {"type": "string", "pattern": '^[^"]*$'},
                        "learning_objectives": {"type": "array", "items": {"type": "string", "pattern": '^[^"]*$'}},
                        "weekly_schedule": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "week": {"type": "integer"},
                                    "focus": {"type": "string", "pattern": '^[^"]*$'},
                                    "tasks": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "title": {"type": "string", "pattern": '^[^"]*$'},
                                                "description": {"type": "string", "pattern": '^[^"]*$'},
                                                "estimated_hours": {"type": "number"},
                                                "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                                                "resources": {"type": "array", "items": {"type": "string", "pattern": '^[^"]*$'}}
                                            },
                                            "required": ["title", "description", "estimated_hours", "priority", "resources"]
                                        }
                                    }
                                },
                                "required": ["week", "focus", "tasks"]
                            }
                        },
                        "milestones": {"type": "array", "items": {"type": "object", "properties": {"week": {"type": "integer"}, "milestone": {"type": "string", "pattern": '^[^"]*$'}, "assessment": {"type": "string", "pattern": '^[^"]*$'}}, "required": ["week", "milestone", "assessment"]}},
                        "resources": {"type": "array", "items": {"type": "string", "pattern": '^[^"]*$'}},
                        "tips": {"type": "array", "items": {"type": "string", "pattern": '^[^"]*$'}}
                    },
                    "required": ["plan_title", "overview", "learning_objectives", "weekly_schedule"]
                }
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                rest_response = await client.post(api_url, headers=headers, json=payload)
                rest_response.raise_for_status()
                rest_data = rest_response.json()
            candidate = rest_data.get("candidates", [{}])[0]
            parts = candidate.get("content", {}).get("parts", [])
            if parts and "text" in parts[0]:
                return parts[0]["text"]
            raise ExternalServiceError("No repaired JSON returned by AI")
        except Exception as e:
            raise ExternalServiceError(f"JSON repair failed: {e}")
    
    def _generate_mock_study_plan(
        self,
        subject: str,
        time_frame: str,
        learning_goals: List[str],
        current_level: str,
        study_hours_per_week: int
    ) -> Dict[str, Any]:
        """Generate mock study plan for testing when API key is not configured"""
        
        # 根据学科生成不同的学习计划
        subject_plans = {
            "python": {
                "plan_title": f"{subject.upper()} 编程学习计划",
                "overview": f"这是一个为期{time_frame}的{subject}编程学习计划，适合{current_level}水平的学习者。",
                "learning_objectives": learning_goals + ["掌握基本语法", "完成实践项目"],
                "weekly_schedule": [
                    {
                        "week": 1,
                        "focus": "基础语法学习",
                        "tasks": [
                            {
                                "title": "变量和数据类型",
                                "description": "学习Python的基本数据类型和变量声明",
                                "estimated_hours": study_hours_per_week // 2,
                                "priority": "high",
                                "resources": ["Python官方文档", "在线教程"]
                            },
                            {
                                "title": "控制流程",
                                "description": "掌握if语句、循环等控制结构",
                                "estimated_hours": study_hours_per_week // 2,
                                "priority": "high",
                                "resources": ["练习题库", "编程练习"]
                            }
                        ]
                    },
                    {
                        "week": 2,
                        "focus": "函数和模块",
                        "tasks": [
                            {
                                "title": "函数定义和调用",
                                "description": "学习如何定义和使用函数",
                                "estimated_hours": study_hours_per_week // 2,
                                "priority": "medium",
                                "resources": ["函数教程", "实践项目"]
                            },
                            {
                                "title": "模块和包",
                                "description": "了解Python模块系统",
                                "estimated_hours": study_hours_per_week // 2,
                                "priority": "medium",
                                "resources": ["标准库文档", "第三方库"]
                            }
                        ]
                    }
                ],
                "milestones": [
                    {
                        "week": 1,
                        "milestone": "完成基础语法学习",
                        "assessment": "编写简单的Python程序"
                    },
                    {
                        "week": 2,
                        "milestone": "掌握函数和模块",
                        "assessment": "完成小型项目"
                    }
                ],
                "resources": [
                    "Python官方文档",
                    "《Python编程：从入门到实践》",
                    "LeetCode Python题库",
                    "GitHub开源项目"
                ],
                "tips": [
                    "每天坚持编程练习",
                    "多阅读优秀的Python代码",
                    "参与开源项目",
                    "建立学习笔记"
                ]
            },
            "数学": {
                "plan_title": f"{subject} 数学学习计划",
                "overview": f"这是一个系统性的{subject}数学学习计划，适合{current_level}水平的学习者。",
                "learning_objectives": learning_goals + ["掌握核心概念", "提高解题能力"],
                "weekly_schedule": [
                    {
                        "week": 1,
                        "focus": "基础概念复习",
                        "tasks": [
                            {
                                "title": "核心概念学习",
                                "description": "系统学习基础数学概念",
                                "estimated_hours": study_hours_per_week // 2,
                                "priority": "high",
                                "resources": ["教材", "在线课程"]
                            },
                            {
                                "title": "基础练习",
                                "description": "完成基础练习题",
                                "estimated_hours": study_hours_per_week // 2,
                                "priority": "high",
                                "resources": ["练习册", "在线题库"]
                            }
                        ]
                    }
                ],
                "milestones": [
                    {
                        "week": 1,
                        "milestone": "掌握基础概念",
                        "assessment": "完成章节测试"
                    }
                ],
                "resources": [
                    "数学教材",
                    "Khan Academy",
                    "数学练习题库",
                    "数学视频教程"
                ],
                "tips": [
                    "理解概念比记忆公式更重要",
                    "多做练习题巩固知识",
                    "建立错题本",
                    "定期复习"
                ]
            }
        }
        
        # 获取对应学科的计划，如果没有则使用通用计划
        plan_data = subject_plans.get(subject.lower(), {
            "plan_title": f"{subject} 学习计划",
            "overview": f"这是一个为期{time_frame}的{subject}学习计划，适合{current_level}水平的学习者。",
            "learning_objectives": learning_goals,
            "weekly_schedule": [
                {
                    "week": 1,
                    "focus": "基础学习",
                    "tasks": [
                        {
                            "title": "基础知识学习",
                            "description": f"学习{subject}的基础知识和核心概念",
                            "estimated_hours": study_hours_per_week,
                            "priority": "high",
                            "resources": ["教材", "在线课程", "视频教程"]
                        }
                    ]
                }
            ],
            "milestones": [
                {
                    "week": 1,
                    "milestone": "完成基础学习",
                    "assessment": "自测和练习"
                }
            ],
            "resources": [
                "相关教材",
                "在线课程",
                "练习题库",
                "学习社区"
            ],
            "tips": [
                "保持规律学习",
                "及时复习巩固",
                "多做练习",
                "寻求帮助"
            ]
        })
        
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(plan_data, ensure_ascii=False, indent=2)
                    }
                }
            ],
            "usage": {
                "total_tokens": 500
            }
        }
    
    def _generate_mock_response(self) -> Dict[str, Any]:
        """Generate a mock OpenAI API response"""
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "plan_title": "AI学习计划（模拟数据）",
                            "overview": "这是一个模拟的学习计划，因为OpenAI API配额已用完。",
                            "learning_objectives": ["学习目标1", "学习目标2"],
                            "weekly_schedule": [
                                {
                                    "week": 1,
                                    "focus": "基础学习",
                                    "tasks": [
                                        {
                                            "title": "基础任务",
                                            "description": "学习基础知识",
                                            "estimated_hours": 5,
                                            "priority": "high",
                                            "resources": ["教材", "在线课程"]
                                        }
                                    ]
                                }
                            ],
                            "milestones": [
                                {
                                    "week": 1,
                                    "milestone": "完成基础学习",
                                    "assessment": "自测"
                                }
                            ],
                            "resources": ["教材", "在线课程"],
                            "tips": ["保持学习", "及时复习"]
                        }, ensure_ascii=False, indent=2)
                    }
                }
            ],
            "usage": {
                "total_tokens": 100
            }
        }
    
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

