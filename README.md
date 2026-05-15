# AI Study Assistant with Digital Notebook (Flask + MongoDB)

This project is a full-stack study assistant platform.

- **Flask backend** with REST APIs
- **MongoDB** for persistence
- **Vanilla JS frontend** served as static files

---

## Key fix (Server error 500 on registration)
Registration (`POST /api/auth/register`) previously failed with **500** due to MongoDB index creation throwing:

> `pymongo.errors.OperationFailure: Index already exists with a different name ... IndexOptionsConflict`

The fix was to make index creation tolerant of existing/previously-created indexes by wrapping index creation in `try/except` inside:
- `backend/models/user.py`

After the fix, user registration succeeds with **HTTP 200**.

---

## Features

- **Authentication** (Register/Login) using JWT tokens
- **User profile**
- **Digital Notebook** (notes CRUD, subject/topic filtering)
- **Study Planner** (tasks, deadlines, status)
- **AI Assistant** (ask/summarize/quiz endpoints)
- **File support** (upload/list/download)

---

## Tech Stack

- Backend: **Python 3 + Flask + PyMongo + JWT**
- Frontend: **HTML/CSS/Vanilla JavaScript**
- Database: **MongoDB**

---

## Requirements

- Python 3.8+
- MongoDB (local or Atlas)
- OpenAI API key (for AI features)

---

## Setup

1) Create/activate virtual environment

```powershell
python -m venv .venv
.\venv\Scripts\Activate.ps1
```

2) Install backend dependencies

```powershell
pip install -r backend/requirements.txt
```

3) Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=super-secret
JWT_SECRET_KEY=super-secret-jwt
MONGO_URI=mongodb://localhost:27017/ai_study_assistant
OPENAI_API_KEY=sk-your-key
HOST=0.0.0.0
PORT=5000
```

4) Start MongoDB

```powershell
mongod
```

5) Start the server

```powershell
python backend/app.py
```

Backend runs on:

- `http://localhost:5000`

---

## API Endpoints (high level)

### Authentication
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET  /api/auth/profile`

### Notes
- `GET/POST /api/notes`
- `GET/PUT/DELETE /api/notes/<id>`
- `POST /api/notes/<id>/share`

### Tasks
- `GET/POST /api/tasks`
- `PUT/DELETE /api/tasks/<id>`

### AI
- `POST /api/ai/ask`
- `POST /api/ai/summarize`
- `POST /api/ai/quiz`

### Files
- `GET/POST /api/files`
- `DELETE /api/files/<file_id>`
- `GET /api/files/<file_id>/download`

---

## Testing the registration fix

```bash
curl -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"Password123!"}'
```

Expected:
- `success: true` and `data.user_id` in response

---

## License

MIT

