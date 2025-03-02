#  VerifiBot

A Telegram bot that verifies information accuracy and detects deepfakes using AI-powered analysis.
find it [here](https://t.me/fakealertbot)
## 🔍 Overview

FactCheck Bot helps fight misinformation by automatically analyzing claims against reliable sources, extracting text from images, and detecting manipulated media. It provides evidence-based verdicts on the truthfulness of claims and can identify signs of AI manipulation in images.

![FactCheck Bot Flow](https://media.discordapp.net/attachments/1277657282116845671/1345655546790809670/image.png?ex=67c556e3&is=67c40563&hm=9f63a217be124bafdf070b5039e80a7f40f8e0ea6dbbd61839a78988bbb3ef7d&=&format=webp&quality=lossless&width=625&height=728)

## ✨ Features

- **Text-based Fact-checking**: Verifies claims against multiple reliable sources
- **Image Text Extraction**: Pulls text from images for verification
- **Deepfake Detection**: Analyzes images for signs of AI manipulation
- **URL Analysis**: Processes web content for fact-checking
- **Rhetoric Detection**: Identifies problematic language in news sources
- **Progress Updates**: Provides real-time feedback during analysis

## 🤖 Commands

- `/start` - Initialize the bot in normal fact-checking mode
- `/help` - Display usage instructions
- `/deepfake` - Enter deepfake detection mode
- `/normal` - Return to standard fact-checking mode

## 🔄 Workflow

### Normal Mode
1. **Send text, image, or URL**
2. Bot gathers information from authoritative sources
3. Content is analyzed for truthfulness and rhetoric
4. A clear verdict is provided with supporting evidence

### Deepfake Mode
1. **Send an image**
2. Bot analyzes visual anomalies and inconsistencies
3. A deepfake likelihood score (1-10) is provided with evidence
4. A detailed explanation of suspicious elements is returned

## 🔧 Setup

### Prerequisites
- Python 3.8+
- Google API keys (Gemini API and Custom Search API)
- Telegram Bot API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/factcheck-bot.git
   cd factcheck-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```
   TELEGRAM_API_KEY=your_telegram_bot_token
   GEMINI_API_KEY=your_gemini_api_key
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_CSE_ID=your_custom_search_engine_id
   ```

4. **Run the bot**
   ```bash
   python bot7.py
   ```

## 🛠️ Architecture

- **Google Gemini 1.5 Flash**: Handles image analysis and text extraction
- **Google Gemini 2.0 Flash**: Performs fact analysis and reasoning
- **Google Custom Search**: Retrieves authoritative sources
- **Parallel Processing**: Handles multiple sources simultaneously
- **Mode-based Processing**: Routes requests based on user's active mode

## 📋 Example Usage

### Fact-checking a claim
Send: `The Earth is flat`

Response:
```
📊 Fact Check Analysis:

❌ VERDICT: FALSE

📊 EVIDENCE: Multiple sources confirm Earth is an oblate spheroid. NASA, scientific organizations, and physics principles all validate Earth's roundness. Photographs from space show curved horizon.

📚 SOURCE SUMMARY:
Source 1: Earth is an oblate spheroid proven by scientific observation and physics.
Source 2: Visual evidence from space confirms Earth's spherical shape.
Source 3: Ancient civilizations calculated Earth's roundness using shadows and measurements.

📝 CONCLUSION: The claim that "Earth is flat" is demonstrably false. Scientific consensus, observational evidence, and physics principles uniformly confirm Earth's spherical shape.
```

### Analyzing an image for deepfakes
Send: [Image] with `/deepfake` command

Response:
```
📊 Deepfake Analysis:

🟠 DEEPFAKE LIKELIHOOD: 6

🔍 EVIDENCE:
- Unnatural smoothness in skin texture
- Slight distortion around eye edges
- Inconsistent lighting between face and background
- Minor artifacts around hairline
- Unusual reflection patterns in the eyes

📝 CONCLUSION: The image shows some suspicious elements that suggest possible manipulation, particularly around facial features. While not definitively AI-generated, several inconsistencies raise concerns about its authenticity.
```


## 🙏 Acknowledgments

- Google Gemini API for advanced AI capabilities
- Python Telegram Bot library
- Trafilatura for web content extraction
