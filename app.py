from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, make_response
import pandas as pd
import json
import os
from datetime import datetime, timedelta, date
from database import init_database, create_user, authenticate_user, save_study_session, get_user_study_sessions, save_score_history, get_user_score_history, get_leaderboard_data, update_user_scores, get_user_streak, update_streak
from auth import login_required, get_current_user, is_logged_in

app = Flask(__name__)
app.secret_key = 'mirror-x-secret-key-change-in-production'

# Initialize database
init_database()

# Import existing modules
from data import get_available_subjects
from analysis import analyze_study_data, detect_behavioral_patterns, get_recent_data, calculate_streak

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

def mirror_chat(df, user_input):
    """AI chat function that provides honest, strategic advice"""
    if df.empty:
        return "No study data available. Log some sessions first."
    
    # Analyze user data
    result = analyze_behavior(df)
    patterns = result['patterns']
    scores = result['scores']
    hidden_patterns = result.get('hidden_patterns', [])
    
    # Process user input
    user_input_lower = user_input.lower().strip()
    
    # Direct questions about what to do today
    if 'what should i do today' in user_input_lower or 'today' in user_input_lower:
        return generate_daily_plan(df, patterns, scores)
    
    # Questions about failing
    if 'why am i failing' in user_input_lower or 'failing' in user_input_lower or 'fail' in user_input_lower:
        return generate_failure_analysis(df, patterns, scores, hidden_patterns)
    
    # General study advice
    if 'study' in user_input_lower or 'improve' in user_input_lower or 'better' in user_input_lower:
        return generate_study_advice(df, patterns, scores)
    
    # Pattern questions
    if 'pattern' in user_input_lower:
        return generate_pattern_analysis(patterns, hidden_patterns)
    
    # Score questions
    if 'score' in user_input_lower or 'grades' in user_input_lower:
        return generate_score_analysis(scores)
    
    # Default response
    return generate_general_advice(df, patterns, scores)

def generate_daily_plan(df, patterns, scores):
    """Generate specific daily plan"""
    total_hours = df['hours'].sum()
    avg_hours = total_hours / len(df) if len(df) > 0 else 0
    
    if avg_hours < 2:
        return "You need to study at least 2 hours today. Start with your weakest subject for 30 minutes, then move to your strength. No excuses."
    
    if scores['reality_score'] < 40:
        return f"Your reality score is {scores['reality_score']}. Stop lying to yourself. Study {avg_hours:.1f} hours today with your hardest subject first."
    
    # Check for patterns
    if 'over_focus_easy' in patterns:
        return "You're hiding in easy subjects again. Today you study one hard subject (2 hours minimum) and two medium subjects. Your discipline score shows this weakness."
    
    if 'irregular_study' in patterns:
        return "Your consistency is terrible. Study at the same time every day for 7 days straight. No more random schedules."
    
    return f"Based on your data, study {avg_hours:.1f} hours today. Focus on quality over quantity. Your discipline score of {scores['discipline_score']} needs work."

def generate_failure_analysis(df, patterns, scores, hidden_patterns):
    """Analyze why user is failing"""
    total_hours = df['hours'].sum()
    consistency_score = scores.get('consistency', 0)
    
    issues = []
    
    if total_hours < 10:
        issues.append(f"Only {total_hours:.1f} total hours. That's not studying, that's dabbling.")
    
    if consistency_score < 30:
        issues.append(f"Consistency at {consistency_score:.1f}% is pathetic. Success requires showing up daily.")
    
    if scores['avoidance_score'] > 70:
        issues.append(f"Avoidance score of {scores['avoidance_score']} means you run from challenges. Growth happens outside your comfort zone.")
    
    if 'fake_productivity' in [p.get('pattern', '') for p in hidden_patterns]:
        issues.append("You log many short sessions to feel productive. That's self-sabotage.")
    
    if not issues:
        return "You're not actually failing. You're just being lazy and looking for excuses. Take ownership of your mediocrity."
    
    return " | ".join(issues) + " Fix these issues or accept being average."

def generate_study_advice(df, patterns, scores):
    """Generate strategic study advice"""
    if scores['discipline_score'] < 50:
        return "Your discipline is your biggest weakness. Study at the same time every day for 21 days straight. Discipline beats talent every time."
    
    if 'subject_neglect_cycle' in [p.get('pattern', '') for p in patterns]:
        return "You keep abandoning subjects after short bursts. Pick one subject and master it for 30 days before switching."
    
    avg_session_length = df['hours'].mean()
    if avg_session_length < 1.5:
        return "Your sessions are too short. You need at least 90-minute focused sessions. Short sessions waste time on context switching."
    
    return "Focus on depth over breadth. One 3-hour focused session beats three 1-hour superficial sessions every time."

def generate_pattern_analysis(patterns, hidden_patterns):
    """Analyze user's patterns"""
    if not patterns and not hidden_patterns:
        return "No significant patterns detected. Keep studying consistently."
    
    pattern_list = []
    
    if 'over_focus_easy' in patterns:
        pattern_list.append("You consistently choose easy subjects to feel productive. This is preventing real growth.")
    
    if 'irregular_study' in patterns:
        pattern_list.append("Your study schedule is chaotic. Random sessions prevent knowledge retention.")
    
    if hidden_patterns:
        for pattern in hidden_patterns:
            if pattern['pattern'] == 'spike_then_crash':
                pattern_list.append(f"You study intensely then disappear. This indicates burnout, not productivity.")
            elif pattern['pattern'] == 'fake_productivity':
                pattern_list.append(f"You log {pattern['session_count']} short sessions to feel busy. This is fake productivity.")
            elif pattern['pattern'] == 'subject_neglect_cycle':
                pattern_list.append(f"You abandon subjects after short obsession. This shows lack of long-term commitment.")
    
    return " | ".join(pattern_list) if pattern_list else "Keep studying consistently and avoid these patterns."

def generate_score_analysis(scores):
    """Analyze user's scores"""
    reality = scores['reality_score']
    discipline = scores['discipline_score']
    avoidance = scores['avoidance_score']
    
    if reality < 30:
        return f"Your reality score is {reality}. You're delusional about your abilities. Start with subjects you actually struggle with."
    
    if discipline < 40:
        return f"Discipline score of {discipline} is embarrassing. Success requires daily effort, not occasional motivation."
    
    if avoidance > 60:
        return f"Avoidance score of {avoidance} means you're running from challenges. Growth happens when you're uncomfortable."
    
    highest = max(reality, discipline, 100 - avoidance)
    if highest == reality:
        return f"Your reality score ({reality}) is your strength. Build on it by studying more challenging material."
    
    return f"Your scores show reality: {reality}, discipline: {discipline}, avoidance: {avoidance}. Focus on improving your lowest score."

def generate_general_advice(df, patterns, scores):
    """Generate general strategic advice"""
    total_sessions = len(df)
    
    if total_sessions < 5:
        return "You need more data. Log at least 10 sessions before asking for meaningful analysis."
    
    if scores['reality_score'] > 80 and scores['discipline_score'] > 80:
        return "Your metrics are strong. Maintain consistency and gradually increase difficulty. Don't get complacent."
    
    if 'weekend_warrior' in patterns:
        return "Your weekend studying is good, but your weekday consistency is weak. Balance your schedule across the week."
    
    return "Based on your data, focus on consistent daily study sessions with increasing difficulty. Quality over quantity."

def analyze_behavior(df):
    """Analyze user behavior and detect patterns"""
    if df.empty:
        return {
            'patterns': [],
            'truth_statements': [],
            'scores': {'reality_score': 0, 'discipline_score': 0, 'avoidance_score': 0},
            'analysis': {'total_hours': 0, 'total_sessions': 0, 'consistency': 0, 'current_streak': 0},
            'hidden_patterns': []
        }
    
    # Calculate basic metrics
    total_hours = df['hours'].sum()
    total_sessions = len(df)
    
    # Calculate consistency (study days vs total days)
    df['date'] = pd.to_datetime(df['date']).dt.date
    study_days = len(df['date'].unique())
    date_range = (df['date'].max() - df['date'].min()).days + 1
    consistency = (study_days / date_range) * 100 if date_range > 0 else 0
    
    # Calculate streak
    df_sorted = df.sort_values('date')
    current_streak = calculate_current_streak(df_sorted)
    
    # Detect behavioral patterns
    patterns = detect_behavioral_patterns(df)
    
    # Detect hidden patterns
    hidden_patterns = detect_hidden_patterns(df)
    
    # Generate truth statements
    truth_statements = generate_truth_statements(df, patterns, hidden_patterns)
    
    # Calculate scores
    scores = calculate_behavior_scores(df, patterns, hidden_patterns)
    
    return {
        'patterns': patterns,
        'truth_statements': truth_statements,
        'scores': scores,
        'analysis': {
            'total_hours': total_hours,
            'total_sessions': total_sessions,
            'consistency': consistency,
            'current_streak': current_streak,
            'hidden_patterns': hidden_patterns
        }
    }

def detect_hidden_patterns(df):
    """Detect hidden negative patterns in study behavior"""
    hidden_patterns = []
    
    if df.empty:
        return hidden_patterns
    
    # Spike then crash pattern
    spike_then_crash = detect_spike_crash_pattern(df)
    if spike_then_crash:
        hidden_patterns.append(spike_then_crash)
    
    # Fake productivity pattern
    fake_productivity = detect_fake_productivity_pattern(df)
    if fake_productivity:
        hidden_patterns.append(fake_productivity)
    
    # Subject neglect cycles
    neglect_cycles = detect_subject_neglect_cycles(df)
    if neglect_cycles:
        hidden_patterns.append(neglect_cycles)
    
    # Last-minute bursts
    last_minute = detect_last_minute_bursts(df)
    if last_minute:
        hidden_patterns.append(last_minute)
    
    return hidden_patterns

def detect_spike_crash_pattern(df):
    """Detect spike then crash pattern"""
    if len(df) < 7:
        return None
    
    # Calculate daily hours
    df['date'] = pd.to_datetime(df['date']).dt.date
    daily_hours = df.groupby('date')['hours'].sum().reset_index()
    
    # Look for spike (high hours) followed by crash (zero hours)
    for i in range(len(daily_hours) - 2):
        current_day = daily_hours.iloc[i]
        next_day = daily_hours.iloc[i + 1] if i + 1 < len(daily_hours) else None
        
        if (current_day['hours'] > 6 and 
            next_day and next_day['hours'] < 1):
            return {
                'pattern': 'spike_then_crash',
                'description': 'You study 8+ hours one day, then disappear completely the next.',
                'severity': 'high',
                'days': [current_day['date'].strftime('%Y-%m-%d'), next_day['date'].strftime('%Y-%m-%d')],
                'hours': [current_day['hours'], next_day['hours']]
            }
    
    return None

def detect_fake_productivity_pattern(df):
    """Detect fake productivity pattern (many sessions, low hours)"""
    if len(df) < 10:
        return None
    
    # Check for many sessions with very low hours
    avg_session_length = df['hours'].mean()
    session_count = len(df)
    
    if (session_count > 15 and avg_session_length < 1.0):
        return {
            'pattern': 'fake_productivity',
            'description': f'You log {session_count} sessions but only average {avg_session_length:.1f} hours each. That\'s not studying, that\'s pretending.',
            'severity': 'medium',
            'session_count': session_count,
            'avg_hours': avg_session_length
        }
    
    return None

def detect_subject_neglect_cycles(df):
    """Detect subject neglect cycles"""
    if len(df) < 14:
        return None
    
    # Group by week to see cycles
    df['week'] = pd.to_datetime(df['date']).dt.isocalendar().week
    weekly_subjects = df.groupby('week')['subject'].apply(list).reset_index()
    
    # Look for neglect cycles (focusing on one subject, then switching)
    neglect_cycles = []
    
    for i in range(len(weekly_subjects) - 3):
        week_subjects = weekly_subjects.iloc[i]['subject']
        
        # Check if dominated by one subject (>60% of sessions)
        subject_counts = pd.Series(week_subjects).value_counts()
        if len(subject_counts) == 1:
            dominant_subject = subject_counts.index[0]
            dominant_percentage = (subject_counts[dominant_subject] / len(week_subjects)) * 100
            
            if dominant_percentage > 60:
                # Check next weeks for pattern
                next_week = weekly_subjects.iloc[i + 1]['subject'] if i + 1 < len(weekly_subjects) else []
                if next_week and dominant_subject not in next_week:
                    neglect_cycles.append({
                        'pattern': 'subject_neglect_cycle',
                        'description': f'You obsessed over {dominant_subject} for a week, then completely abandoned it.',
                        'severity': 'high',
                        'weeks': [i + 1, i + 2],
                        'neglected_subject': dominant_subject,
                        'new_subjects': next_week[:3] if next_week else []
                    })
    
    return neglect_cycles[0] if neglect_cycles else None

def detect_last_minute_bursts(df):
    """Detect last-minute study bursts"""
    if len(df) < 7:
        return None
    
    # Check for sessions clustered around deadlines
    df['datetime'] = pd.to_datetime(df['date'])
    df['hour'] = df['datetime'].dt.hour
    
    # Look for late night sessions (after 10 PM)
    late_night_sessions = df[df['hour'] >= 22]
    
    if len(late_night_sessions) > len(df) * 0.4:
        return {
            'pattern': 'last_minute_bursts',
            'description': f'{len(late_night_sessions)} out of {len(df)} sessions are after 10 PM. You only study when panic hits.',
            'severity': 'medium',
            'burst_sessions': len(late_night_sessions),
            'total_sessions': len(df)
        }
    
    return None

def generate_truth_statements(df, patterns, hidden_patterns):
    """Generate harsh truth statements based on patterns"""
    truths = []
    
    for pattern in hidden_patterns:
        if pattern['pattern'] == 'spike_then_crash':
            truths.append(f"You think {pattern['hours'][0]} hours of work makes you a genius, then {pattern['hours'][1]} hours the next day makes you lazy.")
        
        elif pattern['pattern'] == 'fake_productivity':
            truths.append(f"Logging {pattern['session_count']} sessions with {pattern['avg_hours']:.1f} hours each is pathetic. You're fooling yourself, not your grades.")
        
        elif pattern['pattern'] == 'subject_neglect_cycle':
            truths.append(f"You abandoned {pattern['neglected_subject']} for {pattern['new_subjects'][0] if pattern['new_subjects'] else 'anything new'}. Your attention span is that of a goldfish.")
        
        elif pattern['pattern'] == 'last_minute_bursts':
            truths.append(f"{pattern['burst_sessions']} panic sessions prove you only care about grades, not learning. Cramming isn't studying.")
    
    return truths

def calculate_behavior_scores(df, patterns, hidden_patterns):
    """Calculate behavior scores based on patterns"""
    base_reality = 50
    base_discipline = 50
    base_avoidance = 50
    
    # Adjust scores based on hidden patterns
    for pattern in hidden_patterns:
        if pattern['severity'] == 'high':
            base_reality -= 15
            base_discipline -= 15
            base_avoidance += 20
        elif pattern['severity'] == 'medium':
            base_reality -= 8
            base_discipline -= 8
            base_avoidance += 10
    
    # Ensure scores stay in valid range
    reality_score = max(0, min(100, base_reality))
    discipline_score = max(0, min(100, base_discipline))
    avoidance_score = max(0, min(100, base_avoidance))
    
    return {
        'reality_score': reality_score,
        'discipline_score': discipline_score,
        'avoidance_score': avoidance_score
    }
from visual import plot_subject_distribution, plot_daily_hours
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

@app.route('/')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    current_user = get_current_user()
    sessions_data = get_user_study_sessions(current_user['id'])
    
    if not sessions_data:
        return render_template('index.html', has_data=False, user=current_user, streak_data={'current_streak': 0, 'longest_streak': 0}, failure_alert=None, top_one_percent=False)
    
    df = pd.DataFrame(sessions_data)
    result = analyze_behavior(df)
    scores = result['scores']
    analysis = result['analysis']
    
    # Save score history
    save_score_history(current_user['id'], scores['reality_score'], scores['discipline_score'], scores['avoidance_score'])
    
    # Get streak data
    streak_data = get_user_streak(current_user['id'])
    
    # Check for failure alerts
    failure_alert = check_failure_alerts(analysis, streak_data)
    
    # Check if streak was broken (no study today)
    today = datetime.now().strftime('%Y-%m-%d')
    studied_today = any(session['date'] == today for session in sessions_data)
    
    if not studied_today and streak_data['current_streak'] > 0:
        update_streak(current_user['id'], False)
        flash('You broke your streak. That\'s exactly why you\'re average.', 'warning')
    
    # Check for top 1% mode
    top_one_percent = check_top_one_percent(scores, analysis)
    
    # Calculate performance grade
    avg_score = (scores['reality_score'] + scores['discipline_score'] + (100 - scores['avoidance_score'])) / 3
    if avg_score >= 85:
        grade, grade_text = "A", "EXCELLENT"
    elif avg_score >= 70:
        grade, grade_text = "B", "GOOD"
    elif avg_score >= 55:
        grade, grade_text = "C", "AVERAGE"
    elif avg_score >= 40:
        grade, grade_text = "D", "POOR"
    else:
        grade, grade_text = "F", "CRITICAL"
    
    # Show streak motivation
    if streak_data['current_streak'] >= 7:
        flash('You\'re building momentum. Don\'t ruin it.', 'info')
    
    return render_template('index.html', 
                         has_data=True,
                         total_hours=analysis.get('total_hours', 0),
                         reality_score=scores['reality_score'],
                         discipline_score=scores['discipline_score'],
                         avoidance_score=scores['avoidance_score'],
                         grade=grade,
                         grade_text=grade_text,
                         consistency=analysis.get('consistency', 0),
                         current_streak=streak_data['current_streak'],
                         longest_streak=streak_data['longest_streak'],
                         total_sessions=analysis.get('total_sessions', 0),
                         user=current_user,
                         streak_data=streak_data,
                         failure_alert=failure_alert,
                         top_one_percent=top_one_percent)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('signup.html')
        
        if create_user(username, email, password):
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username or email already exists.', 'error')
            return render_template('signup.html')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = authenticate_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Welcome back!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

def check_top_one_percent(scores, analysis):
    """Check if user qualifies for top 1% mode"""
    discipline_score = scores.get('discipline_score', 0)
    consistency_score = analysis.get('consistency', 0)
    total_hours = analysis.get('total_hours', 0)
    
    # Top 1% requirements
    if discipline_score > 80 and consistency_score > 75 and total_hours > 20:
        return True
    
    return False
    """Check for failure conditions and generate alerts"""
    alerts = []
    risk_level = "LOW"
    
    # Check consistency
    consistency = analysis.get('consistency', 0)
    if consistency < 30:
        alerts.append("Low consistency detected")
        risk_level = "HIGH"
    elif consistency < 50:
        alerts.append("Consistency needs improvement")
        if risk_level != "HIGH":
            risk_level = "MEDIUM"
    
    # Check avoidance
    if 'avoidance_score' in analysis:
        avoidance_score = analysis['avoidance_score']
        if avoidance_score > 70:
            alerts.append("High avoidance behavior")
            risk_level = "HIGH"
        elif avoidance_score > 50:
            alerts.append("Moderate avoidance patterns")
            if risk_level != "HIGH":
                risk_level = "MEDIUM"
    
    # Check total hours
    total_hours = analysis.get('total_hours', 0)
    if total_hours < 5:
        alerts.append("Low total study hours")
        if risk_level != "HIGH":
            risk_level = "MEDIUM"
    elif total_hours < 10:
        alerts.append("Insufficient study time")
        if risk_level != "HIGH":
            risk_level = "MEDIUM"
    
    # Check streak
    current_streak = streak_data.get('current_streak', 0)
    if current_streak == 0:
        alerts.append("No active study streak")
        risk_level = "HIGH"
    elif current_streak < 3:
        alerts.append("Short study streak")
        if risk_level != "HIGH":
            risk_level = "MEDIUM"
    
    if alerts:
        return {
            'message': "You're on track to fail.",
            'risk_level': risk_level,
            'alerts': alerts
        }
    
    return None

@app.route('/daily_tasks')
@login_required
def daily_tasks():
    current_user = get_current_user()
    sessions_data = get_user_study_sessions(current_user['id'])
    
    if not sessions_data:
        return render_template('daily_tasks.html', user=current_user, tasks=None, completion_status=0)
    
    # Analyze user data to determine weak subjects
    df = pd.DataFrame(sessions_data)
    weak_subjects = detect_weak_subjects_for_tasks(df)
    
    # Generate 3 mandatory tasks based on weak subjects
    tasks = generate_daily_tasks(weak_subjects)
    
    # Check if user has completed all tasks today
    completion_status = check_daily_task_completion(current_user['id'], tasks)
    
    return render_template('daily_tasks.html', user=current_user, tasks=tasks, completion_status=completion_status)

def detect_weak_subjects_for_tasks(df):
    """Detect weak subjects for daily task generation"""
    if df.empty:
        return []
    
    # Find subjects with low performance
    subject_performance = df.groupby('subject').agg({
        'hours': 'sum',
        'avg_difficulty': lambda x: x.mode().iloc[0] if not x.mode().empty else 'medium',
        'session_count': 'count'
    }).to_dict('index')
    
    weak_subjects = []
    for subject, perf in subject_performance.iterrows():
        if perf['hours'] < 5 or perf['avg_difficulty'] == 'easy':
            weak_subjects.append(subject)
            if len(weak_subjects) >= 3:
                break
    
    return weak_subjects[:3]  # Top 3 weakest subjects

def generate_daily_tasks(weak_subjects):
    """Generate 3 mandatory daily tasks based on weak subjects"""
    tasks = []
    
    for i, subject in enumerate(weak_subjects):
        if i == 0:
            tasks.append({
                'id': i + 1,
                'subject': subject,
                'task': f'Study {subject} for minimum 90 minutes',
                'difficulty': 'medium',
                'completed': False
            })
        elif i == 1:
            tasks.append({
                'id': i + 1,
                'subject': subject,
                'task': f'Complete 20 practice problems for {subject}',
                'difficulty': 'hard',
                'completed': False
            })
        else:
            tasks.append({
                'id': i + 1,
                'subject': subject,
                'task': f'Review {subject} concepts and create summary',
                'difficulty': 'medium',
                'completed': False
            })
    
    return tasks

def check_daily_task_completion(user_id, tasks):
    """Check if user has completed all daily tasks"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Check if all tasks are completed today
    cursor.execute('''
        SELECT COUNT(*) as completed_count
        FROM daily_task_completions
        WHERE user_id = ? AND date = ?
    ''', (user_id, today))
    
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] >= len(tasks):
        return 100  # All tasks completed
    elif result:
        return (result[0] / len(tasks)) * 100  # Percentage completed
    
    return 0

@app.route('/complete_all_tasks', methods=['POST'])
@login_required
def complete_all_tasks():
    current_user = get_current_user()
    
    # Mark all tasks as completed
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get all tasks for today
    cursor.execute('''
        SELECT task_id FROM daily_tasks 
        WHERE user_id = ? AND date = ?
    ''', (current_user['id'], today))
    
    task_ids = [row[0] for row in cursor.fetchall()]
    
    # Mark all as completed
    for task_id in task_ids:
        cursor.execute('''
            INSERT INTO daily_task_completions (user_id, task_id, date)
            VALUES (?, ?, ?)
        ''', (current_user['id'], task_id, today))
    

@app.route('/competitor')
@login_required
def competitor():
    current_user = get_current_user()
    sessions_data = get_user_study_sessions(current_user['id'])
    
    if not sessions_data:
        return render_template('competitor.html', user=current_user, competitor=None, comparison=None)
    
    # Analyze user data
    df = pd.DataFrame(sessions_data)
    result = analyze_behavior(df)
    scores = result['scores']
    analysis = result['analysis']
    
    # Generate AI competitor data
    competitor_data = generate_ai_comitor(scores, analysis)
    
    # Create comparison
    comparison = create_comparison(scores, analysis, competitor_data)
    
    return render_template('competitor.html', 
                     user=current_user, 
                     competitor=competitor_data, 
                     comparison=comparison)

def generate_ai_comitor(user_scores, user_analysis):
    """Generate AI competitor that's always slightly better"""
    # Base competitor metrics (always slightly better)
    competitor_hours = user_analysis.get('total_hours', 0) * 1.15
    competitor_discipline = min(100, user_scores.get('discipline_score', 0) + 8)
    competitor_streak = user_analysis.get('current_streak', 0) + 2
    
    # Generate competitor name based on user's performance
    if user_scores.get('discipline_score', 0) < 50:
        competitor_name = "Alex_Chen"
        competitor_subject = "Mathematics"
    elif user_scores.get('reality_score', 0) < 50:
        competitor_name = "Sarah_Kim"
        competitor_subject = "Physics"
    else:
        competitor_name = "Jordan_Lee"
        competitor_subject = "Chemistry"
    
    return {
        'name': competitor_name,
        'subject': competitor_subject,
        'total_hours': competitor_hours,
        'discipline_score': competitor_discipline,
        'current_streak': competitor_streak,
        'avatar': '🤖'
    }

def create_comparison(user_scores, user_analysis, competitor_data):
    """Create comparison between user and AI competitor"""
    return {
        'hours_diff': competitor_data['total_hours'] - user_analysis.get('total_hours', 0),
        'discipline_diff': competitor_data['discipline_score'] - user_scores.get('discipline_score', 0),
        'streak_diff': competitor_data['current_streak'] - user_analysis.get('current_streak', 0),
        'user_ahead': user_analysis.get('total_hours', 0) > competitor_data['total_hours'],
        'message': generate_competitor_message(user_scores, user_analysis, competitor_data)
    }

def generate_competitor_message(user_scores, user_analysis, competitor_data):
    """Generate motivational message about competitor"""
    if user_scores.get('discipline_score', 0) < 60:
        return f"{competitor_data['name']} is doing what you're avoiding. He's studying {competitor_data['subject']} while you're stuck in easy subjects."
    elif user_analysis.get('current_streak', 0) < competitor_data['current_streak']:
        return f"{competitor_data['name']} has a {competitor_data['current_streak']-user_analysis.get('current_streak', 0)} day streak lead. He's consistent while you're struggling."
    else:
        return f"{competitor_data['name']} is always one step ahead. He's putting in the work you're skipping."

@app.route('/update_competitor', methods=['POST'])
@login_required
def update_competitor():
    current_user = get_current_user()
    sessions_data = get_user_study_sessions(current_user['id'])
    
    if not sessions_data:
        return jsonify({'success': False, 'message': 'No data available'})
    
    # Analyze current user performance
    df = pd.DataFrame(sessions_data)
    result = analyze_behavior(df)
    scores = result['scores']
    analysis = result['analysis']
    
    # Generate updated competitor (always slightly better)
    competitor_data = generate_ai_comitor(scores, analysis)
    
    # Competitor improves based on user's improvement
    if scores.get('discipline_score', 0) > 70:
        competitor_data['discipline_score'] = min(100, competitor_data['discipline_score'] + 5)
    if analysis.get('total_hours', 0) > 20:
        competitor_data['total_hours'] = competitor_data['total_hours'] * 1.1
    if analysis.get('current_streak', 0) > 5:
        competitor_data['current_streak'] = competitor_data['current_streak'] + 1
    
    return jsonify({
        'success': True,
        'competitor': competitor_data,
        'comparison': create_comparison(scores, analysis, competitor_data)
    })

@app.route('/timeline')
@login_required
def timeline():
    current_user = get_current_user()
    sessions_data = get_user_study_sessions(current_user['id'])
    
    if not sessions_data:
        return render_template('timeline.html', user=current_user, timeline_data=None)
    
    # Get filter parameter
    filter_days = request.args.get('filter', '30')
    
    # Analyze timeline data
    timeline_data = generate_timeline_data(sessions_data, filter_days)
    
    return render_template('timeline.html', user=current_user, timeline_data=timeline_data)

def generate_timeline_data(sessions_data, filter_days):
    """Generate timeline data with daily performance and streak history"""
    if not sessions_data:
        return None
    
    df = pd.DataFrame(sessions_data)
    df['date'] = pd.to_datetime(df['date']).dt.date
    
    # Filter by time period
    today = datetime.now().date()
    if filter_days != 'all':
        cutoff_date = today - timedelta(days=int(filter_days))
        df = df[df['date'] >= cutoff_date]
    
    # Generate daily performance data
    daily_data = []
    for date in sorted(df['date'].unique(), reverse=True):
        day_data = df[df['date'] == date]
        
        if not day_data.empty:
            hours = day_data['hours'].sum()
            discipline_score = day_data['discipline_score'].iloc[0] if not day_data['discipline_score'].empty else 50
            
            # Determine day quality
            is_good = hours >= 2 and discipline_score >= 60
            is_bad = hours < 1 or discipline_score < 30
            
            # Check for relapse
            is_relapse = False
            if len(daily_data) > 1:
                prev_date = date - timedelta(days=1)
                prev_data = df[df['date'] == prev_date]
                if not prev_data.empty:
                    prev_hours = prev_data['hours'].sum()
                    prev_discipline = prev_data['discipline_score'].iloc[0] if not prev_data['discipline_score'].empty else 50
                    # Relapse if significant drop in performance
                    if (prev_hours >= 2 and hours < 1) or (prev_discipline >= 60 and discipline_score < 30):
                        is_relapse = True
            
            # Get current streak
            current_streak = calculate_current_streak(df[df['date'] <= date])
            
            daily_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'hours': hours,
                'discipline_score': discipline_score,
                'is_good': is_good,
                'is_bad': is_bad,
                'is_relapse': is_relapse,
                'streak': current_streak
            })
    
    # Generate streak history
    streak_history = generate_streak_history(df)
    
    # Calculate statistics
    total_days = len(daily_data)
    good_days = len([d for d in daily_data if d['is_good']])
    bad_days = len([d for d in daily_data if d['is_bad']])
    relapses = len([d for d in daily_data if d['is_relapse']])
    
    return {
        'days': daily_data,
        'streak_history': streak_history,
        'total_days': total_days,
        'good_days': good_days,
        'bad_days': bad_days,
        'relapses': relapses
    }

def generate_streak_history(df):
    """Generate streak history from session data"""
    if df.empty:
        return []
    
    df_sorted = df.sort_values('date')
    streaks = []
    current_streak = 0
    streak_start = None
    
    for _, row in df_sorted.iterrows():
        date = pd.to_datetime(row['date']).date()
        hours = row['hours']
        
        if hours > 0:
            if current_streak == 0:
                streak_start = date
            current_streak += 1
        else:
            # Check if this is consecutive
            prev_date = date - timedelta(days=1)
            if prev_date in [pd.to_datetime(r['date']).date() for _, r in df_sorted.iterrows() if pd.to_datetime(r['date']).date() == prev_date]:
                current_streak += 1
            else:
                # Streak ended
                if streak_start and current_streak > 1:
                    streaks.append({
                        'start_date': streak_start.strftime('%Y-%m-%d'),
                        'end_date': (date - timedelta(days=1)).strftime('%Y-%m-%d'),
                        'length': current_streak,
                        'is_active': False
                    })
                
                current_streak = 1
                streak_start = date
    
    # Add current streak if active
    if current_streak > 1:
        streaks.append({
            'start_date': streak_start.strftime('%Y-%m-%d'),
            'end_date': datetime.now().date().strftime('%Y-%m-%d'),
            'length': current_streak,
            'is_active': True
        })
    
    return streaks[:10]  # Last 10 streaks

@app.route('/transformation')
@login_required
def transformation():
    current_user = get_current_user()
    sessions_data = get_user_study_sessions(current_user['id'])
    
    if not sessions_data:
        return render_template('transformation.html', user=current_user, transformation_active=False, strict_schedule=None)
    
    # Analyze user data
    df = pd.DataFrame(sessions_data)
    result = analyze_behavior(df)
    scores = result['scores']
    analysis = result['analysis']
    
    # Check if transformation mode is active
    transformation_active = session.get('transformation_mode', False)
    
    if transformation_active:
        # Generate strict schedule
        strict_schedule = generate_strict_schedule(scores, analysis)
    else:
        strict_schedule = None
    
    return render_template('transformation.html', 
                     user=current_user, 
                     transformation_active=transformation_active, 
                     strict_schedule=strict_schedule)

@app.route('/activate_transformation', methods=['POST'])
@login_required
def activate_transformation():
    current_user = get_current_user()
    sessions_data = get_user_study_sessions(current_user['id'])
    
    if not sessions_data:
        return jsonify({'success': False, 'message': 'No study data available'})
    
    # Activate transformation mode
    session['transformation_mode'] = True
    session['transformation_start'] = datetime.now().strftime('%Y-%m-%d')
    
    # Generate strict schedule
    df = pd.DataFrame(sessions_data)
    result = analyze_behavior(df)
    scores = result['scores']
    analysis = result['analysis']
    
    strict_schedule = generate_strict_schedule(scores, analysis)
    
    return jsonify({
        'success': True,
        'message': 'Transformation mode activated',
        'strict_schedule': strict_schedule
    })

@app.route('/deactivate_transformation', methods=['POST'])
@login_required
def deactivate_transformation():
    session['transformation_mode'] = False
    session.pop('transformation_start', None)
    session.pop('strict_schedule', None)
    
    return jsonify({
        'success': True,
        'message': 'Transformation mode deactivated'
    })

def generate_strict_schedule(scores, analysis):
    """Generate strict schedule with no flexibility"""
    # Identify user's weak areas
    weak_areas = []
    if scores.get('discipline_score', 0) < 50:
        weak_areas.append('Discipline')
    if scores.get('reality_score', 0) < 50:
        weak_areas.append('Reality')
    if scores.get('avoidance_score', 0) > 60:
        weak_areas.append('Avoidance')
    
    # Generate strict schedule based on weak areas
    schedule = []
    
    # Get user's subjects
    current_user = get_current_user()
    sessions_data = get_user_study_sessions(current_user['id'])
    if sessions_data:
        df = pd.DataFrame(sessions_data)
        subjects = df['subject'].unique().tolist()
    else:
        subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'History', 'English']
    
    # Generate 7-day strict schedule
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for i, day in enumerate(days_of_week):
        if 'Discipline' in weak_areas:
            # Focus on hardest subject first
            schedule.append({
                'day': day,
                'time': '6:00 AM',
                'subject': subjects[0] if subjects else 'Mathematics',
                'duration': 3,
                'difficulty': 'hard',
                'notes': 'No excuses. Maximum focus required.'
            })
            
            if 'Reality' in weak_areas:
                schedule.append({
                    'day': day,
                    'time': '10:00 AM',
                    'subject': subjects[1] if len(subjects) > 1 else 'Physics',
                    'duration': 2,
                    'difficulty': 'hard',
                    'notes': 'Face uncomfortable truths about your abilities.'
                })
            
            if 'Avoidance' in weak_areas:
                schedule.append({
                    'day': day,
                    'time': '2:00 PM',
                    'subject': subjects[2] if len(subjects) > 2 else 'Chemistry',
                    'duration': 2,
                    'difficulty': 'medium',
                    'notes': 'Confront what you avoid. No escape routes.'
                })
            
            # Fill remaining slots with moderate difficulty
            remaining_subjects = [s for s in subjects if s not in [item['subject'] for item in schedule]]
            for j in range(2, 4):
                if j < len(remaining_subjects):
                    schedule.append({
                        'day': day,
                        'time': f"{8 + j}:00 AM" if j < 2 else f"{8 + j}:00 PM",
                        'subject': remaining_subjects[j],
                        'duration': 2,
                        'difficulty': 'medium',
                        'notes': 'Consistent effort beats talent.'
                    })
    
    return {
        'schedule': schedule,
        'weak_areas': weak_areas,
        'message': 'This is the version of you that wins.',
        'start_date': datetime.now().strftime('%Y-%m-%d'),
        'strict_mode': True
    }

@app.route('/log', methods=['GET', 'POST'])
@login_required
def log():
    current_user = get_current_user()
    
    if request.method == 'POST':
        subject = request.form['subject']
        hours = float(request.form['hours'])
        difficulty = request.form['difficulty']
        
        if save_study_session(current_user['id'], subject, hours, difficulty):
            # Update streak (studied today)
            streak_result = update_streak(current_user['id'], True)
            
            # Show motivational messages
            if streak_result['broke_streak']:
                flash('You broke your streak. That\'s exactly why you\'re average.', 'warning')
            elif streak_result['current_streak'] >= 7:
                flash('You\'re building momentum. Don\'t ruin it.', 'info')
            
            # Check for relapse alert
            sessions_data = get_user_study_sessions(current_user['id'])
            df = pd.DataFrame(sessions_data)
            result = analyze_behavior(df)
            analysis = result['analysis']
            failure_alert = check_failure_alerts(analysis, streak_result)
            
            if failure_alert:
                flash(failure_alert['message'], 'error')
                if failure_alert.get('recovery_plan'):
                    for plan_item in failure_alert['recovery_plan']['plan']:
                        flash(f'Recovery: {plan_item}', 'info')
            
            flash('Study session logged successfully!', 'success')
            return redirect(url_for('index'))
        
        # Check if all tasks are completed today
        completion_status = check_daily_task_completion(current_user['id'], tasks)
        
        if completion_status == 100:
            flash('All daily tasks completed! Great job staying consistent.', 'success')
        elif completion_status > 0:
            flash(f'{completion_status}% of tasks completed. Keep going!', 'info')
        else:
            flash('Complete all 3 tasks to avoid failure alert.', 'warning')
        
        return render_template('log.html', subjects=get_available_subjects(), user=current_user)
    
    subjects = get_available_subjects()
    return render_template('log.html', subjects=subjects, user=current_user)

@app.route('/analysis')
@login_required
def analysis():
    current_user = get_current_user()
    sessions_data = get_user_study_sessions(current_user['id'])
    
    if not sessions_data:
        return render_template('analysis.html', has_data=False, user=current_user)
    
    df = pd.DataFrame(sessions_data)
    
    # Generate graphs
    subject_img = create_subject_graph(df)
    daily_img = create_daily_graph(df)
    
    # Display study data table
    sessions = df.to_dict('records')
    
    return render_template('analysis.html', 
                         has_data=True,
                         sessions=sessions,
                         subject_graph=subject_img,
                         daily_graph=daily_img,
                         user=current_user)

@app.route('/mirror')
@login_required
def mirror():
    current_user = get_current_user()
    sessions_data = get_user_study_sessions(current_user['id'])
    
    if not sessions_data:
        return render_template('mirror.html', has_data=False, user=current_user)
    
    df = pd.DataFrame(sessions_data)
    result = analyze_behavior(df)
    
    # Get pattern names
    pattern_names = {
        'over_focus_easy': 'Hiding in Easy Subjects',
        'lack_balance': 'Unbalanced Study Approach',
        'irregular_study': 'Inconsistent Schedule',
        'hard_subject_avoidance': 'Avoiding Hard Subjects',
        'fake_consistency': 'Fake Consistency Pattern',
        'spike_then_crash': 'Spike Then Crash Pattern'
    }
    
    patterns = [pattern_names.get(p, p) for p in result['patterns']]
    
    return render_template('mirror.html',
                         has_data=True,
                         truth_statements=result['truth_statements'],
                         patterns=patterns,
                         scores=result['scores'],
                         analysis=result['analysis'],
                         user=current_user)

@app.route('/report')
@login_required
def report():
    current_user = get_current_user()
    generate_new = request.args.get('generate', 'false').lower() == 'true'
    
    sessions_data = get_user_study_sessions(current_user['id'])
    
    if not sessions_data:
        return render_template('report.html', user=current_user, report_data=None)
    
    df = pd.DataFrame(sessions_data)
    
    # Generate weekly report
    report_data = generate_weekly_report(df)
    
    return render_template('report.html', user=current_user, report_data=report_data)

def generate_weekly_report(df):
    """Generate weekly reality report"""
    if df.empty:
        return None
    
    # Get last 7 days
    end_date = pd.to_datetime(df['date']).max()
    start_date = end_date - timedelta(days=6)
    
    # Filter last week data
    df['date'] = pd.to_datetime(df['date'])
    week_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    if week_df.empty:
        week_df = df.tail(7)  # Fallback to last 7 sessions
    
    # Calculate daily stats
    daily_stats = week_df.groupby(week_df['date'].dt.strftime('%A')).agg({
        'hours': 'sum',
        'sessions': 'count'
    }).to_dict('index')
    
    # Find best and worst days
    best_day_name = max(daily_stats, key=lambda x: daily_stats[x]['hours'])
    worst_day_name = min(daily_stats, key=lambda x: daily_stats[x]['hours'])
    
    best_day = {
        'day': best_day_name,
        'hours': daily_stats[best_day_name]['hours'],
        'sessions': daily_stats[best_day_name]['sessions']
    }
    
    worst_day = {
        'day': worst_day_name,
        'hours': daily_stats[worst_day_name]['hours'],
        'sessions': daily_stats[worst_day_name]['sessions']
    }
    
    # Analyze patterns for biggest mistake
    difficulty_dist = week_df['difficulty'].value_counts()
    subject_dist = week_df['subject'].value_counts()
    
    biggest_mistake = {}
    if 'easy' in difficulty_dist and difficulty_dist['easy'] > len(week_df) * 0.6:
        biggest_mistake = {
            'title': 'Comfort Zone Addiction',
            'description': f'{difficulty_dist["easy"]} out of {len(week_df)} sessions were easy difficulty'
        }
    elif len(subject_dist) == 1:
        biggest_mistake = {
            'title': 'Subject Monotony',
            'description': f'You only studied {subject_dist.index[0]} all week'
        }
    else:
        most_studied = subject_dist.index[0]
        least_studied = subject_dist.index[-1]
        biggest_mistake = {
            'title': 'Subject Imbalance',
            'description': f'Focused too much on {most_studied}, ignored {least_studied}'
        }
    
    # Generate harsh truth
    total_hours = week_df['hours'].sum()
    total_sessions = len(week_df)
    avg_hours_per_day = total_hours / 7
    
    harsh_truth = ""
    if total_hours < 10:
        harsh_truth = f"You studied only {total_hours:.1f} hours this week. That's not studying, that's pretending to care."
    elif avg_hours_per_day < 1.5:
        harsh_truth = f"Your daily average of {avg_hours_per_day:.1f} hours is pathetic. Success requires actual effort."
    elif len(daily_stats) < 5:
        harsh_truth = f"You only studied {len(daily_stats)} different days this week. Consistency is not your strong suit."
    else:
        harsh_truth = f"{total_hours:.1f} hours this week might look decent, but your efficiency is terrible. Quality over quantity matters."
    
    # Calculate grade
    avg_score = (total_hours / 20) * 100  # 20 hours = 100%
    if avg_score >= 80:
        grade, grade_text, grade_class = 'A', 'EXCELLENT', 'grade-excellent'
    elif avg_score >= 60:
        grade, grade_text, grade_class = 'B', 'GOOD', 'grade-good'
    elif avg_score >= 40:
        grade, grade_text, grade_class = 'C', 'AVERAGE', 'grade-average'
    elif avg_score >= 20:
        grade, grade_text, grade_class = 'D', 'POOR', 'grade-poor'
    else:
        grade, grade_text, grade_class = 'F', 'CRITICAL', 'grade-critical'
    
    # Format week range
    week_range = f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
    
    # Generate full text report
    full_text = f"""MIRROR-X WEEKLY REALITY REPORT
{week_range}

GRADE: {grade} - {grade_text}

BEST DAY: {best_day['day']}
- Hours: {best_day['hours']:.1f}
- Sessions: {best_day['sessions']}

WORST DAY: {worst_day['day']}
- Hours: {worst_day['hours']:.1f}
- Sessions: {worst_day['sessions']}

BIGGEST MISTAKE: {biggest_mistake['title']}
{biggest_mistake['description']}

HARSH TRUTH:
{harsh_truth}

TOTALS:
- Hours: {total_hours:.1f}
- Sessions: {total_sessions}
- Daily Average: {avg_hours_per_day:.1f} hours

Generated by MIRROR-X Study Intelligence System
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return {
        'week_range': week_range,
        'grade': grade,
        'grade_text': grade_text,
        'grade_class': grade_class,
        'best_day': best_day,
        'worst_day': worst_day,
        'biggest_mistake': biggest_mistake,
        'harsh_truth': harsh_truth,
        'full_text': full_text
    }

@app.route('/leaderboard')
@login_required
def leaderboard():
    current_user = get_current_user()
    
    # Update scores before fetching leaderboard
    update_user_scores()
    
    # Get leaderboard data
    leaderboard = get_leaderboard_data(limit=100)
    
    # Calculate user's rank
    your_rank = len(leaderboard) + 1  # Default to last if not found
    for i, user in enumerate(leaderboard):
        if user['id'] == current_user['id']:
            your_rank = i + 1
            break
    
    # Calculate statistics
    total_users = len(leaderboard)
    average_discipline = sum(user['discipline_score'] for user in leaderboard) / len(leaderboard) if leaderboard else 0
    average_consistency = sum(user['consistency'] for user in leaderboard) / len(leaderboard) if leaderboard else 0
    top_streak = max((user['current_streak'] for user in leaderboard), default=0) if leaderboard else 0
    
    return render_template('leaderboard.html',
                         user=current_user,
                         leaderboard=leaderboard,
                         top_users=leaderboard[:3],
                         your_rank=your_rank,
                         total_users=total_users,
                         average_discipline=average_discipline,
                         average_consistency=average_consistency,
                         top_streak=top_streak)

@app.route('/streak')
@login_required
def streak():
    current_user = get_current_user()
    sessions_data = get_user_study_sessions(current_user['id'])
    
    if not sessions_data:
        return render_template('streak.html', 
                         user=current_user, 
                         streak_data={'current_streak': 0, 'longest_streak': 0},
                         calendar_days=[],
                         recent_streaks=[],
                         monthly_days_studied=0,
                         monthly_study_rate=0)
    
    # Get streak data
    streak_data = get_user_streak(current_user['id'])
    
    # Generate calendar data for last 30 days
    calendar_days = []
    today = datetime.now()
    
    for i in range(30):
        check_date = today - timedelta(days=i)
        date_str = check_date.strftime('%Y-%m-%d')
        studied = any(session['date'] == date_str for session in sessions_data)
        
        calendar_days.append({
            'day': check_date.day,
            'studied': studied,
            'date': date_str
        })
    
    calendar_days.reverse()  # Show oldest to newest
    
    # Calculate monthly stats
    current_month = today.strftime('%Y-%m')
    monthly_sessions = [s for s in sessions_data if s['date'].startswith(current_month)]
    monthly_days_studied = len(set(s['date'] for s in monthly_sessions))
    monthly_study_rate = (monthly_days_studied / today.day) * 100 if today.day > 0 else 0
    
    # Generate recent streaks
    recent_streaks = []
    if sessions_data:
        # Group by date and find streak periods
        dates = sorted(set(s['date'] for s in sessions_data), reverse=True)
        
        current_streak_start = None
        current_streak_length = 0
        
        for date_str in dates:
            if current_streak_start is None:
                current_streak_start = date_str
                current_streak_length = 1
            else:
                # Check if consecutive
                prev_date = datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=1)
                if prev_date.strftime('%Y-%m-%d') in dates:
                    current_streak_length += 1
                else:
                    # End streak and start new one
                    if current_streak_length > 1:
                        recent_streaks.append({
                            'start_date': current_streak_start,
                            'end_date': date_str,
                            'length': current_streak_length,
                            'active': False
                        })
                    current_streak_start = date_str
                    current_streak_length = 1
        
        # Add current streak if active
        if current_streak_length > 0:
            recent_streaks.append({
                'start_date': current_streak_start,
                'end_date': today.strftime('%Y-%m-%d'),
                'length': current_streak_length,
                'active': True
            })
    
    return render_template('streak.html', 
                     user=current_user, 
                     streak_data=streak_data,
                     calendar_days=calendar_days,
                     recent_streaks=recent_streaks[:5],  # Show last 5 streaks
                     monthly_days_studied=monthly_days_studied,
                     monthly_study_rate=monthly_study_rate)

@app.route('/plan')
@login_required
def plan():
    current_user = get_current_user()
    return render_template('plan.html', user=current_user, plan_generated=False)

@app.route('/generate_plan', methods=['POST'])
@login_required
def generate_plan():
    current_user = get_current_user()
    sessions_data = get_user_study_sessions(current_user['id'])
    
    if not sessions_data:
        return jsonify({'success': False, 'error': 'No study data available'})
    
    try:
        data = request.get_json()
        
        # Analyze user data
        df = pd.DataFrame(sessions_data)
        weak_subjects = data['weak_subjects']
        patterns = data['patterns']
        avoidance = data['avoidance']
        preferences = data['preferences']
        
        # Generate AI study plan
        plan = ai_generate_study_plan(df, weak_subjects, patterns, avoidance, preferences)
        
        # Store plan in session
        session['study_plan'] = plan
        session['plan_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/regenerate_plan', methods=['POST'])
@login_required
def regenerate_plan():
    current_user = get_current_user()
    sessions_data = get_user_study_sessions(current_user['id'])
    
    if not sessions_data:
        return jsonify({'success': False, 'error': 'No study data available'})
    
    try:
        df = pd.DataFrame(sessions_data)
        
        # Auto-detect patterns from data
        weak_subjects = detect_weak_subjects(df)
        patterns = detect_study_patterns(df)
        avoidance = detect_avoidance_patterns(df)
        
        # Default preferences
        preferences = {
            'daily_hours': 4,
            'sessions_per_day': 2,
            'session_length': 2
        }
        
        # Generate new plan
        plan = ai_generate_study_plan(df, weak_subjects, patterns, avoidance, preferences)
        
        # Update session
        session['study_plan'] = plan
        session['plan_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def ai_generate_study_plan(df, weak_subjects, patterns, avoidance, preferences):
    """Generate AI-powered study plan based on user data and inputs"""
    
    # Analyze current performance
    subject_performance = df.groupby('subject').agg({
        'hours': 'sum',
        'difficulty': lambda x: x.mode().iloc[0] if not x.mode().empty else 'medium'
    }).to_dict('index')
    
    # Create daily schedule
    schedule = create_daily_schedule(patterns, preferences, weak_subjects)
    
    # Prioritize subjects
    subject_priority = prioritize_subjects(weak_subjects, subject_performance, avoidance)
    
    # Allocate hours
    hours_allocation = allocate_hours(subject_priority, preferences['daily_hours'] * 7)
    
    # Generate implementation tips
    implementation_tips = generate_tips(patterns, avoidance, weak_subjects)
    
    return {
        'schedule': schedule,
        'subject_priority': subject_priority,
        'hours_allocation': hours_allocation,
        'implementation_tips': implementation_tips
    }

def create_daily_schedule(patterns, preferences, weak_subjects):
    """Create 7-day study schedule"""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    schedule = []
    
    for i, day_name in enumerate(days):
        sessions = []
        total_hours = 0
        
        # Determine best time based on patterns
        if patterns.get('morning_person') and i < 5:  # Weekday
            sessions.append({
                'time': '8:00 AM',
                'subject': weak_subjects[0]['name'] if weak_subjects else 'Focus Subject',
                'duration': preferences['session_length'],
                'difficulty': 'medium'
            })
            total_hours += preferences['session_length']
        
        if patterns.get('afternoon_person') and i < 5 and total_hours < preferences['daily_hours']:
            sessions.append({
                'time': '2:00 PM',
                'subject': weak_subjects[1]['name'] if len(weak_subjects) > 1 else 'Practice Subject',
                'duration': min(preferences['session_length'], preferences['daily_hours'] - total_hours),
                'difficulty': 'hard' if not patterns.get('avoid_hard') else 'medium'
            })
            total_hours += min(preferences['session_length'], preferences['daily_hours'] - total_hours)
        
        if patterns.get('evening_person') and i < 5 and total_hours < preferences['daily_hours']:
            remaining = preferences['daily_hours'] - total_hours
            if remaining > 0:
                sessions.append({
                    'time': '7:00 PM',
                    'subject': weak_subjects[2]['name'] if len(weak_subjects) > 2 else 'Review Subject',
                    'duration': remaining,
                    'difficulty': 'easy'
                })
                total_hours += remaining
        
        schedule.append({
            'name': day_name,
            'total_hours': total_hours,
            'sessions': sessions
        })
    
    return schedule

def prioritize_subjects(weak_subjects, subject_performance, avoidance):
    """Prioritize subjects based on weakness and performance"""
    priority_list = []
    
    # Add weak subjects first (highest priority)
    for subject in weak_subjects:
        priority_list.append({
            'name': subject['name'],
            'reason': f"Weak subject ({subject['difficulty']} difficulty)",
            'recommended_hours': 6,
            'priority_score': 100
        })
    
    # Add other subjects based on performance
    for subject, perf in subject_performance.items():
        if subject not in [s['name'] for s in weak_subjects]:
            priority_score = max(0, 50 - perf['hours'])  # Less studied = higher priority
            priority_list.append({
                'name': subject,
                'reason': f"Needs more practice ({perf['hours']:.1f}h studied)",
                'recommended_hours': 4,
                'priority_score': priority_score
            })
    
    # Sort by priority score
    priority_list.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return priority_list[:5]  # Top 5 subjects

def allocate_hours(subject_priority, total_weekly_hours):
    """Allocate weekly hours to subjects"""
    allocation = []
    remaining_hours = total_weekly_hours
    
    colors = ['#4a9eff', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    
    for i, subject in enumerate(subject_priority):
        hours = min(subject['recommended_hours'], remaining_hours)
        percentage = (hours / total_weekly_hours) * 100 if total_weekly_hours > 0 else 0
        
        allocation.append({
            'name': subject['name'],
            'hours': hours,
            'percentage': percentage,
            'color': colors[i % len(colors)]
        })
        
        remaining_hours -= hours
        if remaining_hours <= 0:
            break
    
    return allocation

def generate_tips(patterns, avoidance, weak_subjects):
    """Generate personalized implementation tips"""
    tips = []
    
    # Pattern-based tips
    if patterns.get('procrastinator'):
        tips.append({
            'icon': '⏰',
            'title': 'Beat Procrastination',
            'description': 'Start with 15-minute sessions. The hardest part is starting.'
        })
    
    if patterns.get('avoid_consistency'):
        tips.append({
            'icon': '📅',
            'title': 'Build Consistency',
            'description': 'Study at the same time daily. Your brain will adapt automatically.'
        })
    
    # Avoidance-based tips
    if avoidance.get('avoid_hard'):
        tips.append({
            'icon': '💪',
            'title': 'Embrace Difficulty',
            'description': 'Start each session with your hardest subject. Willpower is highest then.'
        })
    
    if avoidance.get('avoid_long_sessions'):
        tips.append({
            'icon': '⏱️',
            'title': 'Extend Sessions Gradually',
            'description': 'Add 15 minutes to each session weekly. Build endurance slowly.'
        })
    
    # Weak subject tips
    if weak_subjects:
        hardest_subject = max(weak_subjects, key=lambda x: {'hard': 3, 'medium': 2, 'easy': 1}[x['difficulty']])
        tips.append({
            'icon': '🎯',
            'title': f'Focus on {hardest_subject["name"]}',
            'description': f'Dedicate your best study hours to {hardest_subject["name"]} when mentally fresh.'
        })
    
    return tips

def detect_weak_subjects(df):
    """Auto-detect weak subjects from performance data"""
    if df.empty:
        return []
    
    subject_performance = df.groupby('subject').agg({
        'hours': 'sum',
        'avg_difficulty': lambda x: x.mode().iloc[0] if not x.mode().empty else 'medium'
    }).to_dict('index')
    
    weak_subjects = []
    for subject, perf in subject_performance.iterrows():
        if perf['hours'] < 5 or perf['avg_difficulty'] == 'easy':
            weak_subjects.append({
                'name': subject,
                'difficulty': perf['avg_difficulty']
            })
    
    return weak_subjects[:3]  # Top 3 weakest

def detect_study_patterns(df):
    """Detect study patterns from user data"""
    patterns = {}
    
    if not df.empty:
        return patterns
    
    # Time patterns
    df['hour'] = pd.to_datetime(df['date']).dt.hour
    morning_sessions = len(df[(df['hour'] >= 6) & (df['hour'] < 12)])
    afternoon_sessions = len(df[(df['hour'] >= 12) & (df['hour'] < 18)])
    evening_sessions = len(df[(df['hour'] >= 18) | (df['hour'] < 6)])
    
    total_sessions = len(df)
    
    if morning_sessions / total_sessions > 0.4:
        patterns['morning_person'] = True
    if afternoon_sessions / total_sessions > 0.4:
        patterns['afternoon_person'] = True
    if evening_sessions / total_sessions > 0.4:
        patterns['evening_person'] = True
    
    # Consistency pattern
    df['date'] = pd.to_datetime(df['date']).dt.date
    study_days = len(df['date'].unique())
    total_days = (df['date'].max() - df['date'].min()).days + 1
    if study_days / total_days < 0.5:
        patterns['avoid_consistency'] = True
    
    return patterns

def detect_avoidance_patterns(df):
    """Detect avoidance patterns from user data"""
    avoidance = {}
    
    if df.empty:
        return avoidance
    
    # Hard subject avoidance
    hard_sessions = len(df[df['difficulty'] == 'hard'])
    total_sessions = len(df)
    if hard_sessions / total_sessions < 0.2:
        avoidance['avoid_hard'] = True
    
    # Long session avoidance
    avg_session_length = df['hours'].mean()
    if avg_session_length < 1.5:
        avoidance['avoid_long_sessions'] = True
    
    return avoidance

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    current_user = get_current_user()
    
    if request.method == 'POST':
        user_input = request.form['message']
        sessions_data = get_user_study_sessions(current_user['id'])
        
        if not sessions_data:
            response = "No data to analyze. Log your study sessions first."
        else:
            df = pd.DataFrame(sessions_data)
            response = mirror_chat(df, user_input)
        
        return jsonify({'response': response})
    
    # Check if user has a generated plan
    plan_generated = 'study_plan' in session
    plan_data = session.get('study_plan', {})
    plan_date = session.get('plan_date', '')
    
    return render_template('plan.html', 
                     user=current_user, 
                     plan_generated=plan_generated,
                     schedule=plan_data.get('schedule', []),
                     subject_priority=plan_data.get('subject_priority', []),
                     hours_allocation=plan_data.get('hours_allocation', []),
                     implementation_tips=plan_data.get('implementation_tips', []),
                     plan_date=plan_date)

def create_subject_graph(df):
    plt.figure(figsize=(10, 6))
    subject_hours = df.groupby('subject')['hours'].sum().sort_values(ascending=False)
    subject_hours.plot(kind='bar', color='#4a9eff')
    plt.title('Study Hours by Subject', fontsize=14, fontweight='bold', color='white')
    plt.xlabel('Subject', color='white')
    plt.ylabel('Total Hours', color='white')
    plt.xticks(rotation=45, color='white')
    plt.yticks(color='white')
    plt.gca().set_facecolor('#1a1a1a')
    plt.gcf().patch.set_facecolor('#1a1a1a')
    plt.tight_layout()
    plt.grid(axis='y', alpha=0.3, color='white')
    
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor='#1a1a1a')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    return plot_url

def create_daily_graph(df):
    plt.figure(figsize=(12, 6))
    daily_hours = df.groupby('date')['hours'].sum()
    daily_hours.index = pd.to_datetime(daily_hours.index)
    daily_hours = daily_hours.sort_index()
    
    plt.plot(daily_hours.index, daily_hours.values, marker='o', linewidth=2, markersize=6, color='#ff6b6b')
    plt.title('Daily Study Hours', fontsize=14, fontweight='bold', color='white')
    plt.xlabel('Date', color='white')
    plt.ylabel('Hours Studied', color='white')
    plt.xticks(rotation=45, color='white')
    plt.yticks(color='white')
    plt.gca().set_facecolor('#1a1a1a')
    plt.gcf().patch.set_facecolor('#1a1a1a')
    plt.grid(True, alpha=0.3, color='white')
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor='#1a1a1a')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    return plot_url

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

def create_daily_graph(df):
    plt.figure(figsize=(12, 6))
    daily_hours = df.groupby('date')['hours'].sum()
    daily_hours.index = pd.to_datetime(daily_hours.index)
    daily_hours = daily_hours.sort_index()
    
    plt.plot(daily_hours.index, daily_hours.values, marker='o', linewidth=2, markersize=6, color='#ff6b6b')
    plt.title('Daily Study Hours', fontsize=14, fontweight='bold', color='white')
    plt.xlabel('Date', color='white')
    plt.ylabel('Hours Studied', color='white')
    plt.xticks(rotation=45, color='white')
    plt.yticks(color='white')
    plt.gca().set_facecolor('#1a1a1a')
    plt.gcf().patch.set_facecolor('#1a1a1a')
    plt.grid(True, alpha=0.3, color='white')
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor='#1a1a1a')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    return plot_url

if __name__ == '__main__':
    initialize_csv()
    app.run(debug=True)
