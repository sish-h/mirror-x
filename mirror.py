import pandas as pd
from typing import Dict, List
from analysis import get_recent_data, calculate_streak
import json
import os

HISTORY_FILE = 'score_history.json'

def load_score_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_score_history(history):
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)
    except:
        pass

def get_behavior_trend(df: pd.DataFrame) -> Dict:
    if df.empty:
        return {'trend': 'no_data', 'direction': 'none'}
    
    history = load_score_history()
    
    # Get recent data for comparison
    recent_df = get_recent_data(df, 7)
    if recent_df.empty:
        return {'trend': 'insufficient_data', 'direction': 'none'}
    
    # Compare with previous period if available
    if len(history) >= 2:
        previous_scores = history[-2]
        current_scores = history[-1] if history else None
        
        if current_scores and previous_scores:
            current_avg = (current_scores['reality_score'] + current_scores['discipline_score']) / 2
            previous_avg = (previous_scores['reality_score'] + previous_scores['discipline_score']) / 2
            
            if current_avg > previous_avg + 5:
                return {'trend': 'improving', 'direction': 'up', 'magnitude': current_avg - previous_avg}
            elif current_avg < previous_avg - 5:
                return {'trend': 'declining', 'direction': 'down', 'magnitude': previous_avg - current_avg}
            else:
                return {'trend': 'stable', 'direction': 'neutral'}
    
    return {'trend': 'insufficient_data', 'direction': 'none'}

def calculate_adaptive_intensity(scores: Dict, trend: Dict) -> float:
    base_intensity = 1.0
    
    # Adjust based on performance
    avg_score = (scores['reality_score'] + scores['discipline_score']) / 2
    
    if avg_score < 40:
        base_intensity += 0.5  # Increase intensity for poor performance
    elif avg_score > 70:
        base_intensity -= 0.3  # Reduce intensity for good performance
    
    # Adjust based on trend
    if trend.get('trend') == 'improving':
        base_intensity -= 0.2  # Reduce intensity if improving
    elif trend.get('trend') == 'declining':
        base_intensity += 0.3  # Increase intensity if declining
    
    return max(0.3, min(2.0, base_intensity))

def calculate_reality_score(analysis: Dict) -> int:
    if not analysis:
        return 0
    
    score = 100
    
    # Consistency impact
    if 'consistency' in analysis:
        if analysis['consistency'] < 40:
            score -= 30
        elif analysis['consistency'] < 60:
            score -= 15
    
    # Balance impact
    if 'subject_hours' in analysis and len(analysis['subject_hours']) > 1:
        hours = list(analysis['subject_hours'].values())
        if hours and max(hours) > 0:
            balance = min(hours) / max(hours)
            if balance < 0.2:
                score -= 25
            elif balance < 0.4:
                score -= 10
    
    # Difficulty balance
    if 'difficulty_hours' in analysis:
        total = sum(analysis['difficulty_hours'].values())
        if total > 0:
            easy_ratio = analysis['difficulty_hours'].get('easy', 0) / total
            if easy_ratio > 0.7:
                score -= 20
    
    # Contradiction penalty (low hours + high frequency)
    if 'recent_total_hours' in analysis and 'recent_sessions' in analysis:
        if analysis['recent_sessions'] > 5 and analysis['recent_total_hours'] < 10:
            score -= 15
    
    # Streak bonus
    if 'current_streak' in analysis:
        if analysis['current_streak'] >= 7:
            score += 10
        elif analysis['current_streak'] >= 3:
            score += 5
    
    return max(0, min(100, score))

def calculate_discipline_score(analysis: Dict) -> int:
    if not analysis:
        return 0
    
    score = 0
    
    # Consistency scoring
    if 'consistency' in analysis:
        score += analysis['consistency'] * 0.3
    
    # Streak scoring (major factor)
    if 'current_streak' in analysis:
        streak_bonus = min(40, analysis['current_streak'] * 5)
        score += streak_bonus
    
    # Regular study habit
    if 'total_hours' in analysis and 'total_sessions' in analysis:
        if analysis['total_hours'] > 20:
            score += 15
        if analysis['total_sessions'] > 10:
            score += 10
    
    # Session regularity
    if 'avg_hours_per_session' in analysis:
        if 1 <= analysis['avg_hours_per_session'] <= 4:
            score += 15
    
    # Missed days penalty
    if 'missed_days' in analysis:
        missed_penalty = min(20, analysis['missed_days'] * 2)
        score -= missed_penalty
    
    return max(0, min(100, int(score)))

def calculate_avoidance_score(analysis: Dict) -> int:
    if not analysis:
        return 0
    
    score = 0
    
    # Easy subject preference
    if 'difficulty_hours' in analysis:
        total = sum(analysis['difficulty_hours'].values())
        if total > 0:
            easy_ratio = analysis['difficulty_hours'].get('easy', 0) / total
            score += easy_ratio * 30
    
    # Subject avoidance
    if 'subject_hours' in analysis and len(analysis['subject_hours']) > 1:
        hours = list(analysis['subject_hours'].values())
        if hours and max(hours) > 0:
            avoidance = 1 - (min(hours) / max(hours))
            score += avoidance * 25
    
    # Inconsistency
    if 'consistency' in analysis:
        inconsistency = (100 - analysis['consistency']) / 100
        score += inconsistency * 20
    
    # Hard subject avoidance penalty
    if 'difficulty_hours' in analysis:
        total = sum(analysis['difficulty_hours'].values())
        if total > 0:
            hard_ratio = analysis['difficulty_hours'].get('hard', 0) / total
            if hard_ratio == 0:
                score += 25
            elif hard_ratio < 0.1:
                score += 15
    
    return min(100, int(score))

def generate_adaptive_truth_statements(analysis: Dict, patterns: List[str], trend: Dict, intensity: float) -> List[str]:
    statements = []
    
    if not analysis:
        return ["You have no study data. Start logging before demanding insights."]
    
    # Trend-aware statements
    if trend.get('trend') == 'improving':
        if intensity < 1.0:
            statements.append("You're improving, but don't get complacent. Consistency beats intensity.")
        else:
            statements.append(f"Improvement detected (+{trend.get('magnitude', 0):.1f} points). Keep this momentum.")
    
    elif trend.get('trend') == 'declining':
        statements.append(f"Performance declining (-{trend.get('magnitude', 0):.1f} points). This is your warning sign.")
    
    # Recent data with intensity adjustment
    if 'recent_total_hours' in analysis:
        if analysis['recent_total_hours'] < 5:
            if intensity > 1.5:
                statements.append("Last 7 days: less than 5 hours. Are you even trying?")
            else:
                statements.append("Last 7 days: less than 5 hours. You need to show up.")
        elif analysis['recent_total_hours'] < 15:
            if intensity > 1.2:
                statements.append(f"Your last 7 days show {analysis['recent_total_hours']:.1f} hours. Pathetic.")
            else:
                statements.append(f"Your last 7 days show {analysis['recent_total_hours']:.1f} hours. Room for improvement.")
    
    # Streak-based with adaptive tone
    if 'current_streak' in analysis:
        if analysis['current_streak'] == 0:
            if intensity > 1.5:
                statements.append("Zero day streak. You've lost all discipline.")
            else:
                statements.append("Current streak: 0. Time to rebuild.")
        elif analysis['current_streak'] < 3:
            statements.append(f"Streak of {analysis['current_streak']} days? That's barely starting.")
    
    # Weakest subject with trend context
    if 'recent_most_ignored' in analysis:
        ignored = analysis['recent_most_ignored']
        if trend.get('trend') == 'improving':
            statements.append(f"You're improving overall, but still ignoring {ignored}. Fix this blind spot.")
        else:
            statements.append(f"Your most ignored subject: {ignored}. This is holding you back.")
    
    # Pattern-specific with intensity
    if "hard_subject_avoidance" in patterns:
        if intensity > 1.3:
            statements.append("You avoid hard subjects like they're poison. Growth requires pain.")
        else:
            statements.append("Focus more on difficult subjects to accelerate growth.")
    
    if "fake_consistency" in patterns:
        if intensity > 1.4:
            statements.append("Logging short sessions doesn't make you disciplined. It makes you a fraud.")
        else:
            statements.append("Increase session quality, not just quantity.")
    
    # Comparative statements
    if 'recent_most_studied' in analysis and 'recent_most_ignored' in analysis:
        if analysis['recent_most_studied'] != analysis['recent_most_ignored']:
            if intensity > 1.2:
                statements.append(f"You favor {analysis['recent_most_studied']} while avoiding {analysis['recent_most_ignored']}. Cowardly.")
            else:
                statements.append(f"Balance your focus between {analysis['recent_most_studied']} and {analysis['recent_most_ignored']}.")
    
    return statements

def mirror_chat(df: pd.DataFrame, user_input: str) -> str:
    from analysis import analyze_study_data, detect_behavioral_patterns
    
    user_input = user_input.lower().strip()
    
    if df.empty:
        return "No data to analyze. Log your study sessions first."
    
    analysis = analyze_study_data(df)
    patterns = detect_behavioral_patterns(analysis)
    trend = get_behavior_trend(df)
    scores = {
        'reality_score': calculate_reality_score(analysis),
        'discipline_score': calculate_discipline_score(analysis),
        'avoidance_score': calculate_avoidance_score(analysis)
    }
    intensity = calculate_adaptive_intensity(scores, trend)
    
    # Why am I failing?
    if "why" in user_input and ("fail" in user_input or "failing" in user_input):
        reasons = []
        
        if 'consistency' in analysis and analysis['consistency'] < 50:
            if intensity > 1.3:
                reasons.append(f"Your consistency is {analysis['consistency']:.1f}% - pathetic")
            else:
                reasons.append(f"Your consistency is {analysis['consistency']:.1f}% - needs work")
        
        if 'current_streak' in analysis and analysis['current_streak'] == 0:
            reasons.append("Zero day streak - no discipline")
        
        if "hard_subject_avoidance" in patterns:
            reasons.append("You avoid difficult subjects completely")
        
        if 'recent_total_hours' in analysis and analysis['recent_total_hours'] < 10:
            reasons.append(f"Last 7 days: only {analysis['recent_total_hours']:.1f} hours")
        
        if trend.get('trend') == 'declining':
            reasons.append("Your performance is declining")
        
        if reasons:
            return "You're failing because: " + ". ".join(reasons) + "."
        else:
            return "Your data doesn't show failure yet, but your trajectory isn't impressive."
    
    # How do I improve?
    elif "how" in user_input and ("improve" in user_input or "better" in user_input):
        suggestions = []
        
        if trend.get('trend') == 'improving':
            suggestions.append("Continue what's working - increase intensity")
        elif trend.get('trend') == 'declining':
            suggestions.append("Reverse the decline - double your consistency")
        
        if 'consistency' in analysis and analysis['consistency'] < 60:
            suggestions.append("Study daily, not when you 'feel like it'")
        
        if 'current_streak' in analysis and analysis['current_streak'] < 3:
            suggestions.append("Build a 7-day streak first")
        
        if "hard_subject_avoidance" in patterns:
            suggestions.append("Spend 30 minutes daily on your hardest subject")
        
        if 'recent_most_ignored' in analysis:
            suggestions.append(f"Focus on {analysis['recent_most_ignored']} - it's dragging you down")
        
        if suggestions:
            return "Improvement requires: " + ". ".join(suggestions) + "."
        else:
            return "Stop seeking advice and start executing consistently."
    
    # Am I consistent?
    elif "consistent" in user_input or "consistency" in user_input:
        if 'consistency' in analysis:
            cons = analysis['consistency']
            if trend.get('trend') == 'improving':
                prefix = "Your consistency is improving: "
            elif trend.get('trend') == 'declining':
                prefix = "Your consistency is declining: "
            else:
                prefix = "Your consistency is: "
            
            if cons >= 80:
                return f"{prefix}{cons:.1f}% - actually decent for once."
            elif cons >= 60:
                return f"{prefix}{cons:.1f}% - mediocre, but not hopeless."
            elif cons >= 40:
                return f"{prefix}{cons:.1f}% - barely trying."
            else:
                return f"{prefix}{cons:.1f}% - you're inconsistent by definition."
        
        return "Can't determine consistency - insufficient data."
    
    # What's my biggest problem?
    elif "problem" in user_input or "issue" in user_input or "wrong" in user_input:
        if "hard_subject_avoidance" in patterns:
            return "Your biggest problem: avoiding difficult subjects. Growth requires discomfort."
        elif 'consistency' in analysis and analysis['consistency'] < 40:
            return "Your biggest problem: inconsistency. You show up randomly and expect results."
        elif 'current_streak' in analysis and analysis['current_streak'] == 0:
            return "Your biggest problem: zero discipline. No streak, no progress."
        elif "fake_consistency" in patterns:
            return "Your biggest problem: fake productivity. Many short sessions, no real learning."
        elif trend.get('trend') == 'declining':
            return "Your biggest problem: declining performance. You're getting worse."
        else:
            return "Your biggest problem: asking questions instead of studying."
    
    # Default response
    else:
        if trend.get('trend') == 'improving':
            return f"You're improving, but {analysis.get('recent_total_hours', 0):.1f} hours in 7 days isn't impressive yet."
        elif trend.get('trend') == 'declining':
            return "You're declining. Fix this before it becomes permanent."
        elif 'recent_total_hours' in analysis and analysis['recent_total_hours'] < 5:
            return f"You studied {analysis['recent_total_hours']:.1f} hours in 7 days. Stop asking questions and start studying."
        elif 'current_streak' in analysis and analysis['current_streak'] == 0:
            return "Your streak is zero. Fix that before asking for advice."
        else:
            return "Your data shows the answer. Look at your patterns instead of seeking validation."

def analyze_behavior(df: pd.DataFrame) -> Dict:
    from analysis import analyze_study_data, detect_behavioral_patterns
    
    analysis = analyze_study_data(df)
    patterns = detect_behavioral_patterns(analysis)
    trend = get_behavior_trend(df)
    
    scores = {
        'reality_score': calculate_reality_score(analysis),
        'discipline_score': calculate_discipline_score(analysis),
        'avoidance_score': calculate_avoidance_score(analysis)
    }
    
    intensity = calculate_adaptive_intensity(scores, trend)
    
    # Save current scores to history
    history = load_score_history()
    history.append(scores)
    if len(history) > 10:  # Keep only last 10 entries
        history = history[-10:]
    save_score_history(history)
    
    return {
        'truth_statements': generate_adaptive_truth_statements(analysis, patterns, trend, intensity),
        'patterns': patterns,
        'scores': scores,
        'trend': trend,
        'intensity': intensity,
        'analysis': analysis
    }
