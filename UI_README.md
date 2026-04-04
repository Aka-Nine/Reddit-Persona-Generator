# Web UI for Reddit Persona Generator

## Quick Start

1. **Install dependencies** (if Flask is not already installed):
   ```bash
   pip install flask flask-cors
   ```
   Or install all requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server**:
   ```bash
   python server.py
   ```

3. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

4. **Enter a Reddit username or profile URL** in the input field and click "Generate Persona"

## Features

- Simple, modern web interface
- Real-time persona generation
- Copy to clipboard functionality
- Error handling and loading indicators
- Responsive design

## API Endpoint

The backend also exposes a REST API endpoint:

**POST** `/analyze`
```json
{
  "profile_url": "username" or "https://www.reddit.com/user/username"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Persona generated successfully",
  "username": "username",
  "file_path": "output/username_persona.txt",
  "persona_content": "..."
}
```

