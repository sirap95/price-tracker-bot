from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters
from config import BOT_TOKEN
from handlers import start, add, get_url, get_price, list_items, remove_item, get_item_number, cancel, URL, PRICE, REMOVE, periodic_price_check
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

def main():
    # Enable logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    # Create the application and pass the bot's token
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Define the conversation handler with states URL, PRICE, and REMOVE
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add)],
        states={
            URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_url)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
            REMOVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_item_number)]  # New state for removing items
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Add handlers to the application
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('list', list_items))
    application.add_handler(CommandHandler('remove', remove_item))

    # Initialize the APScheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(periodic_price_check, trigger=IntervalTrigger(seconds=60), id='price_check_job')  # Check every 60 seconds
    scheduler.start()

    try:
        # Start the bot
        application.run_polling()
    except KeyboardInterrupt:
        # Stop the scheduler on keyboard interrupt
        scheduler.shutdown()

if __name__ == '__main__':
    main()
