"""
DingTalk notification module for sending messages to DingTalk groups
"""

import requests
import json
import time
from typing import Dict, Any, List, Optional
from .logging_config import get_logger


class DingTalkClient:
    """Client for sending messages to DingTalk via webhook"""
    
    def __init__(self, access_token: str, timeout: int = 30, max_retries: int = 3):
        self.access_token = access_token
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = get_logger(__name__)
        
        # DingTalk webhook URL
        self.webhook_url = f"https://oapi.dingtalk.com/robot/send?access_token={access_token}"
    
    def _send_request(self, payload: Dict[str, Any]) -> bool:
        """Send HTTP request to DingTalk webhook with retry logic"""
        headers = {
            'Content-Type': 'application/json',
            'Charset': 'utf-8'
        }
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Sending DingTalk message (attempt {attempt + 1})")
                
                response = requests.post(
                    self.webhook_url,
                    headers=headers,
                    data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                result = response.json()
                
                if result.get('errcode') == 0:
                    self.logger.info("DingTalk message sent successfully")
                    return True
                else:
                    self.logger.error(f"DingTalk API error: {result}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"HTTP error sending DingTalk message: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
            except Exception as e:
                self.logger.error(f"Unexpected error sending DingTalk message: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
        
        return False
    
    def send_text_message(self, content: str, at_mobiles: List[str] = None, is_at_all: bool = False) -> bool:
        """
        Send text message to DingTalk
        
        Args:
            content (str): Message content
            at_mobiles (List[str]): List of mobile numbers to @ mention
            is_at_all (bool): Whether to @ everyone
            
        Returns:
            bool: True if message sent successfully
        """
        payload = {
            "msgtype": "text",
            "text": {
                "content": content
            },
            "at": {
                "atMobiles": at_mobiles or [],
                "isAtAll": is_at_all
            }
        }
        
        return self._send_request(payload)
    
    def send_markdown_message(self, title: str, content: str, at_mobiles: List[str] = None, is_at_all: bool = False) -> bool:
        """
        Send markdown message to DingTalk
        
        Args:
            title (str): Message title
            content (str): Markdown content
            at_mobiles (List[str]): List of mobile numbers to @ mention
            is_at_all (bool): Whether to @ everyone
            
        Returns:
            bool: True if message sent successfully
        """
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": content
            },
            "at": {
                "atMobiles": at_mobiles or [],
                "isAtAll": is_at_all
            }
        }
        
        return self._send_request(payload)
    
    def send_link_message(self, title: str, text: str, message_url: str, pic_url: str = None) -> bool:
        """
        Send link message to DingTalk
        
        Args:
            title (str): Message title
            text (str): Message description
            message_url (str): URL to link to
            pic_url (str): URL of image to display
            
        Returns:
            bool: True if message sent successfully
        """
        payload = {
            "msgtype": "link",
            "link": {
                "text": text,
                "title": title,
                "picUrl": pic_url or "",
                "messageUrl": message_url
            }
        }
        
        return self._send_request(payload)
    
    def send_action_card_message(self, title: str, text: str, btns: List[Dict[str, str]], btn_orientation: str = "0") -> bool:
        """
        Send action card message to DingTalk
        
        Args:
            title (str): Message title
            text (str): Message content
            btns (List[Dict[str, str]]): List of buttons with title and actionURL
            btn_orientation (str): Button orientation (0: vertical, 1: horizontal)
            
        Returns:
            bool: True if message sent successfully
        """
        payload = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": title,
                "text": text,
                "btnOrientation": btn_orientation,
                "btns": btns
            }
        }
        
        return self._send_request(payload)
    
    def send_feed_card_message(self, links: List[Dict[str, str]]) -> bool:
        """
        Send feed card message to DingTalk
        
        Args:
            links (List[Dict[str, str]]): List of links with title, messageURL, picURL
            
        Returns:
            bool: True if message sent successfully
        """
        payload = {
            "msgtype": "feedCard",
            "feedCard": {
                "links": links
            }
        }
        
        return self._send_request(payload)
    
    def send_tweet_notification(self, tweet_data: Dict[str, Any], include_stats: bool = True) -> bool:
        """
        Send formatted tweet notification to DingTalk
        
        Args:
            tweet_data (Dict[str, Any]): Tweet data including content, stats, etc.
            include_stats (bool): Whether to include XTracker stats
            
        Returns:
            bool: True if message sent successfully
        """
        tweet = tweet_data.get('tweet', {})
        stats = tweet_data.get('stats', {})
        
        # Build markdown content
        content_parts = []
        
        # Header
        content_parts.append(f"## 🐦 新推文通知")
        content_parts.append(f"**用户**: @{tweet.get('username', 'Unknown')}")
        content_parts.append(f"**时间**: {tweet.get('timestamp', 'Unknown')}")
        
        # Tweet content
        content_parts.append(f"**内容**: {tweet.get('content', 'No content')}")
        
        # Tweet URL
        tweet_url = tweet.get('url', '')
        if tweet_url:
            content_parts.append(f"**链接**: [查看推文]({tweet_url})")
        
        # Media URLs
        media_urls = tweet.get('media_urls', [])
        if media_urls:
            content_parts.append("**媒体**:")
            for i, media_url in enumerate(media_urls[:3], 1):
                content_parts.append(f"  {i}. [媒体链接]({media_url})")
        
        # XTracker stats
        if include_stats and stats:
            content_parts.append("\n---")
            content_parts.append("### 📊 XTracker 统计")
            content_parts.append(f"**关注者**: {stats.get('followers', 'N/A'):,}")
            content_parts.append(f"**关注中**: {stats.get('following', 'N/A'):,}")
            content_parts.append(f"**推文数**: {stats.get('tweets', 'N/A'):,}")
            
            # Calculate growth
            if stats.get('followers_growth_24h') is not None:
                growth = stats['followers_growth_24h']
                emoji = "📈" if growth > 0 else "📉"
                content_parts.append(f"**24小时增长**: {emoji} {growth:,}")
        
        # Footer
        content_parts.append("\n---")
        content_parts.append(f"*通过 X Tweet Monitor 发送*")
        
        markdown_content = "\n\n".join(content_parts)
        
        return self.send_markdown_message(
            title=f"@{tweet.get('username', 'Unknown')} 的新推文",
            content=markdown_content
        )
    
    def send_stats_update(self, username: str, stats: Dict[str, Any]) -> bool:
        """
        Send XTracker stats update to DingTalk
        
        Args:
            username (str): Twitter username
            stats (Dict[str, Any]): Stats data from XTracker
            
        Returns:
            bool: True if message sent successfully
        """
        content_parts = []
        
        content_parts.append(f"## 📊 @{username} 每日统计")
        content_parts.append(f"**更新时间**: {stats.get('updated_at', 'Unknown')}")
        
        # Main stats
        content_parts.append(f"**关注者**: {stats.get('followers', 'N/A'):,}")
        content_parts.append(f"**关注中**: {stats.get('following', 'N/A'):,}")
        content_parts.append(f"**推文数**: {stats.get('tweets', 'N/A'):,}")
        
        # Growth metrics
        if stats.get('followers_growth_24h') is not None:
            growth = stats['followers_growth_24h']
            emoji = "📈" if growth > 0 else "📉"
            content_parts.append(f"**24小时增长**: {emoji} {growth:,}")
        
        if stats.get('followers_growth_7d') is not None:
            growth_7d = stats['followers_growth_7d']
            emoji = "📈" if growth_7d > 0 else "📉"
            content_parts.append(f"**7天增长**: {emoji} {growth_7d:,}")
        
        # Profile URL
        profile_url = f"https://twitter.com/{username}"
        content_parts.append(f"**个人主页**: [查看@{username}]({profile_url})")
        
        content_parts.append("\n---")
        content_parts.append("*通过 X Tweet Monitor 发送*")
        
        markdown_content = "\n\n".join(content_parts)
        
        return self.send_markdown_message(
            title=f"@{username} 每日统计更新",
            content=markdown_content
        )
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to DingTalk webhook
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Send a simple test message
            test_message = "🔧 X Tweet Monitor 连接测试"
            success = self.send_text_message(test_message)
            
            if success:
                return True, "DingTalk connection successful"
            else:
                return False, "Failed to send test message to DingTalk"
                
        except Exception as e:
            return False, f"DingTalk connection error: {str(e)}"


def test_dingtalk():
    """Test function for DingTalk client"""
    import os
    
    access_token = os.getenv('DINGTALK_ACCESS_TOKEN')
    if not access_token:
        print("Please set DINGTALK_ACCESS_TOKEN environment variable")
        return
    
    client = DingTalkClient(access_token)
    
    print("Testing DingTalk client...")
    
    # Test connection
    success, message = client.test_connection()
    print(f"Connection test: {'✓' if success else '✗'} - {message}")
    
    if success:
        print("\nSending test messages...")
        
        # Test text message
        client.send_text_message("🚀 Hello from X Tweet Monitor!")
        
        # Test markdown message
        markdown_content = """
## 📊 测试消息
**时间**: 当前时间
**状态**: ✅ 运行正常
**功能**: DingTalk通知测试
"""
        client.send_markdown_message("测试消息", markdown_content)
        
        print("Test messages sent!")


if __name__ == "__main__":
    test_dingtalk()