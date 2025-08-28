import logging
import re
import time
from typing import List, Optional, Tuple
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from .state import read_last_tweet_id, write_last_tweet_id
from .proxy_config import get_proxy_config

# 浏览器User-Agent，避免被屏蔽
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

class TwitterMonitor:
    """Twitter/X监控器，用于监控指定用户的推文"""
    
    def __init__(self, username: str, nitter_instance: str = "https://nitter.net"):
        """
        初始化Twitter监控器
        
        Args:
            username: 要监控的Twitter用户名（不包含@符号）
            nitter_instance: Nitter实例URL，默认为nitter.net
        """
        self.username = username
        self.nitter_instance = nitter_instance.rstrip('/')
        self.logger = logging.getLogger(__name__)
    
    def fetch_latest_ids(self, timeout: int = 30) -> List[str]:
        """
        获取最新的推文ID列表
        
        Args:
            timeout: 请求超时时间（秒）
            
        Returns:
            推文ID列表，按时间倒序排列（最新的在前）
        """
        url = f"{self.nitter_instance}/{self.username}"
        tweet_ids = []
        
        try:
            # 获取代理配置
            proxies = get_proxy_config()
            if proxies:
                logging.debug("Using proxies: %s", proxies)
            
            # 发送请求
            response = requests.get(
                url, 
                headers={"User-Agent": USER_AGENT},
                timeout=timeout,
                proxies=proxies
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找推文元素
            tweets = soup.find_all('div', class_='timeline-item')
            
            for tweet in tweets:
                # 查找推文链接
                link = tweet.find('a', href=re.compile(r'/status/'))
                if link and link.get('href'):
                    # 从链接中提取推文ID
                    match = re.search(r'/status/(\d+)', link['href'])
                    if match:
                        tweet_ids.append(match.group(1))
            
            self.logger.info(f"成功获取 {len(tweet_ids)} 条推文ID")
            return tweet_ids
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求失败: {e}")
            return []
        except Exception as e:
            self.logger.error(f"解析推文ID时出错: {e}")
            return []
    
    def get_new_tweets(self, since_id: Optional[str] = None) -> List[str]:
        """
        获取新的推文ID
        
        Args:
            since_id: 从这个ID之后的推文开始获取，如果为None则获取所有推文
            
        Returns:
            新的推文ID列表
        """
        all_tweets = self.fetch_latest_ids()
        
        if not all_tweets:
            return []
        
        if since_id is None:
            return all_tweets
        
        new_tweets = []
        for tweet_id in all_tweets:
            if tweet_id == since_id:
                break
            new_tweets.append(tweet_id)
        
        return new_tweets
    
    def monitor_once(self) -> List[str]:
        """
        执行一次监控检查
        
        Returns:
            新发现的推文ID列表
        """
        last_id = read_last_tweet_id(self.username)
        new_tweets = self.get_new_tweets(last_id)
        
        if new_tweets:
            # 更新最后一条推文ID
            write_last_tweet_id(self.username, new_tweets[0])
            self.logger.info(f"发现 {len(new_tweets)} 条新推文")
        else:
            self.logger.debug("没有发现新推文")
        
        return new_tweets

    def get_tweet_url(self, tweet_id: str) -> str:
        """获取推文URL"""
        return f"https://twitter.com/{self.username}/status/{tweet_id}"