import os
import traceback
from datetime import datetime
import asyncio
import httpx
import trafilatura
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from googleapiclient.discovery import build
from transformers import pipeline
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys  # Add this import at the top of your file

# Load environment variables
load_dotenv('.env')
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Initialize Gemini
genai_client = genai.Client(api_key=GEMINI_API_KEY)
genai_client.generation_config = genai.types.GenerationConfig(
    response_mime_type="text/plain"
)

# Initialize summarizer once at startup
try:
    print("Initializing text summarizer...")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=0 if torch.cuda.is_available() else -1)
except Exception as e:
    print(f"Error during initialization: {e}")
    sys.exit(1)  # Exit the program with a non-zero status code

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/analyze', methods=['POST'])
def analyze_claim():
    data = request.json
    claim = data.get('claim', '')
    # Ensure that the claim is not empty
    if not claim:
        return jsonify({'error': 'Claim is required'}), 400

    # Call your existing analysis functions here
    try:
        search_results = asyncio.run(get_search_results(claim))
        analysis = asyncio.run(analyze_sources(claim, search_results))
        return jsonify({'analysis': analysis})
    except Exception as e:
        print(f"Error during analysis: {e}")
        return jsonify({'error': 'An error occurred during analysis'}), 500

async def scrape_webpage(url: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            text = trafilatura.extract(response.text)
            
            if text:
                # Increased character limit to 4000
                return text[:4000] if len(text) > 4000 else text
            return ""
            
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

def chunk_text(text: str, max_chunk_size: int = 4000) -> list:
    """Split text into chunks of maximum size while preserving sentences"""
    chunks = []
    current_chunk = ""
    
    # Split by sentences (roughly)
    sentences = text.split('.')
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + '.'
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence + '.'
    
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def summarize_text(text: str, max_length: int = 1000) -> str:
    """Simple text summarization by keeping first part"""
    if len(text) <= max_length:
        return text
        
    # Find the last complete sentence within max_length
    truncated = text[:max_length]
    last_period = truncated.rfind('.')
    if last_period > 0:
        return truncated[:last_period + 1]
    return truncated

async def get_search_results(claim: str) -> str:
    try:
        print(f"\n=== Searching Google for: {claim} ===")
        all_results = "Source Content:\n\n"
        
        try:
            service = build(
                "customsearch", "v1",
                developerKey=GOOGLE_API_KEY
            )
            
            # Get search results
            search_results = service.cse().list(
                q=f"{claim}",  # Expanded search query
                cx=GOOGLE_CSE_ID,
                num=4,
                fields="items(title,link)"
            ).execute()
            
            if 'items' in search_results:
                urls = [item.get('link', '') for item in search_results['items']]
                
                print(f"Found {len(urls)} URLs to scrape:")
                for url in urls:
                    print(f"- {url}")
                
                # Scrape all URLs concurrently
                scraping_tasks = [scrape_webpage(url) for url in urls]
                contents = await asyncio.gather(*scraping_tasks, return_exceptions=True)
                
                successful_scrapes = 0
                for i, (item, content) in enumerate(zip(search_results['items'], contents), 1):
                    if isinstance(content, Exception) or not content:
                        print(f"Failed to scrape source {i}")
                        continue
                    
                    print(f"Successfully scraped source {i} with {len(content)} characters")
                    title = item.get('title', '').replace('\n', ' ')
                    source = item.get('link', '').split('//')[1].split('/')[0] if '//' in item.get('link', '') else item.get('link', '')
                    
                    all_results += f"\n=== Source {i}: [{source}] {title} ===\n"
                    all_results += f"{content}\n"
                    all_results += "\n---\n"
                    successful_scrapes += 1
            
            print(f"Successfully processed {successful_scrapes} sources")
            if successful_scrapes == 0:
                return "Error: Could not retrieve any valid content from sources."
                
            return all_results if len(all_results) > 30 else "No relevant content found."
            
        except Exception as e:
            print(f"Search error: {e}")
            traceback.print_exc()
            return f"Error performing search: {str(e)}"
        
    except Exception as e:
        print(f"Critical error in search: {e}")
        traceback.print_exc()
        return "Error gathering results."

async def analyze_sources(claim: str, search_results: str) -> str:
    try:
        current_time = datetime.now().strftime("%B %d, %Y")
        print(f"Starting source analysis for claim: {claim}")
        
        # Summarize if content is too large
        if len(search_results) > 4000:
            search_results = summarize_text(search_results, max_length=4000)
            print("Summarized search results for analysis")
        
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
            f"5. Based SOLELY on the available source content, provide a clear verdict\n\n"
            f"FORMAT YOUR RESPONSE AS:\n"
            f"VERDICT: Choose ONE of these options based on the evidence:\n"
            f"- CONFIRMED (when multiple reliable sources clearly support the claim)\n"
            f"- FALSE (when multiple reliable sources clearly contradict the claim)\n"
            f"- PARTIALLY TRUE (when some aspects are true but others are not)\n"
            f"- UNVERIFIABLE (ONLY if sources don't provide enough evidence)\n\n"
            f"EVIDENCE:\n[20-30 words as a list of specific facts, numbers, and quotes from sources that support your verdict]\n\n"
            f"SOURCE SUMMARY:\n[20 word summary of what each source says]\n\n"
            f"Be decisive when evidence is clear. Choose UNVERIFIABLE only as a last resort when sources truly don't address the claim."
        )
        
        print("Requesting Gemini analysis...")
        response = genai_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        if not response:
            return "Unable to analyze sources."

        analysis = response.text.strip()
        formatted_response = (
            "📊 SOURCE ANALYSIS:\n\n" +
            analysis.replace("VERDICT:", "📍 VERDICT:").
            replace("EVIDENCE:", "\n📚 EVIDENCE:").
            replace("SOURCE SUMMARY:", "\n📋 SOURCE SUMMARY:")
        )
        
        return formatted_response

    except Exception as e:
        print(f"Error in analysis: {e}")
        traceback.print_exc()
        return "Error analyzing sources."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        claim = update.message.text
        await update.message.reply_text("🔍 Gathering information from sources... Please wait.")

        search_results = await get_search_results(claim)
        analysis = await analyze_sources(claim, search_results)
        await update.message.reply_text(analysis)

    except Exception as e:
        print(f"Error in handle_message: {e}")
        traceback.print_exc()
        await update.message.reply_text("Sorry, I encountered an error while gathering information.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to the Fact Checker Bot! Send me a news headline or claim, "
        "and I'll verify its truthfulness using multiple sources and AI analysis."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "This bot helps you verify the truthfulness of news and claims.\n\n"
        "How to use:\n"
        "• Send any news headline, claim, or rumor\n"
        "• The bot will search reliable sources\n"
        "• You'll get an analysis based on available information\n\n"
        "Commands:\n"
        "/start - Begin using the bot\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_text)

def main():
    try:
        app = ApplicationBuilder().token(TELEGRAM_API_KEY).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        print("Fact Checker Bot is running...")
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"Bot error: {e}")

if __name__ == "__main__":
    app.run(port=5000)  # Ensure this port is not in use
