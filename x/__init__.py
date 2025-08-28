"""
X Tweet Monitor & XTracker Service

A Python service that monitors Twitter/X tweets for a specific user and pushes notifications to DingTalk.
"""

__version__ = "1.0.0"
__author__ = "Paul Zhu"
__email__ = "isanwenyu@163.com"
__description__ = "Twitter/X monitoring and DingTalk notification service"

from .config import load_settings
from .twitter_monitor import TwitterMonitor
from .dingtalk import DingTalkClient
from .xtracker_client import XTrackerClient

__all__ = [
    "load_settings",
    "TwitterMonitor", 
    "DingTalkClient",
    "XTrackerClient"
]