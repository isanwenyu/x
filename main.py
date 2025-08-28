#!/usr/bin/env python3
"""
X Tweet Monitor & XTracker Service
主程序入口文件
"""

import os
import sys
import time
import schedule
from datetime import datetime
from typing import List, Dict, Any

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from x.config import Config
from x.twitter_monitor import TwitterMonitor
from x.xtracker_client import XTrackerClient
from x.dingtalk import DingTalkClient
from x.logging_config import get_logger


class XMonitorService:
    """主监控服务类"""
    
    def __init__(self):
        self.config = Config()
        self.logger = get_logger(__name__)
        
        # 初始化各个组件
        self.twitter_monitor = TwitterMonitor(
            nitter_instances=self.config.NITTER_INSTANCES,
            request_timeout=self.config.REQUEST_TIMEOUT,
            max_retries=self.config.MAX_RETRIES
        )
        
        self.xtracker_client = XTrackerClient(
            base_url=self.config.XTRACKER_API_URL,
            timeout=self.config.REQUEST_TIMEOUT,
            max_retries=self.config.MAX_RETRIES
        )
        
        self.dingtalk_client = DingTalkClient(
            access_token=self.config.DINGTALK_ACCESS_TOKEN,
            secret=self.config.DINGTALK_SECRET,
            timeout=self.config.REQUEST_TIMEOUT
        )
        
        # 状态追踪
        self.last_tweet_ids = {}
        self.last_stats = {}
    
    def send_startup_notification(self):
        """发送服务启动通知"""
        message = f"""
🚀 **X Tweet Monitor 服务已启动**

- **启动时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **监控用户**: {', '.join(self.config.TWITTER_USERS)}
- **检查间隔**: 每{self.config.CHECK_INTERVAL}分钟
- **Nitter实例**: {len(self.config.NITTER_INSTANCES)}个
- **XTracker API**: {'启用' if self.config.XTRACKER_API_URL else '禁用'}

服务正在运行中...
        """
        
        self.dingtalk_client.send_text_message(message)
        self.logger.info("Startup notification sent")
    
    def monitor_tweets(self):
        """监控推文"""
        self.logger.info("开始检查新推文...")
        
        for username in self.config.TWITTER_USERS:
            try:
                tweets = self.twitter_monitor.get_latest_tweets(username, limit=5)
                
                if not tweets:
                    self.logger.warning(f"无法获取 {username} 的推文")
                    continue
                
                # 获取最新推文ID
                latest_tweet = tweets[0]
                current_tweet_id = latest_tweet.get('id')
                
                # 检查是否是新推文
                last_id = self.last_tweet_ids.get(username)
                if last_id and current_tweet_id == last_id:
                    self.logger.info(f"{username} 没有新推文")
                    continue
                
                # 更新最后推文ID
                self.last_tweet_ids[username] = current_tweet_id
                
                # 发送新推文通知
                self._send_tweet_notification(username, latest_tweet)
                
            except Exception as e:
                self.logger.error(f"监控 {username} 推文时出错: {e}")
    
    def _send_tweet_notification(self, username: str, tweet: Dict[str, Any]):
        """发送推文通知"""
        try:
            content = tweet.get('content', '')
            timestamp = tweet.get('timestamp', '')
            likes = tweet.get('likes', 0)
            retweets = tweet.get('retweets', 0)
            
            # 截断过长的内容
            if len(content) > 300:
                content = content[:300] + "..."
            
            message = f"""
📱 **{username} 发布新推文**

{content}

🔗 [查看推文](https://twitter.com/{username}/status/{tweet.get('id', '')})

📊 **互动数据**:
- 👍 点赞: {likes:,}
- 🔄 转发: {retweets:,}
- 🕐 时间: {timestamp}
            """
            
            self.dingtalk_client.send_tweet_notification(username, tweet)
            self.logger.info(f"已发送 {username} 的新推文通知")
            
        except Exception as e:
            self.logger.error(f"发送推文通知时出错: {e}")
    
    def monitor_xtracker_stats(self):
        """监控XTracker统计数据"""
        if not self.config.XTRACKER_API_URL:
            return
            
        self.logger.info("开始检查XTracker统计数据...")
        
        for username in self.config.TWITTER_USERS:
            try:
                stats = self.xtracker_client.get_user_stats(username)
                
                if not stats:
                    self.logger.warning(f"无法获取 {username} 的XTracker数据")
                    continue
                
                # 检查是否有变化
                last_stats = self.last_stats.get(username, {})
                current_followers = stats.get('followers', 0)
                last_followers = last_stats.get('followers', 0)
                
                # 如果数据有变化，发送通知
                if current_followers != last_followers:
                    self._send_stats_update(username, stats, last_stats)
                    self.last_stats[username] = stats.copy()
                else:
                    self.logger.info(f"{username} 的统计数据没有变化")
                
            except Exception as e:
                self.logger.error(f"监控 {username} XTracker数据时出错: {e}")
    
    def _send_stats_update(self, username: str, current_stats: Dict, last_stats: Dict):
        """发送统计数据更新通知"""
        try:
            followers_change = current_stats.get('followers', 0) - last_stats.get('followers', 0)
            following_change = current_stats.get('following', 0) - last_stats.get('following', 0)
            tweets_change = current_stats.get('tweets', 0) - last_stats.get('tweets', 0)
            
            self.dingtalk_client.send_xtracker_stats_update(username, current_stats, last_stats)
            self.logger.info(f"已发送 {username} 的XTracker数据更新通知")
            
        except Exception as e:
            self.logger.error(f"发送统计数据更新通知时出错: {e}")
    
    def run_once(self):
        """运行一次完整检查"""
        self.logger.info("执行单次检查...")
        
        # 检查推文
        self.monitor_tweets()
        
        # 检查XTracker数据
        self.monitor_xtracker_stats()
        
        self.logger.info("单次检查完成")
    
    def run_schedule(self):
        """启动定时任务"""
        self.logger.info("启动定时监控服务...")
        
        # 发送启动通知
        self.send_startup_notification()
        
        # 设置定时任务
        schedule.every(self.config.CHECK_INTERVAL).minutes.do(self.monitor_tweets)
        
        if self.config.XTRACKER_API_URL:
            schedule.every(self.config.XTRACKER_STATS_INTERVAL).minutes.do(self.monitor_xtracker_stats)
        
        self.logger.info(f"已设置定时任务:")
        self.logger.info(f"- 推文检查: 每{self.config.CHECK_INTERVAL}分钟")
        if self.config.XTRACKER_API_URL:
            self.logger.info(f"- XTracker检查: 每{self.config.XTRACKER_STATS_INTERVAL}分钟")
        
        # 运行定时任务
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("接收到停止信号，正在关闭服务...")
            self.dingtalk_client.send_text_message("🛑 **X Tweet Monitor 服务已停止**")
    
    def health_check(self):
        """健康检查"""
        results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'healthy',
            'components': {}
        }
        
        # 检查Twitter监控
        try:
            tweets = self.twitter_monitor.get_latest_tweets('elonmusk', limit=1)
            results['components']['twitter_monitor'] = 'ok' if tweets else 'warning'
        except Exception as e:
            results['components']['twitter_monitor'] = f'error: {e}'
        
        # 检查XTracker
        if self.config.XTRACKER_API_URL:
            try:
                success, message = self.xtracker_client.test_connection()
                results['components']['xtracker'] = 'ok' if success else f'error: {message}'
            except Exception as e:
                results['components']['xtracker'] = f'error: {e}'
        else:
            results['components']['xtracker'] = 'disabled'
        
        # 检查DingTalk
        try:
            self.dingtalk_client.send_text_message("🔍 健康检查测试")
            results['components']['dingtalk'] = 'ok'
        except Exception as e:
            results['components']['dingtalk'] = f'error: {e}'
        
        # 设置总体状态
        if any('error' in str(v) for v in results['components'].values()):
            results['status'] = 'degraded'
        
        return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='X Tweet Monitor & XTracker Service')
    parser.add_argument('--once', action='store_true', help='运行一次检查')
    parser.add_argument('--health', action='store_true', help='健康检查')
    parser.add_argument('--test-dingtalk', action='store_true', help='测试钉钉通知')
    parser.add_argument('--test-xtracker', help='测试XTracker API (提供用户名)')
    
    args = parser.parse_args()
    
    # 初始化服务
    service = XMonitorService()
    
    if args.health:
        # 健康检查
        results = service.health_check()
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
    elif args.test_dingtalk:
        # 测试钉钉通知
        service.dingtalk_client.send_text_message("🧪 **钉钉通知测试成功！**")
        print("钉钉测试通知已发送")
        
    elif args.test_xtracker:
        # 测试XTracker API
        stats = service.xtracker_client.get_user_stats(args.test_xtracker)
        if stats:
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        else:
            print("获取XTracker数据失败")
            
    elif args.once:
        # 运行一次检查
        service.run_once()
        
    else:
        # 启动定时服务
        service.run_schedule()


if __name__ == "__main__":
    import json
    main()