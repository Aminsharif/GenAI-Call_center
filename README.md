# AI-Powered Call Center Application

This is an open-source call center application that integrates Twilio for call handling and AI capabilities for conversation processing.

## Features

- Automated call handling with Twilio
- AI-powered conversation processing
- Speech-to-Text and Text-to-Speech capabilities
- Conversation history and analytics
- Real-time call monitoring

## Setup Instructions

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your credentials:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   ```
5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Project Structure

- `/app`: Main application code
  - `/api`: API endpoints
  - `/core`: Core business logic
  - `/models`: Database models
  - `/services`: External service integrations
  - `/utils`: Utility functions
- `/tests`: Test files
- `/docs`: Documentation

## Configuration

The application uses environment variables for configuration. Copy the `.env.example` file to `.env` and fill in your credentials.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 