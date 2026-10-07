from urllib.parse import quote
import httpx
from app.config import settings

class PanelError(RuntimeError):
    pass

class ThreeXUI:
    def __init__(self):
        self.base = settings.panel_base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {settings.panel_api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    async def _request(self, method: str, path: str, **kwargs):
        async with httpx.AsyncClient(timeout=30, verify=True, follow_redirects=True) as client:
            response = await client.request(method, self.base + path, headers=self.headers, **kwargs)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise PanelError(f'HTTP {response.status_code} from 3x-ui: {response.text[:500]}') from exc
            try:
                data = response.json()
            except ValueError as exc:
                raise PanelError('3x-ui returned non-JSON response') from exc
            if data.get('success') is False:
                raise PanelError(data.get('msg') or '3x-ui API error')
            return data

    async def get_client(self, email: str):
        return await self._request('GET', f'/panel/api/clients/get/{quote(email, safe="")}')

    async def add_client(self, *, email: str, inbound_id: int, total_bytes: int, expiry_ms: int, tg_id: int):
        body = {
            'client': {
                'email': email,
                'totalGB': total_bytes,
                'expiryTime': expiry_ms,
                'tgId': tg_id,
                'limitIp': 0,
                'limitHwid': 0,
                'enable': True,
            },
            'inboundIds': [inbound_id],
        }
        await self._request('POST', '/panel/api/clients/add', json=body)
        return await self.get_client(email)

    async def update_client(self, email: str, **fields):
        return await self._request('POST', f'/panel/api/clients/update/{quote(email, safe="")}', json=fields)

    async def traffic(self, email: str):
        return await self._request('GET', f'/panel/api/clients/traffic/{quote(email, safe="")}')

    async def links(self, email: str):
        data = await self._request('GET', f'/panel/api/clients/links/{quote(email, safe="")}')
        return data.get('obj') or []

    async def links_by_subid(self, sub_id: str):
        data = await self._request('GET', f'/panel/api/clients/subLinks/{quote(sub_id, safe="")}')
        return data.get('obj') or []

    async def delete_client(self, email: str):
        return await self._request('POST', f'/panel/api/clients/del/{quote(email, safe="")}')
