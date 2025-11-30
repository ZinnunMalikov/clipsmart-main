# ClipSmart

**Smart clipboard processing with AI-powered classification and conversion**

ClipSmart is an intelligent clipboard monitoring system that automatically classifies and processes clipboard content using AI. It can detect math expressions, links, dates, addresses, and convert screenshots to LaTeX.

## Features

- **AI-Powered Classification**: Automatically detects content types (math, links, dates, addresses)
- **Math to LaTeX**: Convert math screenshots to LaTeX using AI
- **Google Maps Integration**: Process location and address data
- **Cloud Storage**: Store processed content to AWS S3
- **FastAPI Backend**: High-performance REST API
- **Cross-Platform**: Works on Windows, macOS, and Linux

*Note: Additional features like calendar integration and other content types are in progress.*

## Quick Start

### Option 1: Python Package Installation

```bash
# Clone the repository
git clone https://github.com/ZinnunMalikov/clipsmart.git
cd clipsmart

# Run installation script
./install.sh  # Linux/macOS
# or
install.bat   # Windows

# Start the server
uvicorn backend.processing.main:app --host 0.0.0.0 --port 8000
```

### Option 2: Docker Installation

```bash
# Build the Docker image
docker build -t clipsmart .

# Run the container
docker run -p 8000:8000 \
  -e GENAI_API_KEY=your-ai-api-key \
  -e AWS_ACCESS_KEY_ID=your-aws-key \
  -e AWS_SECRET_ACCESS_KEY=your-aws-secret \
  clipsmart
```

### Option 3: PyPI Installation (Coming Soon)

```bash
pip install clipsmart
clipsmart --serve
```

## Configuration

### Required Environment Variables

```bash
# AI API Key (for AI processing)
export GENAI_API_KEY="your-ai-api-key"

# AWS S3 Configuration (optional, for cloud storage)
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export S3_BUCKET_NAME="your-bucket-name"
export AWS_REGION="us-east-1"
```

### Get API Keys

1. **AI API**: Get your API key for AI processing
2. **AWS S3**: Create an AWS account and S3 bucket for storage (optional)

## API Usage

### Process Text
```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"text": "Solve for x: 2x + 5 = 15"}'
```

### Process Screenshot
```bash
curl -X POST "http://localhost:8000/process-image" \
  -H "Content-Type: application/json" \
  -d '{"image": "base64-encoded-image", "type": "math"}'
```

### Create Calendar Event
```bash
curl -X POST "http://localhost:8000/create-calendar-event" \
  -H "Content-Type: application/json" \
  -d '{"text": "Meeting tomorrow at 2 PM", "description": "Team standup"}'
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/ZinnunMalikov/clipsmart.git
cd clipsmart

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black backend/

# Type checking
mypy backend/
```

### Project Structure

```
clipsmart/
├── backend/
│   ├── processing/
│   │   ├── main.py              # FastAPI application
│   │   ├── classification/      # Content classification
│   │   ├── conversion/          # LaTeX conversion
│   │   └── s3_storage.py       # Cloud storage
│   └── app/                    # Java components
├── frontend/                    # Frontend (if applicable)
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Package configuration
├── Dockerfile                  # Docker configuration
└── README.md                   # This file
```

## Supported Content Types

- **Math**: LaTeX expressions, equations, formulas (Available)
- **Google Maps**: Location and address processing (Available)
- **Links**: URLs, web addresses (In Progress)
- **Dates**: Date/time expressions for calendar events (In Progress)

## Deployment Options

### 1. Local Development
```bash
uvicorn backend.processing.main:app --reload --port 8000
```

### 2. Production Server
```bash
uvicorn backend.processing.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Docker Compose
```yaml
version: '3.8'
services:
  clipsmart:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GENAI_API_KEY=${GENAI_API_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
```

### 4. Cloud Platforms
- **Heroku**: Use included `Dockerfile`
- **AWS ECS**: Container deployment
- **Google Cloud Run**: Serverless deployment
- **Railway**: One-click deployment

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `pytest`
5. Commit changes: `git commit -am 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Submit a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Documentation](https://github.com/ZinnunMalikov/clipsmart#readme)

