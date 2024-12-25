import httpx
from xml.etree.ElementTree import XML
import logging
from typing import Dict

logger = logging.getLogger("QRZClient")

# https://www.qrz.com/page/current_spec.html

API_BASE = "https://xmldata.qrz.com/xml/current"
MAX_CALLSIGN_LEN = 10
XMLNS = {
    'qrz': 'http://xmldata.qrz.com'
}

class QrzClient:
    def __init__(self, username: str, password: str, agent: str):
        self._username = username
        self._password = password
        self._agent = agent
        
        self._client = httpx.AsyncClient()
        
        self._token = None
        
    def compose_agent(progname: str, version: str):
        return f"{progname.upper()}v{version}"
    
    async def _renew_token(self):
        res = await self._client.get(f"{API_BASE}?username={self._username}&password={self._password}&agent={self._agent}")
        
        root = XML(res.text)
        
        session = root.find('qrz:Session', XMLNS)
        
        if session is None:
            logger.error('API did not return a session object')
            return None
        
        key = session.find('qrz:Key', XMLNS)
        msg = session.find('qrz:Message', XMLNS)
        err = session.find('qrz:Error', XMLNS)
        
        if key is None:
            logger.error("Received error obtaining session key. More info likely to follow.")
            
            if err is not None:
                logger.error(f"QRZ Returned Error: {err.text}")
            
            if msg is not None:
                logger.error(f"QRZ Returned Error: {msg.text}")
        
            return None
    
        self._token = key.text

        return key.text
    
    async def _lookup_callsign(self, callsign: str) -> str | Dict[str, str]:
        if len(callsign) > MAX_CALLSIGN_LEN or not callsign.isalnum():
            return 'ENOENT' # this isn't a valid callsign, so don't waste our effort
        
        if self._token is None: # we need to renew the token
            return 'EAGAIN'
            
        res = await self._client.get(f"{API_BASE}?s={self._token}&callsign={callsign}")

        root = XML(res.text)
        
        session = root.find('qrz:Session', XMLNS)
        
        if session is None:
            logger.error("API did not return a session object. Something is very broken.")
            return 'EIO'
        
        err = session.find('qrz:Error', XMLNS)
        
        if err is not None:
            if 'not found'.casefold() in err.text.casefold():
                return 'ENOENT'
            
            if err.text.casefold() == 'connection refused'.casefold():
                logger.error("API returned connection refusal. Login will not be possible for at least 24 hours.")
                return 'ECONNREFUSED'
        
            if 'session timeout'.casefold() in err.text.casefold():
                self._token = None
                return 'EAGAIN'
        
            return 'EAGAIN'
        
        callobj = root.find('qrz:Callsign', XMLNS)
        
        if callobj is None:
            logger.error("API did not return a callsign object, but did not return an error.")
            return 'ENOENT' # This is probably a goofy not found error
        
        license_dict = {}
        
        for child in callobj:
            license_dict[child.tag.split('}')[-1]] = child.text
        
        return license_dict

    async def lookup_callsign(self, callsign: str) -> str | Dict[str, str] | None:
        result = await self._lookup_callsign(callsign)
        
        if isinstance(result, dict):
            return result
        
        if result == 'EAGAIN':
            if await self._renew_token() is None:
                return "API Failure"
        
            result = await self._lookup_callsign(callsign)

            if isinstance(result, dict):
                return result
            
        if result == 'ENOENT':
            return None

        if result == 'ECONNREFUSED':
            return "API Critical Failure. Service will be unavailable until future notice."
        
        if result == 'EIO':
            return "API Failure"
        
        return "Unknown internal error"
        
        