"""
Twitter/X tweet monitoring module using Nitter mirrors
"""

import requests
import time
import re
import logging
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import random

from .logging_config import get_logger


class Tweet:
    """Represents a Twitter/X tweet"""
    
    def __init__(self, tweet_id: str, username: str, content: str, 
                 timestamp: str, url: str, media_urls: List[str] = None):
        self.tweet_id = tweet_id
        self.username = username
        self.content = content
        self.timestamp = timestamp
        self.url = url
        self.media_urls = media_urls or []
    
    def __repr__(self):
        return f"Tweet(id={self.tweet_id}, user={self.username}, content={self.content[:50]}...)"
    
    def to_dict(self) -> Dict:
        """Convert tweet to dictionary"""
        return {
            'tweet_id': self.tweet_id,
            'username': self.username,
            'content': self.content,
            'timestamp': self.timestamp,
            'url': self.url,
            'media_urls': self.media_urls
        }


class TwitterMonitor:
    """Monitor Twitter/X tweets using Nitter mirrors"""
    
    def __init__(self, username: str, nitter_urls: List[str], 
                 request_timeout: int = 30, max_retries: int = 3, retry_delay: int = 5):
        self.username = username
        self.nitter_urls = nitter_urls
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = get_logger(__name__)
        
    def _get_session(self) -> requests.Session:
        """Create a requests session with proper headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        return session
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        session = self._get_session()
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Attempting request to {url} (attempt {attempt + 1})")
                response = session.get(url, timeout=self.request_timeout)
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    self.logger.error(f"All retry attempts failed for {url}")
                    return None
    
    def _parse_tweet(self, tweet_element, base_url: str) -> Optional[Tweet]:
        """Parse a tweet element into Tweet object"""
        try:
            # Extract tweet ID from URL
            tweet_link = tweet_element.find('a', href=re.compile(r'/status/'))
            if not tweet_link:
                return None
            
            tweet_url = urljoin(base_url, tweet_link['href'])
            tweet_id = tweet_url.split('/')[-1]
            
            # Extract content
            content_div = tweet_element.find('div', class_='tweet-content')
            if not content_div:
                return None
            
            content = content_div.get_text(strip=True)
            
            # Extract timestamp
            time_element = tweet_element.find('time')
            if time_element and time_element.get('datetime'):
                timestamp = time_element['datetime']
            else:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Extract media URLs
            media_urls = []
            media_elements = tweet_element.find_all('div', class_='tweet-media')
            for media in media_elements:
                img_tags = media.find_all('img')
                for img in img_tags:
                    if img.get('src'):
                        media_urls.append(urljoin(base_url, img['src']))
            
            return Tweet(
                tweet_id=tweet_id,
                username=self.username,
                content=content,
                timestamp=timestamp,
                url=tweet_url,
                media_urls=media_urls
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing tweet: {e}")
            return None
    
    def _get_tweets_from_nitter(self, nitter_url: str, max_tweets: int = 10) -> List[Tweet]:
        """Get tweets from a specific Nitter instance"""
        # Construct URL for user timeline
        user_url = f"{nitter_url.rstrip('/')}/{self.username}"
        
        response = self._make_request(user_url)
        if not response:
            return []
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find tweet containers
            tweet_elements = soup.find_all('div', class_='timeline-item')
            if not tweet_elements:
                # Try alternative selectors
                tweet_elements = soup.find_all('div', class_='tweet')
            
            tweets = []
            for tweet_element in tweet_elements[:max_tweets]:
                tweet = self._parse_tweet(tweet_element, nitter_url)
                if tweet:
                    tweets.append(tweet)
            
            self.logger.info(f"Found {len(tweets)} tweets from {nitter_url}")
            return tweets
            
        except Exception as e:
            self.logger.error(f"Error parsing tweets from {nitter_url}: {e}")
            return []
    
    def get_latest_tweets(self, max_tweets: int = 10) -> List[Tweet]:
        """Get latest tweets from available Nitter instances"""
        all_tweets = []
        
        # Shuffle Nitter URLs to distribute load
        urls = self.nitter_urls.copy()
        random.shuffle(urls)
        
        for nitter_url in urls:
            try:
                tweets = self._get_tweets_from_nitter(nitter_url, max_tweets)
                if tweets:
                    # Add source URL for debugging
                    for tweet in tweets:
                        tweet.nitter_source = nitter_url
                    
                    all_tweets.extend(tweets)
                    self.logger.info(f"Successfully retrieved tweets from {nitter_url}")
                    break  # Use first successful source
                    
            except Exception as e:
                self.logger.warning(f"Failed to get tweets from {nitter_url}: {e}")
                continue
        
        if not all_tweets:
            self.logger.error("Failed to retrieve tweets from all Nitter instances")
        
        # Remove duplicates based on tweet ID
        seen_ids = set()
        unique_tweets = []
        for tweet in all_tweets:
            if tweet.tweet_id not in seen_ids:
                seen_ids.add(tweet.tweet_id)
                unique_tweets.append(tweet)
        
        # Sort by tweet ID (newest first)
        unique_tweets.sort(key=lambda x: x.tweet_id, reverse=True)
        
        return unique_tweets[:max_tweets]
    
    def get_tweet_by_id(self, tweet_id: str) -> Optional[Tweet]:
        """Get a specific tweet by ID"""
        tweets = self.get_latest_tweets(max_tweets=50)
        for tweet in tweets:
            if tweet.tweet_id == tweet_id:
                return tweet
        return None
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test connection to Nitter instances"""
        working_urls = []
        
        for nitter_url in self.nitter_urls:
            try:
                test_url = f"{nitter_url.rstrip('/')}/{self.username}"
                response = self._make_request(test_url)
                if response and response.status_code == 200:
                    working_urls.append(nitter_url)
                    
            except Exception as e:
                self.logger.warning(f"Connection test failed for {nitter_url}: {e}")
                continue
        
        if working_urls:
            return True, f"Working Nitter URLs: {', '.join(working_urls)}"
        else:
            return False, "No working Nitter URLs found"


def test_twitter_monitor():
    """Test function for TwitterMonitor"""
    import os
    
    # Use test configuration
    username = "elonmusk"
    nitter_urls = [
        "https://nitter.poast.org",
        "https://nitter.privacydev.net",
        "https://nitter.cz"
    ]
    
    monitor = TwitterMonitor(username, nitter_urls)
    
    print("Testing Twitter Monitor...")
    
    # Test connection
    success, message = monitor.test_connection()
    print(f"Connection test: {'✓' if success else '✗'} - {message}")
    
    if success:
        print("\nFetching latest tweets...")
        tweets = monitor.get_latest_tweets(max_tweets=3)
        
        if tweets:
            print(f"Found {len(tweets)} tweets:")
            for tweet in tweets:
                print(f"- {tweet.tweet_id}: {tweet.content[:100]}...")
        else:
            print("No tweets found")


if __name__ == "__main__":
    test_twitter_monitor()