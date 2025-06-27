"""HTTP adapter to support both httpx and aiohttp clients."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
import json

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

import httpx


class HTTPAdapter(ABC):
    """Abstract base class for HTTP adapters."""
    
    @abstractmethod
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        pass
    
    @abstractmethod
    async def post(self, url: str, json_data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make a POST request with JSON data."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the session."""
        pass


class HTTPXAdapter(HTTPAdapter):
    """Adapter for httpx.AsyncClient."""
    
    def __init__(self, session: Optional[httpx.AsyncClient] = None, headers: Optional[Dict[str, str]] = None, timeout: float = 15.0):
        self.session = session
        self.headers = headers or {}
        self.timeout = timeout
        self._owns_session = session is None
        
    async def _ensure_session(self) -> httpx.AsyncClient:
        """Ensure we have a session."""
        if self.session is None:
            self.session = httpx.AsyncClient(headers=self.headers, timeout=self.timeout)
        return self.session
    
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        session = await self._ensure_session()
        response = await session.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def post(self, url: str, json_data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make a POST request with JSON data."""
        session = await self._ensure_session()
        response = await session.post(url, json=json_data, headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def close(self) -> None:
        """Close the session if we own it."""
        if self._owns_session and self.session:
            await self.session.aclose()
            self.session = None


if HAS_AIOHTTP:
    class AIOHTTPAdapter(HTTPAdapter):
        """Adapter for aiohttp.ClientSession."""
        
        def __init__(self, session: aiohttp.ClientSession, headers: Optional[Dict[str, str]] = None):
            self.session = session
            self.headers = headers or {}
            
        async def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
            """Make a GET request."""
            combined_headers = {**self.headers, **(headers or {})}
            async with self.session.get(url, headers=combined_headers) as response:
                response.raise_for_status()
                return await response.json()
        
        async def post(self, url: str, json_data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
            """Make a POST request with JSON data."""
            combined_headers = {**self.headers, **(headers or {})}
            async with self.session.post(url, json=json_data, headers=combined_headers) as response:
                response.raise_for_status()
                return await response.json()
        
        async def close(self) -> None:
            """aiohttp sessions are typically managed externally, so we don't close them."""
            pass


def create_adapter(session: Optional[Union[httpx.AsyncClient, 'aiohttp.ClientSession']] = None, 
                  headers: Optional[Dict[str, str]] = None,
                  timeout: float = 15.0) -> HTTPAdapter:
    """Create an appropriate adapter based on the session type."""
    if session is None:
        # Default to httpx for backward compatibility
        return HTTPXAdapter(headers=headers, timeout=timeout)
    
    if isinstance(session, httpx.AsyncClient):
        return HTTPXAdapter(session=session, headers=headers, timeout=timeout)
    
    if HAS_AIOHTTP and hasattr(session, 'get') and hasattr(session, 'post'):
        # Duck typing for aiohttp.ClientSession
        return AIOHTTPAdapter(session=session, headers=headers)
    
    raise ValueError(f"Unsupported session type: {type(session)}")