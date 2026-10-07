from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import Session
from app.db.models import User,Plan,Order,Payment,Service
from app.bot.keyboards import main,plan,admin,review,plan_admin
from app.config import settings
from app.services.provision import provision_order
from app.services.panel import ThreeXUI
import qrcode, io

router=Router()

class AddPlan(StatesGroup):
    name=State(); description=State(); price=State(); volume=State(); days=State(); inbound=State()

async def get_user(m):
    async with Session() as s:
        u=(await s.execute(select(User).where(User.telegram_id==m.from_user.id))).scalar_one_or_none()
        if not u:
            u=User(telegram_id=m.from_user.id,username=m.from_user.username,first_name=m.from_user.first_name);s.add(u);await s.commit()
        return u

@router.message(Command('start'))
async def start(m):
    await get_user(m)
    await m.answer('سلام 👋\nبه ربات فروش VPN خوش آمدید.\n\nاز منوی زیر سرویس موردنظر را انتخاب کنید.',reply_markup=main())

@router.callback_query(F.data=='plans')
async def plans(c):
    async with Session() as s:
        rows=(await s.execute(select(Plan).where(Plan.enabled==True).order_by(Plan.sort_order,Plan.id))).scalars().all()
    if not rows: await c.message.edit_text('در حال حاضر پلن فعالی وجود ندارد.'); return
    for p in rows:
        txt=f'📦 {p.name}\n💰 {p.price:,} تومان\n📊 {p.volume_gb} GB\n⏳ {p.duration_days} روز\n🔌 نوع: {"Direct" if p.inbound_id==settings.inbound_direct_id else "Tunnel"}\n\n{p.description}'
        await c.message.answer(txt,reply_markup=plan(p.id))
    await c.answer()

@router.callback_query(F.data.startswith('buy:'))
async def buy(c):
    pid=int(c.data.split(':')[1])
    async with Session() as s:
        p=await s.get(Plan,pid); u=(await s.execute(select(User).where(User.telegram_id==c.from_user.id))).scalar_one()
        if not p or not p.enabled: await c.answer('این پلن فعال نیست.',show_alert=True);return
        o=Order(user_id=u.id,plan_id=p.id,amount=p.price);s.add(o);await s.flush();await s.commit(); oid=o.id
    holder=f'\nبه نام: {settings.payment_card_holder}' if settings.payment_card_holder else ''
    await c.message.answer(f'🧾 سفارش #{oid}\n\n💳 شماره کارت:\n`{settings.payment_card_number}`{holder}\n\nمبلغ: **{p.price:,} تومان**\n\nپس از واریز، عکس رسید را همینجا ارسال کنید.',parse_mode='Markdown')
    await c.answer()

@router.message(F.photo)
async def receipt(m):
    async with Session() as s:
        u=(await s.execute(select(User).where(User.telegram_id==m.from_user.id))).scalar_one_or_none()
        if not u:return
        o=(await s.execute(select(Order).where(Order.user_id==u.id,Order.status=='awaiting_receipt').order_by(Order.id.desc()))).scalars().first()
        if not o: await m.answer('سفارش بازی برای دریافت رسید ندارید.');return
        old=await s.get(Payment,o.id)
        if old and old.status=='pending': await m.answer('رسید شما قبلاً ثبت شده است.');return
        p=Payment(order_id=o.id,receipt_file_id=m.photo[-1].file_id);s.add(p);o.status='payment_pending';await s.commit()
        plan_obj=await s.get(Plan,o.plan_id)
    for aid in settings.admin_ids:
        await m.bot.send_photo(aid,m.photo[-1].file_id,caption=f'🧾 رسید سفارش #{o.id}\n👤 کاربر: {m.from_user.id}\n📦 پلن: {plan_obj.name}\n💰 مبلغ: {o.amount:,} تومان',reply_markup=review(o.id))
    await m.answer('✅ رسید دریافت شد و برای بررسی ادمین ارسال شد.')

@router.callback_query(F.data.startswith('approve:'))
async def approve(c):
    if c.from_user.id not in settings.admin_ids:return await c.answer('دسترسی ندارید',show_alert=True)
    oid=int(c.data.split(':')[1])
    async with Session() as s:
        o=(await s.execute(select(Order).options(selectinload(Order.plan),selectinload(Order.user)).where(Order.id==oid))).scalar_one_or_none()
        if not o:return await c.answer('سفارش پیدا نشد',show_alert=True)
        if o.status=='completed':return await c.answer('قبلاً تکمیل شده است')
        p=await s.get(Payment,oid)
        if not p or p.status!='pending':return await c.answer('رسید در وضعیت قابل تأیید نیست',show_alert=True)
        o.status='provisioning';p.status='approved';p.reviewed_by=c.from_user.id
        await s.commit()
        try:
            svc=await provision_order(s,o,o.plan,o.user)
            o.status='completed';await s.commit()
            links=await ThreeXUI().links_by_subid(svc.sub_id)
            sub=settings.panel_sub_base_url.rstrip('/')+'/'+svc.sub_id
            await c.bot.send_message(o.user.telegram_id,f'🎉 سرویس شما فعال شد!\n\n📦 {o.plan.name}\n⏳ {o.plan.duration_days} روز\n📊 {o.plan.volume_gb} GB\n\n🔗 Subscription:\n`{sub}`',parse_mode='Markdown')
            if links:
                for link in links:
                    await c.bot.send_message(o.user.telegram_id,f'🔐 VLESS:\n`{link}`',parse_mode='Markdown')
                    qr=qrcode.make(link);buf=io.BytesIO();qr.save(buf,format='PNG');buf.seek(0)
                    await c.bot.send_photo(o.user.telegram_id,buf,caption='📱 QR Code')
            await c.message.edit_reply_markup(reply_markup=None);await c.answer('تأیید و ساخت سرویس انجام شد.')
        except Exception as e:
            o.status='provision_error';await s.commit();await c.answer('پرداخت تأیید شد ولی ساخت سرویس خطا داد؛ سفارش برای retry باقی ماند.',show_alert=True);raise

@router.callback_query(F.data.startswith('reject:'))
async def reject(c):
    if c.from_user.id not in settings.admin_ids:return await c.answer('دسترسی ندارید',show_alert=True)
    oid=int(c.data.split(':')[1])
    async with Session() as s:
        o=await s.get(Order,oid);p=await s.get(Payment,oid)
        if o and p:p.status='rejected';p.reviewed_by=c.from_user.id;o.status='rejected';await s.commit();uid=o.user_id
        else:return await c.answer('پیدا نشد',show_alert=True)
        u=await s.get(User,uid)
    await c.bot.send_message(u.telegram_id,f'❌ رسید سفارش #{oid} رد شد. در صورت نیاز با پشتیبانی تماس بگیرید.');await c.message.edit_reply_markup(reply_markup=None);await c.answer('رد شد')

@router.callback_query(F.data=='services')
async def services(c):
    async with Session() as s:
        u=(await s.execute(select(User).where(User.telegram_id==c.from_user.id))).scalar_one_or_none()
        svcs=(await s.execute(select(Service).options(selectinload(Service.plan)).where(Service.user_id==u.id).order_by(Service.id.desc()))).scalars().all() if u else []
    if not svcs:return await c.message.answer('هنوز سرویسی ندارید.')
    for x in svcs:
        await c.message.answer(f'📦 {x.plan.name}\n📧 {x.email}\n🔗 {settings.panel_sub_base_url.rstrip("/")}/{x.sub_id}')
    await c.answer()

@router.callback_query(F.data=='support')
async def support(c): await c.message.answer('🆘 برای پشتیبانی، پیام خود را برای ادمین ارسال کنید.');await c.answer()

@router.message(Command('admin'))
async def admin_cmd(m):
    if m.from_user.id not in settings.admin_ids:return
    await m.answer('پنل مدیریت',reply_markup=admin())

@router.callback_query(F.data=='admin_orders')
async def admin_orders(c):
    if c.from_user.id not in settings.admin_ids:return
    async with Session() as s:
        rows=(await s.execute(select(Order).options(selectinload(Order.user),selectinload(Order.plan)).where(Order.status=='payment_pending').order_by(Order.id))).scalars().all()
    if not rows:return await c.message.answer('سفارش در انتظار نداریم.')
    for o in rows: await c.message.answer(f'🧾 #{o.id}\n👤 {o.user.telegram_id}\n📦 {o.plan.name}\n💰 {o.amount:,}',reply_markup=review(o.id))

@router.callback_query(F.data=='admin_plans')
async def admin_plans(c):
    if c.from_user.id not in settings.admin_ids:return
    async with Session() as s: rows=(await s.execute(select(Plan).order_by(Plan.id))).scalars().all()
    await c.message.answer('دستورها:\n/addplan برای ساخت پلن\n/editplan ID name|description|price|GB|days|inbound\n/delplan ID\n/toggleplan ID\n\nپلن‌ها:')
    for p in rows: await c.message.answer(f'#{p.id} {p.name} — {p.price:,} — {p.volume_gb}GB/{p.duration_days}d — inbound {p.inbound_id} — {"ON" if p.enabled else "OFF"}',reply_markup=plan_admin(p.id))

@router.message(Command('addplan'))
async def addplan(m,state:FSMContext):
    if m.from_user.id not in settings.admin_ids:return
    await state.set_state(AddPlan.name);await m.answer('نام پلن؟')

@router.message(AddPlan.name)
async def ap1(m,state):await state.update_data(name=m.text);await state.set_state(AddPlan.description);await m.answer('توضیحات؟')
@router.message(AddPlan.description)
async def ap2(m,state):await state.update_data(description=m.text);await state.set_state(AddPlan.price);await m.answer('قیمت به تومان؟')
@router.message(AddPlan.price)
async def ap3(m,state):await state.update_data(price=int(m.text.replace(',','')));await state.set_state(AddPlan.volume);await m.answer('حجم به GB؟')
@router.message(AddPlan.volume)
async def ap4(m,state):await state.update_data(volume_gb=int(m.text));await state.set_state(AddPlan.days);await m.answer('مدت به روز؟')
@router.message(AddPlan.days)
async def ap5(m,state):await state.update_data(duration_days=int(m.text));await state.set_state(AddPlan.inbound);await m.answer(f'Inbound؟ فقط {settings.inbound_direct_id} یا {settings.inbound_tunnel_id}')
@router.message(AddPlan.inbound)
async def ap6(m,state):
    d=await state.update_data(inbound_id=int(m.text));data=await state.get_data()
    async with Session() as s:s.add(Plan(**data));await s.commit()
    await state.clear();await m.answer('✅ پلن ساخته شد.')

@router.message(Command('editplan'))
async def editplan(m):
    if m.from_user.id not in settings.admin_ids:return
    try: pid,rest=m.text.split(maxsplit=1);pid=int(pid);name,desc,price,gb,days,inbound=rest.split('|');
    except: return await m.answer('فرمت: /editplan ID name|description|price|GB|days|inbound')
    async with Session() as s:
        p=await s.get(Plan,pid)
        if not p:return await m.answer('پلن پیدا نشد')
        p.name=name;p.description=desc;p.price=int(price);p.volume_gb=int(gb);p.duration_days=int(days);p.inbound_id=int(inbound);await s.commit()
    await m.answer('✅ ویرایش شد.')

@router.message(Command('delplan'))
async def delplan(m):
    if m.from_user.id not in settings.admin_ids:return
    try:pid=int(m.text.split()[1])
    except:return
    async with Session() as s:
        p=await s.get(Plan,pid)
        if p:await s.delete(p);await s.commit()
    await m.answer('✅ حذف شد.')

@router.message(Command('toggleplan'))
async def toggleplan(m):
    if m.from_user.id not in settings.admin_ids:return
    try:pid=int(m.text.split()[1])
    except:return
    async with Session() as s:
        p=await s.get(Plan,pid)
        if p:p.enabled=not p.enabled;await s.commit();msg='فعال' if p.enabled else 'غیرفعال'
        else:msg='پیدا نشد'
    await m.answer(f'پلن {msg}.')

@router.callback_query(F.data.startswith('toggleplan:'))
async def toggle_plan_cb(c):
    if c.from_user.id not in settings.admin_ids:return
    pid=int(c.data.split(':')[1])
    async with Session() as s:
        p=await s.get(Plan,pid)
        if not p:return await c.answer('پیدا نشد',show_alert=True)
        p.enabled=not p.enabled;await s.commit();state='فعال' if p.enabled else 'غیرفعال'
    await c.answer(state);await c.message.edit_text(f'پلن #{pid}: {state}')

@router.callback_query(F.data.startswith('delplan:'))
async def del_plan_cb(c):
    if c.from_user.id not in settings.admin_ids:return
    pid=int(c.data.split(':')[1])
    async with Session() as s:
        p=await s.get(Plan,pid)
        if not p:return await c.answer('پیدا نشد',show_alert=True)
        await s.delete(p);await s.commit()
    await c.answer('حذف شد');await c.message.edit_text(f'پلن #{pid} حذف شد.')

@router.callback_query(F.data.startswith('cancel:'))
async def cancel_order(c):
    oid=int(c.data.split(':')[1])
    async with Session() as s:
        o=await s.get(Order,oid)
        if not o or o.user_id!=(await s.execute(select(User).where(User.telegram_id==c.from_user.id))).scalar_one().id:return await c.answer('سفارش معتبر نیست',show_alert=True)
        if o.status in ('awaiting_receipt','payment_pending'):o.status='cancelled';await s.commit()
    await c.answer('لغو شد');await c.message.answer('سفارش لغو شد.')
