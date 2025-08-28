"""
XTracker API client for fetching Twitter/X account statistics
"""

import requests
import json
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from .logging_config import get_logger


class XTrackerClient:
    """Client for fetching Twitter/X statistics from XTracker API"""
    
    def __init__(self, base_url: str, timeout: int = 30, max_retries: int = 3):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = get_logger(__name__)
    
    def _make_request(self, username: str) -> Optional[Dict[str, Any]]:
        """Make HTTP request to XTracker API with retry logic"""
        url = f"{self.base_url}&username={username}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Fetching XTracker data for {username} (attempt {attempt + 1})")
                
                response = requests.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, list) and len(data) > 0:
                    return data[0]  # Take first item if it's a list
                elif isinstance(data, dict):
                    return data
                else:
                    self.logger.warning(f"Unexpected response format: {type(data)}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"All retry attempts failed for {username}")
                    return None
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON decode error: {e}")
                return None
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                return None
    
    def get_user_stats(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user statistics from XTracker
        
        Args:
            username (str): Twitter/X username
            
        Returns:
            Optional[Dict[str, Any]]: User statistics or None if failed
        """
        data = self._make_request(username)
        if not data:
            return None
        
        try:
            # Parse the response data
            stats = {
                'username': username,
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'raw_data': data  # Store raw data for debugging
            }
            
            # Extract basic stats
            if 'followersCount' in data:
                stats['followers'] = int(data['followersCount'])
            elif 'followers' in data:
                stats['followers'] = int(data['followers'])
            elif 'stats' in data and 'followers' in data['stats']:
                stats['followers'] = int(data['stats']['followers'])
            else:
                stats['followers'] = 0
            
            if 'followingCount' in data:
                stats['following'] = int(data['followingCount'])
            elif 'following' in data:
                stats['following'] = int(data['following'])
            elif 'stats' in data and 'following' in data['stats']:
                stats['following'] = int(data['stats']['following'])
            else:
                stats['following'] = 0
            
            if 'tweetsCount' in data:
                stats['tweets'] = int(data['tweetsCount'])
            elif 'tweets' in data:
                stats['tweets'] = int(data['tweets'])
            elif 'stats' in data and 'tweets' in data['stats']:
                stats['tweets'] = int(data['stats']['tweets'])
            else:
                stats['tweets'] = 0
            
            # Extract additional stats if available
            if 'verified' in data:
                stats['verified'] = bool(data['verified'])
            
            if 'description' in data:
                stats['description'] = str(data['description'])
            
            if 'profileImageUrl' in data:
                stats['profile_image_url'] = str(data['profileImageUrl'])
            
            # Extract growth metrics if available
            if 'growth' in data:
                growth = data['growth']
                if isinstance(growth, dict):
                    stats['followers_growth_24h'] = int(growth.get('followers_24h', 0))
                    stats['followers_growth_7d'] = int(growth.get('followers_7d', 0))
                    stats['followers_growth_30d'] = int(growth.get('followers_30d', 0))
            
            # Calculate derived metrics
            stats['following_to_followers_ratio'] = (
                stats['following'] / max(stats['followers'], 1)
            )
            
            self.logger.info(f"Successfully fetched stats for {username}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error parsing XTracker data: {e}")
            return None
    
    def get_daily_summary(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get daily summary of user statistics
        
        Args:
            username (str): Twitter/X username
            
        Returns:
            Optional[Dict[str, Any]]: Daily summary or None if failed
        """
        stats = self.get_user_stats(username)
        if not stats:
            return None
        
        summary = {
            'username': username,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'followers': stats['followers'],
            'following': stats['following'],
            'tweets': stats['tweets'],
            'verified': stats.get('verified', False),
            'description': stats.get('description', ''),
            'profile_image_url': stats.get('profile_image_url', ''),
            'growth_24h': stats.get('followers_growth_24h', 0),
            'growth_7d': stats.get('followers_growth_7d', 0),
            'growth_30d': stats.get('followers_growth_30d', 0),
            'following_ratio': round(stats['following_to_followers_ratio'], 2)
        }
        
        return summary
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to XTracker API
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Test with a known username
            test_username = "elonmusk"
            stats = self.get_user_stats(test_username)
            
            if stats and 'followers' in stats:
                return True, f"XTracker API connection successful. Found {stats['followers']:,} followers for {test_username}"
            else:
                return False, "Failed to fetch data from XTracker API"
                
        except Exception as e:
            return False, f"XTracker API connection error: {str(e)}"


def test_xtracker():
    """Test function for XTracker client"""
    import os
    
    # Use test configuration
    base_url = "https://www.xtracker.io/api/users?stats=true&platform=X"
    username = "elonmusk"
    
    client = XTrackerClient(base_url)
    
    print("Testing XTracker client...")
    
    # Test connection
    success, message = client.test_connection()
    print(f"Connection test: {'✓' if success else '✗'} - {message}")
    
    if success:
        print(f"\nFetching stats for {username}...")
        stats = client.get_user_stats(username)
        
        if stats:
            print("User Statistics:")
            print(f"  Followers: {stats['followers']:,}")
            print(f"  Following: {stats['following']:,}")
            print(f"  Tweets: {stats['tweets']:,}")
            
            if 'verified' in stats:
                print(f"  Verified: {'✓' if stats['verified'] else '✗'}")
            
            if 'followers_growth_24h' in stats:
                growth = stats['followers_growth_24h']
                emoji = "📈" if growth > 0 else "📉"
                print(f"  24h Growth: {emoji} {growth:,}")
        else:
            print("Failed to fetch user stats")


if __name__ == "__main__":
    test_xtracker()