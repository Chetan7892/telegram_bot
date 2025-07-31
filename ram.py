from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

BOT_TOKEN = "8417075230:AAE3Z5JEcyU7_v5I_CXTBDpwaekd7R5oTCM"
BASE_DIR = "question_papers"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📘 School", callback_data="category:school")],
        [InlineKeyboardButton("🎓 College", callback_data="category:college")],
        [InlineKeyboardButton("🏛️ Govt Exams", callback_data="category:govt")]
    ]
    await update.message.reply_text("Choose your category:", reply_markup=InlineKeyboardMarkup(keyboard))

# Category selection
async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.split(":")[1]
    context.user_data['category'] = category

    if category == "school":
        classes = ['class5', 'class8', 'class10', 'class12']
        keyboard = [[InlineKeyboardButton(cls.upper(), callback_data=f"class:{cls}")] for cls in classes]
        await query.edit_message_text("Choose class:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif category == "college":
        streams = ['arts', 'commerce', 'bca', 'pcb', 'biology', 'bsc', 'ba', 'bcom']
        keyboard = [[InlineKeyboardButton(s.title(), callback_data=f"stream:{s}")] for s in streams]
        await query.edit_message_text("Choose your stream:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif category == "govt":
        exams = ['ssc', 'upsc', 'railway', 'patwari', '1st_grade', '2nd_grade', 'reet']
        keyboard = [[InlineKeyboardButton(exam.replace("_", " ").title(), callback_data=f"exam:{exam}")] for exam in exams]
        await query.edit_message_text("Select government exam:", reply_markup=InlineKeyboardMarkup(keyboard))

# School class selection
async def class_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    class_selected = query.data.split(":")[1]
    context.user_data['class'] = class_selected

    years = [str(y) for y in range(2020, 2026)]
    keyboard = [[InlineKeyboardButton(year, callback_data=f"year:{year}")] for year in years]
    await query.edit_message_text("Choose year:", reply_markup=InlineKeyboardMarkup(keyboard))

# College stream selection
async def stream_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    stream = query.data.split(":")[1]
    context.user_data['stream'] = stream

    years = ['1st_year', '2nd_year', '3rd_year', '4th_year']
    keyboard = [[InlineKeyboardButton(y.replace("_", " ").title(), callback_data=f"college_year:{y}")] for y in years]
    await query.edit_message_text("Choose college year:", reply_markup=InlineKeyboardMarkup(keyboard))

# College year handler
async def college_year_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    year = query.data.split(":")[1]
    context.user_data['college_year'] = year

    paper_years = [str(y) for y in range(2015, 2021)]
    keyboard = [[InlineKeyboardButton(y, callback_data=f"year:{y}")] for y in paper_years]
    await query.edit_message_text("Choose exam year:", reply_markup=InlineKeyboardMarkup(keyboard))

# Govt exam selection
async def govt_exam_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    exam = query.data.split(":")[1]
    context.user_data['exam'] = exam

    folder_path = os.path.join(BASE_DIR, 'govt', exam)
    if not os.path.exists(folder_path):
        await query.edit_message_text("No papers found for this exam.")
        return

    years = [f[:-4] for f in os.listdir(folder_path) if f.endswith('.pdf')]
    keyboard = [[InlineKeyboardButton(y, callback_data=f"year:{y}")] for y in sorted(years)]
    await query.edit_message_text("Choose year:", reply_markup=InlineKeyboardMarkup(keyboard))

# Final PDF sending
async def send_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_year = query.data.split(":")[1]

    cat = context.user_data.get('category')

    if cat == 'school':
        class_ = context.user_data.get('class')
        path = os.path.join(BASE_DIR, 'school', class_, f"{selected_year}.pdf")

    elif cat == 'college':
        stream = context.user_data.get('stream')
        year = context.user_data.get('college_year')
        path = os.path.join(BASE_DIR, 'college', stream, year, f"{selected_year}.pdf")

    elif cat == 'govt':
        exam = context.user_data.get('exam')
        path = os.path.join(BASE_DIR, 'govt', exam, f"{selected_year}.pdf")

    if os.path.exists(path):
        await context.bot.send_document(chat_id=query.message.chat_id, document=open(path, 'rb'))
    else:
        await query.edit_message_text("❌ Paper not found. Try another.")

# Build & run bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(category_handler, pattern="^category:"))
app.add_handler(CallbackQueryHandler(class_handler, pattern="^class:"))
app.add_handler(CallbackQueryHandler(stream_handler, pattern="^stream:"))
app.add_handler(CallbackQueryHandler(college_year_handler, pattern="^college_year:"))
app.add_handler(CallbackQueryHandler(govt_exam_handler, pattern="^exam:"))
app.add_handler(CallbackQueryHandler(send_pdf, pattern="^year:"))

print("🚀 Bot is running... Ctrl+C to stop.")
app.run_polling()
