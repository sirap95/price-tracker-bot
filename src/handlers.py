from telegram import Update, Bot
from telegram.ext import ContextTypes, ConversationHandler

from config import BOT_TOKEN
from price_fetcher import fetch_price, fetch_object_name
import logging

# States for the conversation
URL, PRICE, REMOVE = range(3)

# Dictionary to store each user's list of tracked items
user_data = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define your async functions for the conversation

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Entered start function.")
    await update.message.reply_text("Welcome! Use /add to start tracking a product.")
    return ConversationHandler.END

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Entered add function. Asking for URL.")
    await update.message.reply_text(
        "Send me the URL of the product you want to track."
    )
    return URL  # Proceed to the URL state

async def get_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = update.message.text
        logger.info(f"Received URL: {url}")
        context.user_data['url'] = url
        context.user_data['object_name'] = 'Sony zv1' #todo: remove constant
        await update.message.reply_text("Got it! Now send me the target price you want to track.")
        return PRICE  # Proceed to the PRICE state
    except Exception as e:
        logger.error(f"Error in get_url: {e}")
        await update.message.reply_text("There was an error processing the URL. Please try again.")
        return ConversationHandler.END


async def get_price_old(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(update.message.text)
        logger.info(f"Received target price: {price}")
        context.user_data['price'] = price
        await update.message.reply_text("Price tracked successfully.")
        return ConversationHandler.END
    except ValueError:
        logger.error("Invalid price format.")
        await update.message.reply_text("Please enter a valid number for the price.")
        return PRICE

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        target_price = float(update.message.text)
        logger.info(f"Received target price: {target_price}")
        chat_id = update.message.chat_id
        url = context.user_data['url']
        context.user_data['target_price'] = target_price
        logger.info(f"Received target price: {target_price} for URL: {url}")

        # Ensure the chat_id exists in user_data and initialize if necessary
        if chat_id not in user_data:
            user_data[chat_id] = []  # Initialize as an empty list

        object_name = fetch_object_name(url)
        # Add the URL and target price to the user's tracking list
        user_data[chat_id].append({'object_name': object_name, 'url': url, 'target_price': target_price})

        await update.message.reply_text(
            f"Great! I'll notify you if the price of {object_name} drops below €{target_price}."
        )
    except ValueError:
        logger.warning("Invalid price entered.")
        await update.message.reply_text("Please send a valid number for the target price.")
        return PRICE
    except Exception as e:
        logger.error(f"Error in get_price: {e}")
        await update.message.reply_text("There was an error processing your request. Please try again.")
        return ConversationHandler.END

    return ConversationHandler.END


async def list_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in user_data and user_data[chat_id]:
        message = "Here are the items you're tracking:\n"
        for i, item in enumerate(user_data[chat_id], start=1):
            message += f"{i}. OBJECT: {item['object_name']}, URL: {item['url']}, Target Price: €{item['target_price']}\n"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("You're not tracking any items.")


async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in user_data and user_data[chat_id]:
        message = "Send the number of the item you want to remove:\n"
        for i, item in enumerate(user_data[chat_id], start=1):
            message += f"{i}. URL: {item['url']}, Target Price: €{item['target_price']}\n"
        await update.message.reply_text(message)
        return REMOVE  # New state for removing items
    else:
        await update.message.reply_text("You're not tracking any items.")
        return ConversationHandler.END


async def get_item_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    logger.info("Entering get_item_number function.")  # Debugging log
    try:
        item_number = int(update.message.text) - 1
        logger.info(f"User selected item number: {item_number + 1}")  # Log the input
        if 0 <= item_number < len(user_data[chat_id]):
            removed_item = user_data[chat_id].pop(item_number)
            await update.message.reply_text(
                f"Removed item: URL: {removed_item['url']}, Target Price: €{removed_item['target_price']}"
            )
        else:
            await update.message.reply_text("Invalid item number. Please try again.")
            return REMOVE  # Keep in the REMOVE state for another try
    except ValueError:
        await update.message.reply_text("Please send a valid number.")
        return REMOVE  # Keep in the REMOVE state for another try
    except Exception as e:
        logger.error(f"Error in get_item_number: {e}")
        await update.message.reply_text("There was an error processing your request. Please try again.")
        return ConversationHandler.END

    return ConversationHandler.END


async def periodic_price_check():
    for chat_id, items in user_data.items():
        for item in items:
            await track_price(chat_id, item['url'], item['target_price'])


async def track_price(chat_id, url, target_price):
    current_price = fetch_price(url)
    if current_price is None:
        # Unable to fetch the price, send a message if required
        return

    if current_price <= target_price:
        bot = Bot(token=BOT_TOKEN)  # Create a new Bot instance
        await bot.send_message(
            chat_id=chat_id,
            text=f'Price drop alert! The product is now €{current_price}. Check it out: {url}'
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Price tracking has been cancelled.")
    return ConversationHandler.END
