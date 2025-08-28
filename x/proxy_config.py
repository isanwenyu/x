"""代理配置工具"""
import os
from typing import Optional, Dict


def get_proxy_config() -> Optional[Dict[str, str]]:
    """获取代理配置
    
    Returns:
        代理配置字典或None（如果没有配置代理）
    """
    proxies = {}
    
    # 支持多种环境变量名格式
    http_proxy = (
        os.getenv('HTTP_PROXY') or 
        os.getenv('http_proxy') or
        os.getenv('PROXY_HTTP')
    )
    
    https_proxy = (
        os.getenv('HTTPS_PROXY') or 
        os.getenv('https_proxy') or
        os.getenv('PROXY_HTTPS') or
        http_proxy  # 如果没有HTTPS代理，使用HTTP代理
    )
    
    if http_proxy:
        proxies['http'] = http_proxy
    if https_proxy:
        proxies['https'] = https_proxy
    
    return proxies if proxies else None


def configure_requests_session(session, proxies: Optional[Dict[str, str]] = None):
    """配置requests会话的代理
    
    Args:
        session: requests.Session对象
        proxies: 代理配置字典，如果为None则自动获取
    """
    if proxies is None:
        proxies = get_proxy_config()
    
    if proxies:
        session.proxies.update(proxies)
        import logging
        logging.getLogger(__name__).debug("Configured proxies: %s", proxies)