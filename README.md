# FastAPI Audio Transcription Backend

A simple backend API for audio transcription using FastAPI, AWS S3, and AssemblyAI.

## What it does

- Upload audio files (MP3, WAV, M4A)
- Transcribe audio with speaker diarization
- Sentiment analysis and summarization
- User authentication with JWT tokens
- Background processing with Celery

## Tech Stack

- **FastAPI** - Web framework
- **PostgreSQL** - Database
- **RabbitMQ** - Message queue
- **Celery** - Background tasks
- **AWS S3** - File storage
- **AssemblyAI** - Audio transcription

## Quick Setup

### 1. Prerequisites

- Python 3.11+
- Docker & Docker Compose
- AWS S3 account
- AssemblyAI account

### 2. Environment Setup

```bash
# Clone project
git clone <your-repo>
cd fastapi-audio-transcription

# Copy environment file
cp .env.example .env
```

### 3. Configure .env file

```env
# Database
POSTGRES_PASSWORD=postgres

# AWS S3 (required)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
S3_BUCKET_NAME=your-bucket-name

# AssemblyAI (required)
ASSEMBLYAI_API_KEY=your_assemblyai_key

# JWT Secret (change this!)
SECRET_KEY=your-secret-key
```

### 4. Start Services

```bash
# Start all services
docker-compose up -d

# Check if running
curl http://localhost:8000/health
```

### 5. Setup Database

```bash
# Run database migrations
docker-compose exec web alembic upgrade head
```

## API Usage

### Register User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "password123"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### Upload Audio

```bash
curl -X POST "http://localhost:8000/api/v1/transcriptions/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@audio.mp3"
```

### Check Job Status

```bash
curl -X GET "http://localhost:8000/api/v1/transcriptions/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login user |
| POST | `/api/v1/transcriptions/upload` | Upload audio file |
| GET | `/api/v1/transcriptions/{id}` | Get transcription status |
| GET | `/api/v1/transcriptions/` | List user's jobs |

## Development

### Run locally (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Start database services
docker-compose up -d postgres redis rabbitmq

# Run API
uvicorn app.main:app --reload

# Run worker (separate terminal)
celery -A app.core.celery_app worker --loglevel=info
```

### View logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f celery-worker
```

## Monitoring

- **API Docs**: http://localhost:8000/docs
- **RabbitMQ**: http://localhost:15672 (guest/guest)
- **Celery Monitor**: http://localhost:5555

## Troubleshooting

### Common Issues

**API won't start**: Check if all required environment variables are set

**Database connection error**: Make sure PostgreSQL is running
```bash
docker-compose up -d postgres
```

**Transcription fails**: Verify AssemblyAI API key and S3 credentials

**Worker not processing**: Check RabbitMQ connection
```bash
docker-compose logs rabbitmq
```

## File Upload Limits

- **Max file size**: 100MB
- **Supported formats**: MP3, WAV, M4A, OGG
- **Processing time**: Usually 1-5 minutes depending on file length

## Project Structure

```
app/
├── main.py              # FastAPI app
├── core/               # Config, database, security
├── models/             # SQLAlchemy models  
├── schemas/            # Pydantic schemas
├── api/v1/endpoints/   # API routes
├── services/           # S3, AssemblyAI services
└── workers/            # Celery tasks
```

## License

MIT License