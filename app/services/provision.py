from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Service, Order
from app.services.panel import ThreeXUI

async def provision_order(session: AsyncSession, order: Order, plan, user):
    existing=(await session.execute(select(Service).where(Service.order_id==order.id))).scalar_one_or_none()
    if existing:
        return existing
    email=f'tg_{user.telegram_id}_ord_{order.id}'
    expiry=int((datetime.now(timezone.utc)+timedelta(days=plan.duration_days)).timestamp()*1000)
    panel=ThreeXUI()
    result=await panel.add_client(email=email,inbound_id=plan.inbound_id,total_bytes=plan.volume_gb*1024**3,expiry_ms=expiry,tg_id=user.telegram_id)
    client=result.get('obj',{}).get('client',{}) if isinstance(result.get('obj'),dict) else {}
    sub_id=client.get('subId')
    uuid=client.get('id') or client.get('uuid')
    if not sub_id:
        fresh=await panel.get_client(email)
        obj=fresh.get('obj') or {}
        client=obj.get('client',obj) if isinstance(obj,dict) else {}
        sub_id=client.get('subId'); uuid=client.get('id') or client.get('uuid')
    if not sub_id: raise RuntimeError('3x-ui created client but returned no subId')
    svc=Service(user_id=user.id,order_id=order.id,plan_id=plan.id,inbound_id=plan.inbound_id,email=email,sub_id=sub_id,uuid=uuid,enabled=True)
    session.add(svc); await session.flush(); return svc
