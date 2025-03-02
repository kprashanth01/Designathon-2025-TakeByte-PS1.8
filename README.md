# Designathon-2025-TakeByte-PS1.8
````markdown
# Designathon 2025 - TakeByte PS1.8

## Description
The Designathon 2025 project is a fact-checking application that allows users to verify claims and information through a Telegram bot and a web interface. The application leverages various APIs and machine learning models to analyze claims and provide reliable information.

## Technologies Used

### Frontend (`ui-one`)
- **React**: A JavaScript library for building user interfaces.
- **TypeScript**: A superset of JavaScript that adds static types.
- **Vite**: A build tool for fast development and optimized production builds.
- **Tailwind CSS**: A utility-first CSS framework for styling.
- **Framer Motion**: A library for animations in React applications.
- **Lucide React**: An icon library for React.
- **Axios**: A promise-based HTTP client for making requests to APIs.

### Backend (`telegram-bot`)
- **Python**: The programming language used for the backend.
- **FastAPI**: A modern web framework for building APIs.
- **python-telegram-bot**: A library for building Telegram bots.
- **Requests**: A simple HTTP library for Python.
- **BeautifulSoup**: A library for parsing HTML and XML documents.
- **NLTK**: The Natural Language Toolkit for text processing.
- **Google APIs**: For accessing Google's Fact Check API and other services.

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

## Usage
- Access the frontend application in your browser at `http://localhost:3000`.
- Interact with the chat interface to verify claims.
- Use the Telegram bot by sending a message to the bot to analyze claims.

## Commands
- `/start`: Begin using the bot.
- `/help`: Show help information about how to use the bot.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Thanks to the contributors and libraries that made this project possible.
````
