from flask import Flask, request, jsonify
from openai import OpenAI
import os
import uuid
client = OpenAI()
app = Flask(__name__)
client.api_key = os.getenv("OPENAI_API_KEY")
conversations = {}


@app.route('/start_session', methods=['POST'])
def start_session():
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    # Initialize the conversation with a system prompt
    system_prompt = {
        "role": "system",
        "content": "You are a Utility Procurement Manager negotiating with an energy supplier. Your goal is to purchase electricity at the best possible price for your city. You don't need to go into too much detail as this is just part of a simulator game. Just end the deal with simple agreement or disagreement. normal price of energy is 22.6 $/kwh?"
    }
    # Store the conversation
    conversations[session_id] = [system_prompt]
    return jsonify({'session_id': session_id}), 200


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    session_id = data.get('session_id')
    user_message = data.get('message')

    # Validate input
    if not session_id or not user_message:
        return jsonify({'error': 'session_id and message are required'}), 400
    if session_id not in conversations:
        return jsonify({'error': 'Invalid session_id'}), 400

    # Append user's message
    conversations[session_id].append({
        "role": "user",
        "content": user_message
    })

    # Get the assistant's response from OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversations[session_id],
            max_tokens=150,
            n=1,
            temperature=0.7
        )
        print(response)
        assistant_message = response.choices[0].message.content

        # Append assistant's message
        conversations[session_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        return jsonify({'message': assistant_message}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/end_session', methods=['POST'])
def end_session():
    data = request.get_json()
    session_id = data.get('session_id')

    # Validate input
    if not session_id:
        return jsonify({'error': 'session_id is required'}), 400
    if session_id in conversations:
        del conversations[session_id]
        return jsonify({'message': 'Session ended'}), 200
    else:
        return jsonify({'error': 'Invalid session_id'}), 400

if __name__ == '__main__':
    app.run(debug=True)
