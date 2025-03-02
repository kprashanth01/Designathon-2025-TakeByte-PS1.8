import os
import traceback
import asyncio
import httpx
import trafilatura
import logging
import re
import json
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from googleapiclient.discovery import build
from aiolimiter import AsyncLimiter

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('.env')
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Initialize Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Use Gemini 1.5 Flash for image processing (faster, multimodal)
gemini_vision_model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Use Gemini 2.0 Flash for text analysis (better for reasoning)
gemini_text_model = genai.GenerativeModel(model_name="gemini-2.0-flash")

# Create directories
os.makedirs("images", exist_ok=True)

# Adjust rate limiters to be very generous for hackathon demo
gemini_limiter = AsyncLimiter(100, 60)  # 100 requests per minute (very generous)
google_search_limiter = AsyncLimiter(50, 60)  # 50 requests per minute (very generous)

# Track which users are in deepfake mode
user_modes = {}

async def detect_rhetoric_fast(title, snippet, max_chars=300):
    """Quick assessment of rhetoric in title and snippet."""
    if not title and not snippet:
        return ""
        
    text = f"{title} {snippet}"[:max_chars]
    
    # Simple regex-based checks for common patterns
    patterns = {
        "BREAKING": r'\b(?:BREAKING|URGENT)\b',
        "Clickbait": r'\b(?:won\'t believe|shocking|mind-?blowing)\b',
        "Hyperbole": r'\b(?:incredible|amazing|unbelievable|revolutionary|devastat|catastroph)\b',
        "Emotional": r'\b(?:terrifying|horrific|alarming|outrage|anger|furious|hate)\b',
    }
    
    warnings = []
    for label, pattern in patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            warnings.append(f"⚠️ {label}")
    
    return " ".join(warnings)

async def prep_image(image_path):
    """Uploads image to Gemini API."""
    try:
        return genai.upload_file(path=image_path, display_name="Uploaded Image")
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise

async def extract_text_from_image(sample_file):
    """Extracts text from an image using Gemini 1.5 Flash."""
    try:
        async with gemini_limiter:
            response = await asyncio.to_thread(gemini_vision_model.generate_content, 
                [sample_file, "Extract the text in the image verbatim. Only return the exact text from the image."])
            return response.text.strip() if response and response.text else ""
    except Exception as e:
        logger.error(f"Error extracting text from image: {e}")
        traceback.print_exc()
        return ""

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Routes image processing based on user's current mode."""
    user_id = update.effective_user.id
    
    # Check if user is in deepfake mode
    if user_id in user_modes and user_modes[user_id] == "deepfake":
        await process_image_for_deepfake(update, context)
    else:
        # Normal OCR + fact-checking flow
        await process_image_for_factcheck(update, context)

async def process_image_for_factcheck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles image uploads for text extraction and fact-checking."""
    try:
        await update.message.reply_text("📷 Processing image... Please wait.")
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_path = f"images/{photo.file_id}.jpg"
        await file.download_to_drive(image_path)

        sample_file = await prep_image(image_path)
        extracted_text = await extract_text_from_image(sample_file)

        if extracted_text:
            await update.message.reply_text(f"✅ Extracted Text:\n{extracted_text}\n\n🔍 Now fact-checking this content...")
            await handle_message(update, context, extracted_text)
        else:
            await update.message.reply_text("⚠️ Failed to extract text from the image. Please try a clearer image.")
    except Exception as e:
        logger.error(f"Error handling image: {e}")
        traceback.print_exc()
        await update.message.reply_text("❌ Error processing the image. Please try again later.")

async def process_image_for_deepfake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles image uploads for deepfake detection."""
    try:
        progress_message = await update.message.reply_text(
            "🔎 Analyzing image for deepfake indicators...\n\n"
            "Looking for:\n"
            "• Unnatural facial features\n"
            "• Inconsistent shadows\n"
            "• Warped backgrounds\n"
            "• Artificial textures\n\n"
            "This may take up to 30 seconds..."
        )
        
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_path = f"images/deepfake_{photo.file_id}.jpg"
        await file.download_to_drive(image_path)
        
        # Run the deepfake analysis
        analysis = await analyze_deepfake(image_path)
        
        # Delete progress message and send the analysis
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=progress_message.message_id
        )
        
        await update.message.reply_text(analysis)
        
    except Exception as e:
        logger.error(f"Error in deepfake analysis: {e}")
        traceback.print_exc()
        await update.message.reply_text(f"❌ Error analyzing image: {str(e)}")

async def truncate_text(text, max_length=4000):
    """Simple truncation for text that's too long."""
    if not text or len(text) <= max_length:
        return text
    
    # Take first 2000 chars + last 2000 chars (to get intro and conclusion)
    first_part = text[:max_length//2]
    last_part = text[-max_length//2:]
    return first_part + "\n...[content truncated]...\n" + last_part

async def scrape_webpage(url: str) -> str:
    """Scrapes text content from a webpage with minimal processing."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            text = trafilatura.extract(response.text)
            
            if not text:
                return ""
                
            # Simple truncation instead of complex summarization
            truncated_text = await truncate_text(text, 4000)
            return truncated_text
            
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        traceback.print_exc()
        return ""

async def analyze_title_sentiment(titles_snippets):
    """Let Gemini analyze the headlines for sentiment/rhetoric only."""
    try:
        if not titles_snippets:
            return {}
            
        titles_text = "\n".join([f"{i+1}. TITLE: {t['title']}\nSNIPPET: {t['snippet']}" 
                               for i, t in enumerate(titles_snippets)])
        
        prompt = (
            f"Analyze these news headlines and snippets for problematic rhetoric:\n\n"
            f"{titles_text}\n\n"
            f"For each headline, identify if it contains any of these problematic elements:\n"
            f"- Sensationalism (exaggerated claims to provoke reaction)\n"
            f"- Clickbait (misleading or withholding info to generate clicks)\n" 
            f"- Emotional manipulation (exploiting emotions rather than presenting facts)\n"
            f"- Loaded language (biased terms that suggest a conclusion)\n"
            f"- Sarcasm (mocking tone that means opposite of what's said)\n\n"
            f"For each headline, respond with ONLY the headline number and any issues found, like:\n"
            f"1: Sensationalism, Loaded language\n"
            f"2: None\n"
            f"etc."
        )
        
        async with gemini_limiter:
            response = await asyncio.to_thread(
                lambda: gemini_text_model.generate_content(prompt)
            )
            
        if response and hasattr(response, 'text'):
            results = {}
            lines = response.text.strip().split('\n')
            for line in lines:
                if ':' in line:
                    try:
                        num, issues = line.split(':', 1)
                        num = int(num.strip())
                        issues = issues.strip()
                        if issues.lower() != 'none':
                            results[num] = issues
                    except (ValueError, IndexError):
                        pass
            return results
        return {}
    except Exception as e:
        logger.error(f"Error analyzing headlines: {e}")
        return {}

async def get_search_results(claim: str) -> str:
    """Fetches Google search results and scrapes content from sources."""
    try:
        logger.info(f"Searching Google for: {claim}")
        all_results = "Source Content:\n\n"

        async with google_search_limiter:
            service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
            search_results = service.cse().list(
                q=claim, cx=GOOGLE_CSE_ID, num=5, fields="items(title,link,snippet)"
            ).execute()

        if 'items' in search_results:
            urls = [item.get('link', '') for item in search_results['items']]
            logger.info(f"Found {len(urls)} URLs to scrape")
            
            # Prepare titles and snippets for sentiment analysis
            titles_snippets = [
                {"title": item.get('title', ''), "snippet": item.get('snippet', '')}
                for item in search_results['items']
            ]
            
            # Start sentiment analysis in parallel with content scraping
            sentiment_task = asyncio.create_task(analyze_title_sentiment(titles_snippets))
            
            # Start content scraping
            scraping_tasks = [scrape_webpage(url) for url in urls]
            contents = await asyncio.gather(*scraping_tasks, return_exceptions=True)
            
            # Get sentiment results
            headline_issues = await sentiment_task
            
            successful_scrapes = 0
            for i, (item, content) in enumerate(zip(search_results['items'], contents), 1):
                if isinstance(content, Exception) or not content:
                    logger.warning(f"Failed to scrape source {i}: {item.get('link', '')}")
                    continue

                title = item.get('title', '').replace('\n', ' ')
                source = item.get('link', '').split('//')[1].split('/')[0] if '//' in item.get('link', '') else item.get('link', '')
                snippet = item.get('snippet', '').replace('\n', ' ')
                
                # Add any detected issues from headlines
                rhetoric_info = ""
                if i in headline_issues:
                    rhetoric_info = f"⚠️ Rhetoric issues: {headline_issues[i]}\n"
                
                all_results += f"\n=== Source {i}: [{source}] {title} ===\n{rhetoric_info}Snippet: {snippet}\n\nContent:\n{content}\n---\n"
                successful_scrapes += 1
                
            return all_results if successful_scrapes > 0 else "No relevant content found."
        else:
            return "No search results found."
    except Exception as e:
        logger.error(f"Search error: {e}")
        traceback.print_exc()
        return f"Error performing search: {str(e)}"

async def analyze_sources(claim: str, search_results: str) -> str:
    """Uses Gemini 2.0 Flash to analyze gathered sources and determine the truthfulness of a claim."""
    try:
        current_time = datetime.now().strftime("%B %d, %Y")
        
        # Enhanced prompt for better analysis with Gemini 2.0 Flash
        prompt = (
            f"Current Date: {current_time}\n\n"
            f"Review these source contents regarding the following claim and provide a clear analysis.\n\n"
            f"CLAIM: {claim}\n\n"
            f"SOURCE CONTENTS:\n{search_results}\n\n"
            f"INSTRUCTIONS:\n"
            f"1. Carefully analyze what each source says about the specific claim\n"
            f"2. Look for concrete evidence, numbers, and verifiable facts\n"
            f"3. Compare information across sources\n"
            f"4. Consider the reliability and recency of sources\n"
            f"5. Based SOLELY on the available source content, provide a clear verdict\n"
            f"6. If sources are dated before {current_time}, consider if information might be outdated\n"
            f"7. Identify any conflicting information between sources\n"
            f"8. Pay special attention to any RHETORIC ISSUES mentioned with sources\n"
            f"9. Sources can present accurate facts despite emotional language\n"
            f"10. Be especially skeptical when the ONLY supporting evidence comes from sources with rhetoric issues\n\n"
            f"FORMAT YOUR RESPONSE AS:\n"
            f"VERDICT: Choose ONE of these options based on the evidence:\n"
            f"- CONFIRMED (when multiple reliable sources clearly support the claim)\n"
            f"- FALSE (when multiple reliable sources clearly contradict the claim)\n"
            f"- PARTIALLY TRUE (when some aspects are true but others are not)\n"
            f"- UNVERIFIABLE (ONLY if sources don't provide enough evidence)\n\n"
            f"EVIDENCE:\n[20-30 words as a list of specific facts, numbers, and quotes from sources that support your verdict]\n\n"
            f"SOURCE SUMMARY:\n[20 word summary of what each source says]\n\n"
            f"RHETORIC ASSESSMENT: [Briefly note if any sources show evidence of problematic language that affects reliability]\n\n"
            f"CONCLUSION:\n[2-3 sentence final assessment that clearly explains your verdict]\n\n"
            f"Be decisive when evidence is clear. Choose UNVERIFIABLE only as a last resort when sources truly don't address the claim."
        )

        logger.info("Requesting Gemini 2.0 Flash analysis...")
        
        # Using rate limiter with Gemini API
        async with gemini_limiter:
            response = await asyncio.to_thread(
                lambda: gemini_text_model.generate_content(prompt)
            )

        # Check if we got a valid response
        if not response or not hasattr(response, 'text'):
            logger.error("Invalid response from Gemini API")
            return "⚠️ Unable to analyze sources due to an API error."

        # Format the response with emoji for better readability
        formatted_response = response.text.strip()
        
        # Add verdict highlighting with emojis
        if "VERDICT: CONFIRMED" in formatted_response:
            formatted_response = formatted_response.replace(
                "VERDICT: CONFIRMED", 
                "✅ VERDICT: CONFIRMED"
            )
        elif "VERDICT: FALSE" in formatted_response:
            formatted_response = formatted_response.replace(
                "VERDICT: FALSE", 
                "❌ VERDICT: FALSE"
            )
        elif "VERDICT: PARTIALLY TRUE" in formatted_response:
            formatted_response = formatted_response.replace(
                "VERDICT: PARTIALLY TRUE", 
                "⚠️ VERDICT: PARTIALLY TRUE"
            )
        elif "VERDICT: UNVERIFIABLE" in formatted_response:
            formatted_response = formatted_response.replace(
                "VERDICT: UNVERIFIABLE", 
                "❓ VERDICT: UNVERIFIABLE"
            )
        
        formatted_response = formatted_response.replace("EVIDENCE:", "📊 EVIDENCE:")
        formatted_response = formatted_response.replace("SOURCE SUMMARY:", "📚 SOURCE SUMMARY:")
        formatted_response = formatted_response.replace("CONCLUSION:", "📝 CONCLUSION:")
        
        return f"📊 **Fact Check Analysis:**\n\n{formatted_response}"
    except Exception as e:
        logger.error(f"Error in analysis: {e}")
        traceback.print_exc()
        return f"❌ Error analyzing sources: {str(e)}. Please try again later."

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles URL submissions for fact-checking."""
    try:
        url = update.message.text
        await update.message.reply_text(f"🔗 Processing URL: {url}\nExtracting content...")
        
        text_content = await scrape_webpage(url)
        if not text_content:
            await update.message.reply_text("⚠️ Could not extract content from this URL.")
            return
            
        await update.message.reply_text(f"📄 Content extracted. Now checking for accuracy...")
        await handle_message(update, context, text_content[:1000])
    except Exception as e:
        logger.error(f"Error handling URL: {e}")
        await update.message.reply_text(f"❌ Error processing URL: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, claim: str = None):
    """Handles user text messages for fact-checking."""
    try:
        if not claim:
            claim = update.message.text
            
        # Check if it's a URL and handle accordingly
        if claim.startswith(("http://", "https://")) and "://" in claim:
            await handle_url(update, context)
            return

        progress_message = await update.message.reply_text("🔍 Gathering information from sources... Please wait.")

        search_results = await get_search_results(claim)
        
        # Update progress message
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=progress_message.message_id,
            text="📊 Analyzing sources and determining truthfulness..."
        )
        
        analysis = await analyze_sources(claim, search_results)
        
        # Delete progress message and send final analysis
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=progress_message.message_id
        )
        
        await update.message.reply_text(analysis)

    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        traceback.print_exc()
        await update.message.reply_text(f"❌ Sorry, I encountered an error: {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /start command."""
    user_id = update.effective_user.id
    
    # Reset user to normal mode
    if user_id in user_modes:
        del user_modes[user_id]
        
    await update.message.reply_text(
        "👋 Welcome to FactCheck Bot!\n\n"
        "I can help you verify news claims and information. Here's how to use me:\n"
        "- Send any news headline or claim to fact-check\n"
        "- Send an image containing text to extract and verify\n"
        "- Send a URL to analyze its content\n"
        "- Use /deepfake to enter deepfake detection mode\n"
        "- Use /help for more information"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /help command."""
    await update.message.reply_text(
        "📋 FactCheck Bot Help:\n\n"
        "1️⃣ Send any text claim or headline to verify\n"
        "2️⃣ Send an image containing text to extract and fact-check\n"
        "3️⃣ Send a URL to analyze its content\n\n"
        "💡 Special modes:\n"
        "• /deepfake - Enter deepfake detection mode (all images will be analyzed for manipulation)\n"
        "• /normal - Return to standard fact-checking mode\n\n"
        "I'll search for reliable sources and analyze the claim's accuracy."
    )

async def analyze_deepfake(image_path):
    """Analyzes an image for signs of deepfake manipulation using Gemini 1.5 Flash."""
    try:
        # Prepare the image for Gemini
        sample_file = await prep_image(image_path)
        
        # Deepfake detection prompt
        prompt = (
            "Analyze this image carefully for signs of manipulation, AI generation, or deepfake indicators. "
            "Look closely for these telltale signs: "
            "1. Unnatural facial features (eyes, teeth, ears) "
            "2. Inconsistent lighting or shadows "
            "3. Blurry or warped backgrounds "
            "4. Artificial texture in skin or hair "
            "5. Misaligned facial features "
            "6. Unnatural color patterns "
            "7. Artifacts around face boundaries "
            "8. Inconsistent image quality across the image "
            "\n\n"
            "Provide your analysis with a rating from 1-10 on how likely this is to be a deepfake or AI-generated image, where:"
            "1-3: Likely authentic image "
            "4-6: Some suspicious elements but inconclusive "
            "7-10: Strong indicators of manipulation/generation "
            "\n\n"
            "Format your response like this: "
            "DEEPFAKE LIKELIHOOD: [1-10] "
            "EVIDENCE: [List the specific visual anomalies you observed] "
            "CONCLUSION: [2-3 sentence summary explaining your rating]"
        )
        
        # Use Gemini Vision for analysis
        async with gemini_limiter:
            response = await asyncio.to_thread(
                lambda: gemini_vision_model.generate_content([sample_file, prompt])
            )
            
        if response and hasattr(response, 'text'):
            result = response.text.strip()
            
            # Format the response with emojis
            if "DEEPFAKE LIKELIHOOD:" in result:
                # Try to extract the score
                import re
                match = re.search(r"DEEPFAKE LIKELIHOOD:\s*(\d+)", result)
                if match:
                    score = int(match.group(1))
                    emoji = "🟢" if score <= 3 else "🟠" if score <= 6 else "🔴"
                    result = result.replace("DEEPFAKE LIKELIHOOD:", f"{emoji} DEEPFAKE LIKELIHOOD:")
                    
            if "EVIDENCE:" in result:
                result = result.replace("EVIDENCE:", "🔍 EVIDENCE:")
                
            if "CONCLUSION:" in result:
                result = result.replace("CONCLUSION:", "📝 CONCLUSION:")
                
            return f"📊 **Deepfake Analysis:**\n\n{result}"
        else:
            return "⚠️ Unable to analyze the image. Please try again with a clearer image."
    except Exception as e:
        logger.error(f"Error analyzing deepfake: {e}")
        traceback.print_exc()
        return f"❌ Error analyzing image: {str(e)}. Please try again later."

async def deepfake_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /deepfake command - activates deepfake detection mode."""
    user_id = update.effective_user.id
    
    # Set user to deepfake mode
    user_modes[user_id] = "deepfake"
    
    await update.message.reply_text(
        "🔍 *DEEPFAKE DETECTION MODE ACTIVATED* 🔍\n\n"
        "Now send me any image, and I'll analyze it for signs of AI manipulation or generation.\n\n"
        "I'll look for:\n"
        "• Unnatural facial features\n"
        "• Inconsistent lighting\n"
        "• Blurry or warped areas\n"
        "• Other telltale signs of manipulation\n\n"
        "Use /normal to return to regular fact-checking mode."
    )
    
    # If image was included with command, analyze it
    if update.message.photo:
        await process_image_for_deepfake(update, context)

async def normal_mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Switches user back to normal fact-checking mode."""
    user_id = update.effective_user.id
    
    # Remove deepfake mode if it exists
    if user_id in user_modes:
        del user_modes[user_id]
    
    await update.message.reply_text(
        "✅ Returned to normal fact-checking mode.\n\n"
        "Send me any text, image, or URL to fact-check!"
    )

def main():
    """Main function to start the bot."""
    app = Application.builder().token(TELEGRAM_API_KEY).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("deepfake", deepfake_command))
    app.add_handler(CommandHandler("normal", normal_mode_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    logger.info("✅ Fact Checker Bot (Optimized) is running...")
    app.run_polling(drop_pending_updates=True)

if __name__=="__main__":
    main()
