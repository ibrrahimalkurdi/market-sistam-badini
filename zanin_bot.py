# -*- coding: utf-8 -*-

# کتابخانەیێن پێدڤی
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ل ڤێرێ تۆکنێ بۆتێ خۆ یێ کو تە ژ BotFather وەرگرتی بنڤیسە
BOT_TOKEN = "HI:YOUR_TELEGRAM_BOT_TOKEN_HERE"

# چالاکرنا لۆگینگێ بۆ زانینا کێشەیان
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# ئەم دێ داتایان ب شێوەیەکێ دەمکی د ڤێ دیکشنەریێ دا پاشکەفت کەین
# کیلیلا وێ user_id یە، دا کو داتایێن هەر کەسەکی جودا بن
user_data = {}

# فەنکشنێن فەرمانان (Commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ئەڤ فەرمانە دەمێ بکارئینەر بۆتێ دەستپێدکەت کار دکەت"""
    user = update.effective_user
    user_id = user.id
    
    # ئامادەکرنا داتایێن بکارئینەری ئەگەر یێ نوو بیت
    if user_id not in user_data:
        user_data[user_id] = {
            'tasks': [],
            'goals': []
        }

    # دروستکرنا کیبۆردەکێ بۆ ئاسانکاریا بکارئینانێ
    keyboard = [
        ['/erken_min', '/erke_nu'],
        ['/armancan_bibine', '/armance_nu'],
        ['/alikarî']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_html(
        rf"بخێر بهێی {user.mention_html()} بۆ بۆتێ رێبوارێ زانینێ!",
        reply_markup=reply_markup,
    )
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """فەرمانا /alikarî بۆ نیشادانا رێنماییان"""
    await update.message.reply_text("""
    فەرمانێن بەردەست:
    /start - بۆ دەستپێکرنا بۆتی
    /erke_nu [ناڤێ ئەرکی] - بۆ زێدەکرنا ئەرکەکێ نوو
    /erken_min - بۆ نیشادانا ئەرکێن ئەڤرۆ
    /temam [ژمارا ئەرکی] - بۆ دیارکرنا ئەرکی وەک تمام بووی
    /jebirin [ژمارا ئەرکی] - بۆ ژێبرنا ئەرکەکی
    /alikarî - بۆ نیشادانا ڤێ لیستێ
    """)

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """بۆ زێدەکرنا ئەرکەکێ نوو"""
    user_id = update.effective_user.id
    task_text = ' '.join(context.args) # وەرگرتنا تێکستا پشتی فەرمانێ

    if not task_text:
        await update.message.reply_text("تکایە ناڤێ ئەرکی دگەل فەرمانێ بنڤیسە. نمونە: /erke_nu نڤێژا سپێدێ")
        return

    # زێدەکرنا ئەرکی بۆ لیستا وی بکارئینەری
    user_data[user_id]['tasks'].append({'name': task_text, 'completed': False})
    
    await update.message.reply_text(f"ئەرکێ '{task_text}' هاتە زێدەکرن.")
    await view_tasks(update, context) # نیشادانا لیستا نوو

async def view_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """بۆ نیشادانا هەمی ئەرکان"""
    user_id = update.effective_user.id
    tasks = user_data.get(user_id, {}).get('tasks', [])

    if not tasks:
        await update.message.reply_text("هیچ ئەرکەک بۆ ئەڤرۆ نینە.")
        return

    message = "ئەرکێن تە یێن ئەڤرۆ:\n"
    for i, task in enumerate(tasks):
        status = "✅" if task['completed'] else "🔘"
        message += f"{i + 1}. {status} {task['name']}\n"
    
    message += "\nبۆ تمامکرنا ئەرکەکی بنڤیسە: /temam [ژمارا ئەرکی]"
    await update.message.reply_text(message)

async def complete_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """بۆ دیارکرنا ئەرکەکی وەک تمام بووی"""
    user_id = update.effective_user.id
    try:
        task_index = int(context.args[0]) - 1
        tasks = user_data.get(user_id, {}).get('tasks', [])
        if 0 <= task_index < len(tasks):
            tasks[task_index]['completed'] = not tasks[task_index]['completed'] # Toggle status
            await update.message.reply_text("ئەرک هاتە نویکرن!")
            await view_tasks(update, context)
        else:
            await update.message.reply_text("ژمارەکا خەلەت.")
    except (IndexError, ValueError):
        await update.message.reply_text("تکایە ژمارا ئەرکی بنڤیسە. نمونە: /temam 1")

async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """بۆ ژێبرنا ئەرکەکی"""
    user_id = update.effective_user.id
    try:
        task_index = int(context.args[0]) - 1
        tasks = user_data.get(user_id, {}).get('tasks', [])
        if 0 <= task_index < len(tasks):
            removed_task = tasks.pop(task_index)
            await update.message.reply_text(f"ئەرکێ '{removed_task['name']}' هاتە ژێبرن.")
            await view_tasks(update, context)
        else:
            await update.message.reply_text("ژمارەکا خەلەت.")
    except (IndexError, ValueError):
        await update.message.reply_text("تکایە ژمارا ئەرکی بنڤیسە. نمونە: /jebirin 1")

# فەنکشنێ سەرەکی
def main() -> None:
    """بۆتی دەستپێبکە"""
    # دروستکرنا ئۆبجێکتێ ئەپلیکەیشنێ
    application = Application.builder().token(BOT_TOKEN).build()

    # زێدەکرنا فەرمانان
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("alikarî", help_command))
    application.add_handler(CommandHandler("erke_nu", add_task))
    application.add_handler(CommandHandler("erken_min", view_tasks))
    application.add_handler(CommandHandler("temam", complete_task))
    application.add_handler(CommandHandler("jebirin", delete_task))
    
    # دەستپێکرنا بۆتی
    application.run_polling()

if __name__ == "__main__":
    main()
