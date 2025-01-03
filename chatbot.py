from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import os

app = Flask(__name__)

# Load the dataset
data = pd.read_csv("C:\\Users\\bomar\\Downloads\\chat\\merged_lstm_predictions_tableau.csv")

@app.route('/')
def home():
    # Serve the index.html file from the current directory
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/query', methods=['POST'])
def query():
    user_input = request.json['message'].lower()

    # Handle generic questions
    if user_input in ["hi", "hello", "hey"]:
        response = "Hello! How can I assist you today?"
    elif "how are you" in user_input:
        response = "I'm just a chatbot, but I'm here to help you with your projects!"
    elif "thank you" in user_input or "thanks" in user_input:
        response = "You're welcome! Let me know if you need any further assistance."
    elif "help" in user_input:
        response = "Sure, I can help you with project progress, risks, or mitigation details. Try asking about a project or listing available projects."
    elif "who are you" in user_input:
        response = "I'm your Traxidy Chatbot, here to assist with your project management needs."
    elif "what can you do" in user_input:
        response = "I can provide insights on project progress, predicted risks, and mitigation suggestions. Try asking about a specific project!"
    # Handle project-specific queries
    elif "project" in user_input:
        project_id = extract_project_name(user_input)
        response = get_project_details(project_id)
    elif "progress" in user_input:
        response = "Please specify a project ID to check progress."
    elif "mitigation" in user_input or "risk" in user_input:
        response = "Please specify a project ID to get mitigation or risk details."
    else:
        response = "Sorry, I couldn't understand your query. Please ask about a specific project or feature."

    return jsonify({'response': response})

@app.route('/projects', methods=['GET'])
def get_projects():
    projects = data['project_id_x'].dropna().unique().tolist()
    return jsonify({'projects': projects})

def extract_project_name(query):
    # Extract numeric project ID from the query
    for word in query.split():
        if word.isdigit():
            return int(word)
    return None

def get_project_details(project_id):
    if project_id is None:
        return "Please specify a project ID to get details."

    project_data = data[data['project_id_x'] == project_id]
    if project_data.empty:
        return f"No data found for project {project_id}."

    # Fetch details
    total_tasks = project_data.shape[0]
    completed_tasks = project_data[project_data['status_actions'] == 'closed'].shape[0]
    average_progress = project_data['progress_actions'].mean()

    # GYR statuses and due weekday
    gyr_status = project_data['gyr_actions'].iloc[0] if 'gyr_actions' in project_data.columns else "Unknown"
    predicted_status = project_data['predicted_status_label'].iloc[0] if 'predicted_status_label' in project_data.columns else "Unknown"
    due_weekday = project_data['due_weekday'].iloc[0] if 'due_weekday' in project_data.columns else "Unknown"

    # Predicted risk and mitigations
    predicted_risk = project_data['predicted_risk_score'].mean()
    mitigations = project_data['mitigation_suggestions'].dropna().unique()

    response = (
        f"Details for project {project_id}:\n"
        f"- Total Tasks: {total_tasks}\n"
        f"- Completed Tasks: {completed_tasks}\n"
        f"- Average Progress: {average_progress:.2f}%\n"
        f"- Predicted Risk Score: {predicted_risk:.2f}\n"
        f"- GYR Status (Available): {gyr_status}\n"
        f"- Predicted GYR Status: {predicted_status}\n"
        f"- Due Weekday: {due_weekday}\n"
        f"- Mitigation Suggestions: {', '.join(mitigations)}"
    )
    return response

if __name__ == "__main__":
    app.run(debug=True)