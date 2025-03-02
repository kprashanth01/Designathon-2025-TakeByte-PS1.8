# Designathon 2025 - TakeByte PS1.8

## Description
The project is a fact-checking application that allows users to verify claims and information through a **Telegram bot** (refer telegram-bot folder) and a **web interface**. The application leverages various **APIs** and **machine learning models** to analyze claims and provide reliable information.

---

## Technologies Used

### Frontend (`ui-one`)
- **React** – A JavaScript library for building user interfaces.
- **TypeScript** – A superset of JavaScript that adds static types.
- **Vite** – A build tool for fast development and optimized production builds.
- **Tailwind CSS** – A utility-first CSS framework for styling.
- **Lucide React** – An icon library for React.
- **Axios** – A promise-based HTTP client for making API requests.

### Backend (`telegram-bot`)
- **Python** – The programming language used for the backend.
- **FastAPI** – A modern web framework for building APIs.
- **python-telegram-bot** – A library for building Telegram bots.
- **Requests** – A simple HTTP library for Python.
- **Trafilatura** – A library for scraping from given urls.
- **NLTK** – The Natural Language Toolkit for text processing.
- **Google APIs** – For accessing Google' apis and other services.

---

## Installation

### Frontend
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Designathon-2025-TakeByte-PS1.8.git
   cd Designathon-2025-TakeByte-PS1.8/ui-one
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

### Backend
1. Navigate to the backend directory:
   ```bash
   cd Designathon-2025-TakeByte-PS1.8/telegram-bot
   ```
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

---

## Usage
- Access the frontend application in your browser at:  
  **`http://localhost:3000`**
- Interact with the chat interface to verify claims.
- Use the Telegram bot by sending a message to the bot to analyze claims.

---

## Commands
- **`/start`** – Begin using the bot.
- **`/help`** – Show help information about how to use the bot.

---

## Contributing
Contributions are welcome! Feel free to:
- Open an **issue** for bug reports and feature suggestions.
- Submit a **pull request** for improvements.

---

## Acknowledgments
A big thanks to google's gemini api, trafilatura, google's custom search api and python-telegram-bot and  **open-source libraries** that made this project possible! 🚀
