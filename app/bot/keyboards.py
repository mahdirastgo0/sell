from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🛒 خرید سرویس',callback_data='plans')],[InlineKeyboardButton(text='📦 سرویس‌های من',callback_data='services')],[InlineKeyboardButton(text='🆘 پشتیبانی',callback_data='support')]])
def plan(pid): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='💳 خرید این پلن',callback_data=f'buy:{pid}')],[InlineKeyboardButton(text='🔙 بازگشت',callback_data='plans')]])
def admin(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='📋 سفارش‌های در انتظار',callback_data='admin_orders')],[InlineKeyboardButton(text='🗂 مدیریت پلن‌ها',callback_data='admin_plans')]])
def payment(order_id): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='❌ لغو سفارش',callback_data=f'cancel:{order_id}')]])
def review(order_id): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ تأیید',callback_data=f'approve:{order_id}'),InlineKeyboardButton(text='❌ رد',callback_data=f'reject:{order_id}')]])
def plan_admin(pid): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🟢/🔴 فعال/غیرفعال',callback_data=f'toggleplan:{pid}')],[InlineKeyboardButton(text='🗑 حذف',callback_data=f'delplan:{pid}')]])
