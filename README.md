# 📚 Tutor Agent – Personalised AI Learning Assistant

An **AI-powered tutor agent** with mailbox support, designed to provide **real-time, personalised learning experiences**.
It adapts to each learner’s pace, asks **Socratic questions**, builds **custom curriculums**, and identifies **knowledge gaps** with quizzes and projects.

---

## ✨ Features

* 📝 **Curriculum Crafting** – Generates 4-week structured learning paths for any subject using the best free resources (articles, videos, simulations).
* ❓ **Socratic Questioning** – Encourages critical thinking by guiding learners with probing, step-by-step questions.
* 📊 **Knowledge Gap Analysis** – Creates targeted quizzes to test understanding and strengthen weak spots.
* 💻 **Practical Application** – Suggests hands-on projects to apply skills (coding, data analysis, research).
* 📬 **Mailbox-Enabled** – Fully compatible with **Agentverse UI**, enabling real-time chat interactions.

---

## ⚙️ Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/tutor-agent.git
cd tutor-agent
```

### 2️⃣ Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set Environment Variables

Create a `.env` file in the project root and add your **Gemini API key**:

```env
GOOGLE_API_KEY=your_api_key_here
```

---

## ▶️ Run the Tutor Agent

```bash
python3 tutor_agent.py
```

This will start your **Tutor Agent** with mailbox support. You can now connect to it via **Agentverse UI** for real-time tutoring.

---

## 📬 Message Models

* `CurriculumRequest(topic: str)` → Returns HTML curriculum plan.
* `SocraticRequest(concept: str)` → Returns JSON with guiding questions.
* `QuizRequest(topic: str)` → Returns JSON with multiple-choice questions.
* `ProjectRequest(topic: str)` → Returns HTML beginner-friendly project.
* `AIResponse(response: str)` → Standardised AI reply model.

---

## 🌍 Social Impact

Education should be **personal, interactive, and accessible to all**.
This agent leverages AI to help anyone—from students to professionals—learn faster, smarter, and more critically.

---

## 🛠️ Tech Stack

* **[uAgents](https://github.com/fetchai/uAgents)** – For agent communication & mailbox support
* **Google Gemini API** – For intelligent content generation
* **Python 3.10+** – Core language
* **dotenv** – Secure environment variables

---

## 🚀 Future Enhancements

* 🎧 Voice-based tutoring
* 📈 Learning analytics dashboard
* 🌐 Multi-language support
* 🔗 Integration with external LMS platforms
