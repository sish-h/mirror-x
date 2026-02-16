import pandas as pd
from tabulate import tabulate
from data import initialize_csv, log_study_session, load_study_data, get_available_subjects
from mirror import analyze_behavior, mirror_chat
from visual import plot_subject_distribution, plot_daily_hours

def display_menu():
    print("\n" + "="*60)
    print("           MIRROR-X STUDY INTELLIGENCE SYSTEM")
    print("="*60)
    print("1. Log Study Session")
    print("2. View Analysis")
    print("3. Ask Mirror-X")
    print("4. Exit")
    print("="*60)

def log_study():
    print("\n" + "-"*50)
    print("           LOG STUDY SESSION")
    print("-"*50)
    subjects = get_available_subjects()
    
    print("Available subjects:")
    for i, subject in enumerate(subjects, 1):
        print(f"{i}. {subject}")
    
    try:
        choice = int(input("Select subject (1-7): ")) - 1
        if choice < 0 or choice >= len(subjects):
            print("Invalid subject choice.")
            return
        
        subject = subjects[choice]
        
        hours = float(input("Hours studied (0-12): "))
        if hours < 0 or hours > 12:
            print("Invalid hours. Must be between 0 and 12.")
            return
        
        print("Difficulty levels:")
        print("1. Easy")
        print("2. Medium")
        print("3. Hard")
        
        diff_choice = int(input("Select difficulty (1-3): "))
        difficulty_map = {1: 'easy', 2: 'medium', 3: 'hard'}
        difficulty = difficulty_map.get(diff_choice)
        
        if not difficulty:
            print("Invalid difficulty choice.")
            return
        
        if log_study_session(subject, hours, difficulty):
            print(f"\n✓ SESSION LOGGED: {subject} - {hours} hours - {difficulty}")
        else:
            print("✗ Failed to log session.")
            
    except ValueError:
        print("✗ Invalid input. Please enter numbers only.")

def calculate_performance_grade(scores):
    avg_score = (scores['reality_score'] + scores['discipline_score'] + (100 - scores['avoidance_score'])) / 3
    
    if avg_score >= 85:
        return "A", "EXCELLENT"
    elif avg_score >= 70:
        return "B", "GOOD"
    elif avg_score >= 55:
        return "C", "AVERAGE"
    elif avg_score >= 40:
        return "D", "POOR"
    else:
        return "F", "CRITICAL"

def get_dominant_behavior(patterns):
    if not patterns:
        return "None Detected"
    
    behavior_map = {
        'hard_subject_avoidance': 'Avoidance',
        'fake_consistency': 'Inconsistent',
        'spike_then_crash': 'Unstable',
        'over_focus_easy': 'Comfort-Seeking',
        'lack_balance': 'Unfocused',
        'irregular_study': 'Discipline-Lacking'
    }
    
    for pattern in patterns:
        if pattern in behavior_map:
            return behavior_map[pattern]
    
    return "Mixed"

def get_risk_level(scores, patterns):
    risk_score = 0
    
    if scores['reality_score'] < 40:
        risk_score += 2
    elif scores['reality_score'] < 60:
        risk_score += 1
    
    if scores['discipline_score'] < 40:
        risk_score += 2
    elif scores['discipline_score'] < 60:
        risk_score += 1
    
    if scores['avoidance_score'] > 60:
        risk_score += 2
    elif scores['avoidance_score'] > 40:
        risk_score += 1
    
    if 'hard_subject_avoidance' in patterns:
        risk_score += 1
    
    if 'spike_then_crash' in patterns:
        risk_score += 1
    
    if risk_score >= 4:
        return "CRITICAL"
    elif risk_score >= 3:
        return "HIGH"
    elif risk_score >= 2:
        return "MODERATE"
    elif risk_score >= 1:
        return "LOW"
    else:
        return "MINIMAL"

def view_analysis():
    print("\n" + "="*60)
    print("              STUDY PERFORMANCE ANALYSIS")
    print("="*60)
    
    data = load_study_data()
    if not data:
        print("⚠ No study data found. Start logging sessions first.")
        return
    
    df = pd.DataFrame(data)
    
    # Display study data table
    print("\nSTUDY SESSIONS LOG:")
    print(tabulate(df[['date', 'subject', 'hours', 'difficulty']], 
                  headers=['Date', 'Subject', 'Hours', 'Difficulty'], 
                  tablefmt='grid', showindex=False))
    
    # Show visualizations
    print("\n" + "-"*40)
    print("Generating performance visualizations...")
    print("-"*40)
    plot_subject_distribution(df)
    plot_daily_hours(df)
    
    # Get mirror analysis
    result = analyze_behavior(df)
    scores = result['scores']
    patterns = result['patterns']
    analysis = result['analysis']
    
    # Performance Grade Section
    grade, grade_text = calculate_performance_grade(scores)
    print("\n" + "="*60)
    print("                 PERFORMANCE GRADE")
    print("="*60)
    print(f"           GRADE: {grade} - {grade_text}")
    print("="*60)
    
    # Scores Section
    print("\n" + "-"*60)
    print("                    PERFORMANCE METRICS")
    print("-"*60)
    print(f"Reality Score:     {scores['reality_score']:3d}/100  {'✓' if scores['reality_score'] > 60 else '✗'}")
    print(f"Discipline Score:  {scores['discipline_score']:3d}/100  {'✓' if scores['discipline_score'] > 60 else '✗'}")
    print(f"Avoidance Score:   {scores['avoidance_score']:3d}/100  {'✗' if scores['avoidance_score'] < 40 else '⚠'}")
    print("-"*60)
    
    # Profile Analysis Section
    consistency = analysis.get('consistency', 0)
    dominant_behavior = get_dominant_behavior(patterns)
    risk_level = get_risk_level(scores, patterns)
    
    print("\n" + "="*60)
    print("                 PROFILE ANALYSIS")
    print("="*60)
    print(f"Consistency:     {consistency:.1f}% ({'Strong' if consistency > 70 else 'Moderate' if consistency > 40 else 'Weak'})")
    print(f"Dominant Behavior: {dominant_behavior}")
    print(f"Risk Level:        {risk_level}")
    print("="*60)
    
    # Patterns Detected Section
    if patterns:
        print("\n" + "-"*60)
        print("                  BEHAVIORAL PATTERNS")
        print("-"*60)
        pattern_names = {
            'over_focus_easy': '⚠ Hiding in Easy Subjects',
            'lack_balance': '⚠ Unbalanced Study Approach',
            'irregular_study': '⚠ Inconsistent Schedule',
            'hard_subject_avoidance': '⚠ Avoiding Hard Subjects',
            'fake_consistency': '⚠ Fake Consistency Pattern',
            'spike_then_crash': '⚠ Spike Then Crash Pattern'
        }
        for pattern in patterns:
            print(f"  {pattern_names.get(pattern, f'⚠ {pattern}')}")
        print("-"*60)
    
    # Truth Statements Section
    if result['truth_statements']:
        print("\n" + "="*60)
        print("                  BRUTAL TRUTH ANALYSIS")
        print("="*60)
        for i, statement in enumerate(result['truth_statements'], 1):
            print(f"{i}. {statement}")
        print("="*60)
    
    # Summary Statistics Section
    if analysis:
        print("\n" + "-"*60)
        print("                    PERFORMANCE SUMMARY")
        print("-"*60)
        print(f"Total Study Hours:     {analysis.get('total_hours', 0):.1f}")
        print(f"Total Sessions:        {analysis.get('total_sessions', 0)}")
        print(f"Average per Session:   {analysis.get('avg_hours_per_session', 0):.1f} hours")
        print(f"Current Streak:        {analysis.get('current_streak', 0)} days")
        print(f"Missed Days:           {analysis.get('missed_days', 0)}")
        
        if 'subject_hours' in analysis:
            print(f"\nSubject Distribution:")
            for subject, hours in analysis['subject_hours'].items():
                print(f"  • {subject}: {hours:.1f} hours")
        
        if 'recent_total_hours' in analysis:
            print(f"\nRecent Performance (Last 7 Days):")
            print(f"  • Hours: {analysis['recent_total_hours']:.1f}")
            print(f"  • Sessions: {analysis.get('recent_sessions', 0)}")
        
        print("-"*60)

def ask_mirror():
    print("\n" + "="*60)
    print("              MIRROR-X INTELLIGENCE CHAT")
    print("="*60)
    print("Type 'back' to return to menu")
    print("-"*60)
    
    data = load_study_data()
    if not data:
        print("⚠ No study data found. Start logging sessions first.")
        return
    
    df = pd.DataFrame(data)
    
    while True:
        user_input = input("\n❓ Your question: ").strip()
        
        if user_input.lower() == 'back':
            break
        
        if not user_input:
            continue
        
        response = mirror_chat(df, user_input)
        print(f"\n🤖 Mirror-X: {response}")

def main():
    initialize_csv()
    
    while True:
        display_menu()
        
        try:
            choice = int(input("Enter your choice (1-4): "))
            
            if choice == 1:
                log_study()
            elif choice == 2:
                view_analysis()
            elif choice == 3:
                ask_mirror()
            elif choice == 4:
                print("\n" + "="*60)
                print("         MIRROR-X: Face your data. Change your patterns.")
                print("="*60)
                break
            else:
                print("✗ Invalid choice. Enter 1, 2, 3, or 4.")
                
        except ValueError:
            print("✗ Invalid input. Enter a number.")

if __name__ == "__main__":
    main()
