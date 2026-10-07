from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🛒 خرید سرویس', callback_data='plans')],
        [InlineKeyboardButton(text='📦 سرویس‌های من', callback_data='services')],
        [InlineKeyboardButton(text='🆘 پشتیبانی', callback_data='support')],
    ])

def plan(pid):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='💳 خرید این پلن', callback_data=f'buy:{pid}')],
        [InlineKeyboardButton(text='🔙 بازگشت', callback_data='plans')],
    ])

def admin():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📋 سفارش‌های در انتظار', callback_data='admin_orders')],
        [InlineKeyboardButton(text='🗂 مدیریت پلن‌ها', callback_data='admin_plans')],
        [InlineKeyboardButton(text='➕ افزودن پلن', callback_data='add_plan')],
    ])

def review(order_id):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ تأیید', callback_data=f'approve:{order_id}'), InlineKeyboardButton(text='❌ رد', callback_data=f'reject:{order_id}')]])
