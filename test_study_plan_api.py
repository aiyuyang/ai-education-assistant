#!/usr/bin/env python3
"""
学习计划生成模块API测试脚本
测试第2周开发任务的完成情况
"""

import asyncio
import httpx
import json
import time
from datetime import datetime


class StudyPlanAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None
        self.saved_plan_id = None
        
    async def test_user_registration_and_login(self):
        """测试用户注册和登录"""
        print("🔐 测试用户认证...")
        
        async with httpx.AsyncClient() as client:
            # 注册用户
            register_data = {
                "username": f"testuser_{int(time.time())}",
                "email": f"test_{int(time.time())}@example.com",
                "password": "testpassword123",
                "full_name": "测试用户"
            }
            
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/register",
                    json=register_data
                )
                if response.status_code == 200:
                    print("✅ 用户注册成功")
                else:
                    print(f"⚠️ 用户注册失败: {response.text}")
            except Exception as e:
                print(f"❌ 注册请求失败: {e}")
            
            # 登录获取token
            login_data = {
                "username": register_data["username"],
                "password": register_data["password"]
            }
            
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/login",
                    data=login_data
                )
                if response.status_code == 200:
                    result = response.json()
                    self.access_token = result["data"]["access_token"]
                    print("✅ 用户登录成功，获取到访问令牌")
                    return True
                else:
                    print(f"❌ 登录失败: {response.text}")
                    return False
            except Exception as e:
                print(f"❌ 登录请求失败: {e}")
                return False
    
    async def test_ai_connection(self):
        """测试AI服务连接"""
        print("🤖 测试AI服务连接...")
        
        if not self.access_token:
            print("❌ 需要先登录获取访问令牌")
            return False
            
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/study-plans/test-gemini-sdk",
                    headers=headers
                )
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ AI服务连接成功: {result['message']}")
                    return True
                else:
                    print(f"❌ AI服务连接失败: {response.text}")
                    return False
            except Exception as e:
                print(f"❌ AI服务测试请求失败: {e}")
                return False
    
    async def test_generate_study_plan(self):
        """测试AI学习计划生成"""
        print("📚 测试AI学习计划生成...")
        
        if not self.access_token:
            print("❌ 需要先登录获取访问令牌")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        plan_request = {
            "subject": "Python数据科学",
            "time_frame": "4周",
            "learning_goals": [
                "掌握NumPy和Pandas基础",
                "学会数据可视化",
                "了解机器学习基础概念"
            ],
            "current_level": "beginner",
            "study_hours_per_week": 10
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                start_time = time.time()
                response = await client.post(
                    f"{self.base_url}/api/v1/study-plans/generate",
                    headers=headers,
                    json=plan_request
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    result = response.json()
                    plan_data = result["data"]
                    
                    print(f"✅ AI学习计划生成成功 (耗时: {end_time - start_time:.2f}秒)")
                    print(f"📋 计划标题: {plan_data['plan_title']}")
                    print(f"📝 计划概述: {plan_data['overview'][:100]}...")
                    print(f"📅 周计划数量: {len(plan_data['weekly_schedule'])}")
                    print(f"🎯 里程碑数量: {len(plan_data['milestones'])}")
                    print(f"📚 资源数量: {len(plan_data['resources'])}")
                    
                    if plan_data.get("saved_plan_id"):
                        self.saved_plan_id = plan_data["saved_plan_id"]
                        print(f"💾 已保存到数据库，计划ID: {self.saved_plan_id}")
                    
                    # 检查缓存
                    if "from cache" in result["message"]:
                        print("🚀 结果来自Redis缓存")
                    else:
                        print("🆕 结果为新生成")
                    
                    return True
                else:
                    print(f"❌ 学习计划生成失败: {response.text}")
                    return False
            except Exception as e:
                print(f"❌ 学习计划生成请求失败: {e}")
                return False
    
    async def test_get_study_plans_list(self):
        """测试获取学习计划列表"""
        print("📋 测试获取学习计划列表...")
        
        if not self.access_token:
            print("❌ 需要先登录获取访问令牌")
            return False
            
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/study-plans/list",
                    headers=headers
                )
                if response.status_code == 200:
                    result = response.json()
                    plans = result["data"]
                    print(f"✅ 获取学习计划列表成功，共 {len(plans)} 个计划")
                    
                    # 检查AI生成标识
                    ai_generated_count = sum(1 for plan in plans if plan.get("is_ai_generated"))
                    print(f"🤖 其中AI生成的计划: {ai_generated_count} 个")
                    
                    return True
                else:
                    print(f"❌ 获取学习计划列表失败: {response.text}")
                    return False
            except Exception as e:
                print(f"❌ 获取学习计划列表请求失败: {e}")
                return False
    
    async def test_get_specific_plan(self):
        """测试获取特定学习计划详情"""
        if not self.saved_plan_id:
            print("⚠️ 跳过特定计划详情测试（没有保存的计划ID）")
            return True
            
        print(f"📖 测试获取计划详情 (ID: {self.saved_plan_id})...")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/study-plans/{self.saved_plan_id}",
                    headers=headers
                )
                if response.status_code == 200:
                    result = response.json()
                    plan = result["data"]
                    print(f"✅ 获取计划详情成功")
                    print(f"📋 标题: {plan['title']}")
                    print(f"🤖 AI生成: {plan.get('is_ai_generated', False)}")
                    print(f"📚 科目: {plan.get('subject', 'N/A')}")
                    print(f"📊 难度: {plan.get('difficulty_level', 'N/A')}")
                    return True
                else:
                    print(f"❌ 获取计划详情失败: {response.text}")
                    return False
            except Exception as e:
                print(f"❌ 获取计划详情请求失败: {e}")
                return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始学习计划生成模块API测试")
        print("=" * 50)
        
        test_results = []
        
        # 测试用户认证
        result = await self.test_user_registration_and_login()
        test_results.append(("用户认证", result))
        
        if result:
            # 测试AI连接
            result = await self.test_ai_connection()
            test_results.append(("AI服务连接", result))
            
            # 测试学习计划生成
            result = await self.test_generate_study_plan()
            test_results.append(("AI学习计划生成", result))
            
            # 测试计划列表查询
            result = await self.test_get_study_plans_list()
            test_results.append(("学习计划列表查询", result))
            
            # 测试特定计划查询
            result = await self.test_get_specific_plan()
            test_results.append(("特定计划详情查询", result))
        
        # 输出测试结果
        print("\n" + "=" * 50)
        print("📊 测试结果汇总:")
        for test_name, success in test_results:
            status = "✅ 通过" if success else "❌ 失败"
            print(f"  {test_name}: {status}")
        
        success_count = sum(1 for _, success in test_results if success)
        total_count = len(test_results)
        print(f"\n🎯 总体结果: {success_count}/{total_count} 项测试通过")
        
        if success_count == total_count:
            print("🎉 所有测试通过！学习计划生成模块功能正常")
        else:
            print("⚠️ 部分测试失败，请检查相关功能")


async def main():
    """主函数"""
    tester = StudyPlanAPITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())