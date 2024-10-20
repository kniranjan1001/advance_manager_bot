import os
import base64
import logging
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.helpers import escape_markdown

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Prefix for encoded links
CC_LINK_PREFIX = "cclink"
BOT_TOKEN = '7655559636:AAHiU-jPi0OffoZgKGE3CWU6Di9WYVNOb6k'
JSON_FILE_PATH = 'movie_links.txt'  # Path to the JSON file

# Function to encode text
def encode_text(input: str) -> str:
    return f"{CC_LINK_PREFIX}{base64.b64encode(input.encode('utf-8')).decode('utf-8')}"

# Function to decode text
def decode_text(encoded_string: str) -> str:
    if encoded_string.startswith(CC_LINK_PREFIX):
        encoded_string = encoded_string[len(CC_LINK_PREFIX):]
    return base64.b64decode(encoded_string).decode('utf-8')

# Command to show bot commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    commands = (
        "Welcome to the Bot! Here are the available commands:\n\n"
        "/encode <MovieName><link> - Encode the given movie name and link.\n"
        "Example: /encode Inception http://example.com/download\n\n"
        "/decode <encoded_text> - Decode the encoded text.\n"
        "Example: /decode cclink:SGVsbG8gV29ybGQ=\n\n"
        "/movie_template <MovieNAME>,<link> - Format and return movie information and save it.\n"
        "Example: /movie_template Inception, http://example.com/download\n\n"
        "/jsonlinks - Retrieve all saved movie links in JSON format.\n\n"
        "/deletejson - Delete all saved movie links.\n\n"
        "/webseries_template <Webseries Name>, <Season> <link> - Format and return web series information.\n"
        "Example: /webseries_template Kingdom, Season 1 http://google.com, Season 2 http://demowebsite.com\n\n"
        "/webseries_json <Webseries Name> <link> - Add web series name and link to the JSON file.\n"
        "Example: /webseries_json Kingdom http://google.com\n\n"
        "/search_data <Movie or Webseries Name> - Check if the movie or web series is present in the JSON file.\n"
        "Example: /search_data Inception\n"
    )
    await update.message.reply_text(commands)

# Command to encode movie name and link
async def encode_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        # Check if the last argument is 'movie'
        if context.args[-1].lower() == "movie":
            movie_link = " ".join(context.args[:-1])  # Join all except the last
        else:
            movie_link = " ".join(context.args)  # Join all arguments if 'movie' is not present

        # Find the last space to split movie name and link
        last_space_index = movie_link.rfind(" ")
        if last_space_index != -1:
            movie_name = movie_link[:last_space_index].strip()
            link = movie_link[last_space_index:].strip()
            encoded_result = encode_text(f"{movie_name} {link}")

            # If "movie" is in the arguments, run the movie_template command
            if context.args[-1].lower() == "movie":
                await movie_template_command(update, context)

            # Send the formatted response
            response_message = (
                "📛 Code Generated Successfully\n\n"
                f"<code>{encoded_result}</code>\n\n"
                "=================\n"
                "🎬 Steps to download - [here](https://t.me/cctuitorial)"
            )
            await update.message.reply_text(response_message, parse_mode='HTML')
        else:
            await update.message.reply_text("Usage: /encode <MovieName> <link>")
    else:
        await update.message.reply_text("Usage: /encode <MovieName> <link>")



# Command to decode text
async def decode_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        encoded_text = " ".join(context.args)
        try:
            decoded_result = decode_text(encoded_text)
            await update.message.reply_text(f"Decoded text: {decoded_result}")
        except Exception as e:
            await update.message.reply_text("Failed to decode the text.")
            logger.error(f"Decoding error: {e}")
    else:
        await update.message.reply_text("Usage: /decode <encoded_text>")

# Command to format movie information and save to file
async def movie_template_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        try:
            movie_info = " ".join(context.args)
            movie_name, link = map(str.strip, movie_info.split(','))
            formatted_message = (
                f"😍 {escape_markdown(movie_name)}\n\n"
                f"[➡️Download Here]({escape_markdown(link)}) 🔴\n\n"
                f"Join ▶️ @cc_new_movie"
            )
            await update.message.reply_text(formatted_message, disable_web_page_preview=True)

            # Create a JSON format and save to file
            movie_json = {movie_name: link}
            # Load existing data
            if os.path.exists(JSON_FILE_PATH):
                with open(JSON_FILE_PATH, 'r') as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = {}
            else:
                data = {}

            # Add new movie to the dictionary
            data.update(movie_json)

            # Save updated data back to file
            with open(JSON_FILE_PATH, 'w') as file:
                json.dump(data, file)

        except ValueError:
            await update.message.reply_text("Usage: /movie_template <MovieNAME>,<link>")
    else:
        await update.message.reply_text("Usage: /movie_template <MovieNAME>,<link>")

# Command to retrieve all saved movie links in JSON format
async def jsonlinks_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r') as file:
            try:
                data = json.load(file)
                json_response = json.dumps(data, indent=4)
                await update.message.reply_text(f"Saved movie links:\n```\n{json_response}\n```", parse_mode='MarkdownV2')
            except json.JSONDecodeError:
                await update.message.reply_text("No valid JSON data found.")
    else:
        await update.message.reply_text("No movie links saved yet.")

# Command to delete all saved movie links
async def deletejson_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if os.path.exists(JSON_FILE_PATH):
        os.remove(JSON_FILE_PATH)
        await update.message.reply_text("All saved movie links have been deleted.")
    else:
        await update.message.reply_text("No movie links to delete.")

# Command to format web series information and save to file
async def webseries_template_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        try:
            webseries_info = " ".join(context.args)
            parts = webseries_info.split(',')
            webseries_name = parts[0].strip()
            seasons = []

            for part in parts[1:]:
                season_info = part.strip().split()
                if len(season_info) < 2:
                    continue
                season_name = " ".join(season_info[:-1])
                link = season_info[-1].strip()
                seasons.append(f"👉 {season_name} [{link}]")

            formatted_message = (
                f"😍 {escape_markdown(webseries_name)}\n\n"
                + "\n".join(seasons) + "\n\n"
                "Join ▶️ @cc_new_movie"
            )
            await update.message.reply_text(formatted_message, disable_web_page_preview=True)

        except Exception as e:
            await update.message.reply_text("Failed to format web series information.")
            logger.error(f"Error in webseries_template: {e}")
    else:
        await update.message.reply_text("Usage: /webseries_template <Webseries Name>, <Season> <link>")

# Command to add web series to JSON file
async def webseries_json_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        # Join the args to allow for spaces in the web series name and split on the first comma
        input_data = " ".join(context.args).strip()
        if ',' in input_data:
            webseries_name, link = map(str.strip, input_data.split(',', 1))

            # Create a JSON format
            webseries_json = {webseries_name: link}

            # Load existing data
            if os.path.exists(JSON_FILE_PATH):
                with open(JSON_FILE_PATH, 'r') as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = {}
            else:
                data = {}

            # Add new web series to the dictionary
            data.update(webseries_json)

            # Save updated data back to the file
            with open(JSON_FILE_PATH, 'w') as file:
                json.dump(data, file)

            await update.message.reply_text("Added successfully.")
        else:
            await update.message.reply_text("Usage: /webseries_json <Webseries Name>, <link>")
    else:
        await update.message.reply_text("Usage: /webseries_json <Webseries Name>, <link>")


# Command to search for movie or web series name
async def search_data_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        search_name = " ".join(context.args).strip()
        
        if os.path.exists(JSON_FILE_PATH):
            with open(JSON_FILE_PATH, 'r') as file:
                try:
                    data = json.load(file)
                    if search_name in data:
                        await update.message.reply_text("Yes, the movie or web series is present.")
                    else:
                        await update.message.reply_text("No, the movie or web series is not present.")
                except json.JSONDecodeError:
                    await update.message.reply_text("No valid JSON data found.")
        else:
            await update.message.reply_text("No movie or web series links saved yet.")
    else:
        await update.message.reply_text("Usage: /search_data <Movie or Webseries Name>")

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("encode", encode_command))
    application.add_handler(CommandHandler("decode", decode_command))
    application.add_handler(CommandHandler("movie_template", movie_template_command))
    application.add_handler(CommandHandler("jsonlinks", jsonlinks_command))
    application.add_handler(CommandHandler("deletejson", deletejson_command))
    application.add_handler(CommandHandler("webseries_template", webseries_template_command))
    application.add_handler(CommandHandler("webseries_json", webseries_json_command))
    application.add_handler(CommandHandler("search_data", search_data_command))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
