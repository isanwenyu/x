#!/usr/bin/env python3
"""
测试脚本 - 用于验证X Tweet Monitor服务各项功能
"""

import os
import sys
import json
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from x.config import Config
from x.twitter_monitor import TwitterMonitor
from x.xtracker_client import XTrackerClient
from x.dingtalk import DingTalkClient
from x.logging_config import get_logger


class ServiceTester:
    """服务测试类"""
    
    def __init__(self):
        self.config = Config()
        self.logger = get_logger(__name__)
        
        # 初始化各个组件
        self.twitter_monitor = TwitterMonitor(
            nitter_instances=self.config.NITTER_INSTANCES,
            request_timeout=10,  # 测试时使用较短超时
            max_retries=2
        )
        
        self.xtracker_client = XTrackerClient(
            base_url=self.config.XTRACKER_API_URL,
            timeout=10,
            max_retries=2
        )
        
        self.dingtalk_client = DingTalkClient(
            access_token=self.config.DINGTALK_ACCESS_TOKEN,
            secret=self.config.DINGTALK_SECRET,
            timeout=10
        )
    
    def test_config(self):
        """测试配置"""
        print("🔧 测试配置...")
        
        print(f"✓ Twitter用户: {self.config.TWITTER_USERS}")
        print(f"✓ Nitter实例: {len(self.config.NITTER_INSTANCES)}个")
        print(f"✓ 检查间隔: {self.config.CHECK_INTERVAL}分钟")
        print(f"✓ 请求超时: {self.config.REQUEST_TIMEOUT}秒")
        
        # 检查必要的环境变量
        missing_vars = []
        if not self.config.DINGTALK_ACCESS_TOKEN:
            missing_vars.append("DINGTALK_ACCESS_TOKEN")
        if not self.config.DINGTALK_SECRET:
            missing_vars.append("DINGTALK_SECRET")
        
        if missing_vars:
            print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
            return False
        else:
            print("✅ 所有必要环境变量已配置")
            return True
    
    def test_twitter_monitor(self):
        """测试Twitter监控"""
        print("\n🐦 测试Twitter监控...")
        
        test_user = "elonmusk"
        
        try:
            tweets = self.twitter_monitor.get_latest_tweets(test_user, limit=3)
            
            if tweets:
                print(f"✅ 成功获取 {len(tweets)} 条推文")
                for i, tweet in enumerate(tweets[:2], 1):
                    print(f"  {i}. {tweet.get('content', '')[:100]}...")
                return True
            else:
                print("❌ 无法获取推文")
                return False
                
        except Exception as e:
            print(f"❌ Twitter监控测试失败: {e}")
            return False
    
    def test_xtracker_client(self):
        """测试XTracker客户端"""
        print("\n📊 测试XTracker客户端...")
        
        if not self.config.XTRACKER_API_URL:
            print("⚠️  XTracker API未配置，跳过测试")
            return True
        
        test_user = "elonmusk"
        
        try:
            success, message = self.xtracker_client.test_connection()
            print(f"{'✅' if success else '❌'} {message}")
            
            if success:
                stats = self.xtracker_client.get_user_stats(test_user)
                if stats:
                    print(f"✅ 成功获取 {test_user} 的统计数据:")
                    print(f"   关注者: {stats['followers']:,}")
                    print(f"   正在关注: {stats['following']:,}")
                    print(f"   推文数: {stats['tweets']:,}")
                    return True
                else:
                    print("❌ 无法获取用户统计数据")
                    return False
            
            return success
            
        except Exception as e:
            print(f"❌ XTracker客户端测试失败: {e}")
            return False
    
    def test_dingtalk_client(self):
        """测试钉钉客户端"""
        print("\n📱 测试钉钉客户端...")
        
        try:
            # 发送测试消息
            test_message = f"🧪 **测试消息**\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n这是来自X Tweet Monitor服务的测试消息。"
            
            self.dingtalk_client.send_text_message(test_message)
            print("✅ 测试消息已发送到钉钉")
            return True
            
        except Exception as e:
            print(f"❌ 钉钉客户端测试失败: {e}")
            return False
    
    def test_all(self):
        """运行所有测试"""
        print("🚀 开始测试X Tweet Monitor服务...")
        print("=" * 50)
        
        results = {}
        
        # 测试配置
        results['config'] = self.test_config()
        
        # 测试Twitter监控
        results['twitter'] = self.test_twitter_monitor()
        
        # 测试XTracker客户端
        results['xtracker'] = self.test_xtracker_client()
        
        # 测试钉钉客户端
        results['dingtalk'] = self.test_dingtalk_client()
        
        # 总结
        print("\n" + "=" * 50)
        print("📋 测试结果总结:")
        
        for test_name, passed in results.items():
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"{test_name.upper()}: {status}")
        
        passed_count = sum(results.values())
        total_count = len(results)
        
        print(f"\n总计: {passed_count}/{total_count} 测试通过")
        
        if passed_count == total_count:
            print("🎉 所有测试通过！服务可以正常运行")
        else:
            print("⚠️  部分测试失败，请检查配置和网络连接")
        
        return results
    
    def test_environment(self):
        """测试环境配置"""
        print("\n🌍 测试环境配置...")
        
        print(f"Python版本: {sys.version}")
        print(f"工作目录: {os.getcwd()}")
        
        # 检查文件存在
        files_to_check = [
            '.env.example',
            'requirements.txt',
            'main.py',
            'Dockerfile',
            'docker-compose.yml'
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                print(f"✅ {file_path} 存在")
            else:
                print(f"❌ {file_path} 不存在")
        
        # 检查Python包
        try:
            import requests
            import schedule
            print("✅ 所有依赖包已安装")
        except ImportError as e:
            print(f"❌ 缺少依赖包: {e}")


def main():
    """主测试函数"""
    tester = ServiceTester()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "config":
            tester.test_config()
        elif command == "twitter":
            tester.test_twitter_monitor()
        elif command == "xtracker":
            tester.test_xtracker_client()
        elif command == "dingtalk":
            tester.test_dingtalk_client()
        elif command == "env":
            tester.test_environment()
        else:
            print("可用命令: config, twitter, xtracker, dingtalk, env")
    else:
        # 运行所有测试
        tester.test_all()


if __name__ == "__main__":
    main()