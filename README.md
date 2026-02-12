# Workflow Builder Lite 🚀

A simple, powerful web application to build and execute 3-step text processing workflows using Groq's LLM API.

🌐 **Live Demo**: [workflow-builder-db32.onrender.com](https://workflow-builder-db32.onrender.com/)

> **Note**: The app is hosted on Render's free tier, so it may take ~30 seconds to wake up on first visit if it has been inactive.

## ✨ Features

- **3-Step Linear Workflows**: Chain actions like Clean, Summarize, Keypoints, Simplify, Analogy, Classify, and Tone Analysis.
- **Real-time Streaming**: See the output of each step as it's generated.
- **Run History**: Automatically saves your last 5 runs (with detailed logs).
- **Secure**: API Keys are entered in the browser and verified against Groq. They are *not* stored permanently on the server.
- **Simple UI**: Clean, responsive interface built with HTML/CSS and Vanilla JS.
- **Health Monitoring**: Status page to check backend and database health.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Frontend**: Jinja2 Templates, Vanilla JavaScript, CSS variables
- **LLM**: Groq API (Llama 3 models)

## 🚀 How to Run

The simplest way is to visit the **[Live Demo](https://workflow-builder-db32.onrender.com/)**. Enter your Groq API key when prompted, and start building workflows.

### Option 1: Local Development

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/alwaysvivek/workflow-builder.git
    cd workflow-builder
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the server**:
    ```bash
    uvicorn main:app --reload
    ```

4.  **Open the app**:
    Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Option 2: Docker 🐳

Run the application with a single command:

1.  **Build the image**:
    ```bash
    docker build -t workflow-builder .
    ```

2.  **Run the container**:
    ```bash
    docker run -p 8000:8000 workflow-builder
    ```

3.  Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

## ✅ Project Checklist (Goal Achievement)

- [x] Simple Home Page with Workflow Builder
- [x] Status Page (Health Monitoring)
- [x] Basic Input Handling (Empty/Invalid inputs)
- [x] Run History (Last 5 runs)
- [x] Deployment support (Dockerfile)
- [x] No API keys in code