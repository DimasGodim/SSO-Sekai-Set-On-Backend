
<h1 align="center">Sekai Set On Backend 🌐</h1>
<p align="center">
    <b>EZ Integration with Japanese platforms (No more region lock!)</b><br>
    <i>FastAPI-based backend for authentication, news, train info, TTS, weather, and more.</i>
</p>

---

## 🚀 Project Overview

Sekai Set On Backend is a modern API server built with FastAPI, designed to provide seamless integration with Japanese services and platforms. It features user authentication, API key management, NHK news fetching, train station data, TTS (Text-to-Speech), and weather information. The backend supports both PostgreSQL and MongoDB, making it flexible for various deployment scenarios.

---

## 🛠️ Features

- **User Authentication**: Secure signup, login, and verification.
- **API Key Management**: Generate and manage API keys for users.
- **NHK News Fetcher**: Automatically fetches and stores the latest NHK news.
- **Train Station Info**: Query Japanese train stations by city or prefecture.
- **Text-to-Speech (TTS)**: Get character voices and styles.
- **Weather Service**: Access weather data for Japanese regions.
- **Flexible Database**: Supports both PostgreSQL (async) and MongoDB.
- **Scheduler**: Background job for periodic news updates.
- **CORS & Logging**: Secure and observable API.

---

## 📦 Project Structure

```
app/
    api/         # API routers for user, service, etc.
    middleware/  # Custom middlewares (logging, etc.)
    service/     # Service logic (NHK news, TTS, etc.)
    deps/        # Dependency modules
    schema/      # Request/response schemas

data/
    db/          # Database clients and models (SQL & Mongo)
    act/         # Data access logic (CRUD for SQL & Mongo)
    static/      # Static data (stations, characters, etc.)

migrations/    # Alembic migration scripts
env/           # Python virtual environment
plan/          # Project planning docs
```

---

## ⚡ Quickstart

### 1. Clone the Repository

```sh
git clone https://github.com/DimasGodim/SSO-Sekai-Set-On-Backend.git
cd SSO-Back-Refactor
```

### 2. Set Up Python Environment

```sh
python -m venv env
env\Scripts\activate
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your database and secret settings.

```sh
copy .env.example .env
# Edit .env with your own values
```

### 5. Start PostgreSQL with Docker

```sh
docker compose up
```

### 6. Run Database Migrations

```sh
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 7. Start the API Server

```sh
uvicorn index:app --reload
```

---

## 🧩 API Endpoints

- `/api/auth` - User authentication (signup, login, verification)
- `/api/user` - User management
- `/api/apikey` - API key management
- `/api/news` - NHK news service
- `/api/train` - Train station info
- `/api/tts` - Text-to-speech service
- `/api/weather` - Weather service

See the FastAPI docs for interactive API documentation at `http://localhost:8000/docs`.

---

## 📝 Migrations

To create and apply database migrations:

```sh
alembic revision --autogenerate -m "your message"
alembic upgrade head
```

---

## 🛡️ License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## 💡 Credits

Created by DimasGodim and contributors.  
Feel free to fork, contribute, and use for your own Japanese integration projects!
