# MIRROR-X STUDY INTELLIGENCE SYSTEM

A web-based study tracking and analysis system that exposes self-deception patterns and provides brutal, data-driven feedback.

## Features

- **🏠 Dashboard**: Performance metrics, grades, and study summary
- **📝 Study Logging**: Track subjects, hours, and difficulty levels
- **📊 Data Analysis**: Interactive graphs and session tables
- **🪞 Mirror Report**: Brutal truth analysis and pattern detection
- **🤖 AI Chat**: Ask Mirror-X questions about your study habits
- **📈 Performance Grading**: A-F grades based on comprehensive metrics
- **🎨 Modern UI**: Clean dark theme with responsive design

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python run.py
```

Then open http://localhost:5000 in your browser.

## Web Application Structure

```
├── app.py              # Flask web application
├── run.py              # Application runner
├── templates/          # HTML templates
│   ├── index.html      # Dashboard page
│   ├── log.html        # Study logging page
│   ├── analysis.html   # Data analysis page
│   ├── mirror.html     # Mirror report page
│   └── chat.html       # AI chat interface
├── static/
│   └── style.css       # Application styles
├── data.py             # Data storage and retrieval
├── analysis.py         # Behavioral pattern detection
├── mirror.py           # Truth engine and adaptive feedback
└── visual.py           # Data visualization
```

## System Components

### Backend (Flask)
- **Data Management**: CSV-based storage with pandas
- **Analysis Engine**: Pattern detection and scoring algorithms
- **AI Chat**: Intelligent responses based on study data
- **Visualization**: Matplotlib graphs converted to web-friendly format

### Frontend (HTML/CSS/JS)
- **Responsive Design**: Works on desktop and mobile
- **Dark Theme**: Easy on the eyes for extended use
- **Interactive Elements**: Real-time chat and dynamic updates
- **Modern UI**: Clean, professional interface

## Scoring System

- **Reality Score**: How accurately you perceive your study habits
- **Discipline Score**: Consistency and streak maintenance
- **Avoidance Score**: Tendency to avoid difficult subjects/tasks

## Features Deep Dive

### 🏠 Dashboard
- Real-time performance metrics
- A-F grading system
- Study consistency tracking
- Current streak monitoring

### 📊 Analysis
- Subject distribution charts
- Daily study hour trends
- Detailed session history
- Interactive data visualization

### 🪞 Mirror Report
- Brutal truth statements
- Behavioral pattern detection
- Performance scoring breakdown
- Actionable insights

### 🤖 AI Chat
- Natural language interface
- Data-driven responses
- Personalized feedback
- Study habit analysis

## Warning

This system provides direct, unfiltered feedback. It's designed to expose self-deception, not provide comfort.

## Technology Stack

- **Backend**: Python, Flask, Pandas, Matplotlib
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: CSV (for simplicity)
- **Visualization**: Matplotlib with base64 encoding
