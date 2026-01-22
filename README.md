# Al-Muwathiq (Shariah Compliance Assistant) 🕌

A Retrieval-Augmented Generation (RAG) chatbot that helps users navigate Shariah standards (BNM, AAOIFI) with **Visual Provenance**. It answers questions and highlights the *exact evidence* on the original PDF page.

![Visual Provenance Demo](frontend/public/demo-screenshot.png)

## 🌟 Key Features
*   **Pro-Level RAG**: Intelligent retrieval that skips cover pages to find deep content.
*   **Visual Provenance**: Generates a high-quality image of the PDF page with a **Yellow Highlight** on the exact quote used by the AI.
*   **AI-Directed Highlighting**: Uses Google Gemini to determining the exact citation coordinates.
*   **Premium UI**: Glassmorphism, smooth animations, and a clean "Islamic Fintech" aesthetic.

## 🛠️ Tech Stack
*   **Backend**: Django, LangChain, ChromaDB, PyMuPDF.
*   **Frontend**: Next.js, TailwindCSS, Lucide Icons.
*   **AI**: Google Gemini (via `langchain-google-genai`).

---

## 🚀 How to Run (For New Users)

If you have cloned this repo, follow these steps to set up your own instance.

### 1. Prerequisites
*   Python 3.10+
*   Node.js 18+
*   **Google Gemini API Key** (Get one [here](https://aistudio.google.com/app/apikey)).

### 2. Backend Setup
The backend handles the PDF processing and AI logic.

```bash
cd backend
python -m venv .venv
# Activate venv:
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

pip install -r requirements.txt
```

**Configure Environment:**
Create a `.env` file in the `backend/` folder:
```ini
GOOGLE_API_KEY=your_gemini_api_key_here
```

**Run Migrations & Server:**
```bash
python manage.py migrate
python manage.py runserver
```
*Backend is now running at `http://localhost:8000`*

### 3. Frontend Setup
The frontend is the chat interface.

```bash
cd frontend
npm install
npm run dev
```
*Frontend is now running at `http://localhost:3000`*

---

## 🧠 Knowledge Base & Data Strategy
**"The Factory vs. The Inventory"**

This repository provides the **Factory** (Code logic, RAG pipeline, AI Highlighting).
The **Inventory** (PDF Standards) is **not included** in this repo to respect copyright and file size limits.

### 1. Supported Standards
This bot has been architected to handle key policy documents from BNM and AAOIFI.
See the full manifest of tested standards here: [standards_list.md](standards_list.md).

### 2. How to Reproduce (Ingestion)
To build the "Brain" on your local machine:

1.  **Bring Your Own Data**: 
    *   Obtain the PDF files (e.g., *BNM Policy Document on Tawarruq*).
2.  **Upload to Engine**:
    *   Log in to the Admin Panel (`http://localhost:8000/admin`).
    *   Upload your PDFs to the `Source Documents` table.
3.  **Run Ingestion**:
    *   Select the documents in the list.
    *   Choose **"Ingest selected documents..."** from the Actions menu.
    *   *System will chunk text, generate embeddings via Gemini, and store them in the local `chroma_db` folder.*

⚠️ **Note**: The `chroma_db` folder and `media` files are explicitly git-ignored to keep the repo clean.

