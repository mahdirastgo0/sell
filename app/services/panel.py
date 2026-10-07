import httpx
from urllib.parse import quote
from app.config import settings

class PanelError(RuntimeError): pass

class ThreeXUI:
    def __init__(self):
        self.base=settings.panel_base_url.rstrip('/')
        self.headers={'Authorization': f'Bearer {settings.panel_api_token}', 'Content-Type':'application/json'}

    async def _request(self, method, path, **kwargs):
        async with httpx.AsyncClient(timeout=30, verify=True) as c:
            r=await c.request(method, self.base+path, headers=self.headers, **kwargs)
            r.raise_for_status()
            data=r.json()
            if data.get('success') is False:
                raise PanelError(data.get('msg') or '3x-ui API error')
            return data

    async def get_client(self,email):
        return await self._request('GET', f'/panel/api/clients/get/{quote(email, safe="")}')

    async def add_client(self, *, email, inbound_id, total_bytes, expiry_ms, tg_id):
        body={'client':{'email':email,'totalGB':total_bytes,'expiryTime':expiry_ms,'tgId':tg_id,'limitIp':0,'limitHwid':0,'enable':True},'inboundIds':[inbound_id]}
        await self._request('POST','/panel/api/clients/add',json=body)
        return await self.get_client(email)

    async def update_client(self,email,**fields):
        return await self._request('POST',f'/panel/api/clients/update/{quote(email,safe="")}',json=fields)

    async def links_by_subid(self,sub_id):
        data=await self._request('GET',f'/panel/api/clients/subLinks/{quote(sub_id,safe="")}')
        return data.get('obj') or []

    async def info_by_subid(self,sub_id):
        url=f'{settings.panel_sub_base_url.rstrip("/")}/{quote(sub_id,safe="")}';
        async with httpx.AsyncClient(timeout=20,verify=True) as c:
            r=await c.get(url,headers={'Accept':'application/json'})
            r.raise_for_status()
            return r.text, dict(r.headers)
