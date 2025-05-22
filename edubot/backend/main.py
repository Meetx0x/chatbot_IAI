from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import random
import re
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Educational Chatbot for Rural Students")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================= Models =======================
class Message(BaseModel):
    role: str  # "user" or "bot"
    content: str

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    response: str
    conversation_history: List[Message]

# ======================= Data Store =======================
conversations: Dict[str, List[Message]] = {}

# ======================= FAQ Knowledge Base =======================
faq_knowledge = {
    # Math
    "what is a prime number": "A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself. Examples include 2, 3, 5, 7, 11.",
    "define prime number": "A prime number is a number greater than 1 that can only be divided evenly by 1 and itself.",
    "what is a fraction": "A fraction represents a part of a whole and is written as one number over another, like 1/2 or 3/4.",
    "what is addition": "Addition is the mathematical process of putting things together to get a total or sum.",
    "what is subtraction": "Subtraction means taking one quantity away from another.",
    "what is multiplication": "Multiplication is repeated addition of the same number multiple times.",
    "what is division": "Division is splitting a number into equal parts or groups.",
    # Science
    "what is an atom": "An atom is the smallest unit of ordinary matter that forms a chemical element. It consists of protons, neutrons, and electrons.",
    "define atom": "An atom is the basic building block of matter.",
    "what is photosynthesis": "Photosynthesis is the process by which green plants use sunlight to make their own food from carbon dioxide and water.",
    "what is gravity": "Gravity is a force that attracts two bodies towards each other. It's what keeps us on the ground.",
    "what is matter": "Matter is anything that has mass and takes up space.",
    "what is energy": "Energy is the capacity to do work or cause change.",
    # English / General
    "what is a noun": "A noun is a word that names a person, place, thing, or idea.",
    "what is a verb": "A verb is a word that describes an action or state.",
}

# ======================= Regex Pattern-Based Responses =======================
responses = {
    r'hi|hello|hey': [
        "Hello! How can I help you today?",
        "Hi there! What can I do for you?",
        "Hey! How's it going?"
    ],
    r'how are you': [
        "I'm doing well, thanks for asking!",
        "I'm great! How about you?",
        "All systems operational! How can I assist you?"
    ],
    r'bye|goodbye': [
        "Goodbye! Have a great day!",
        "See you later!",
        "Bye for now!"
    ],
    r'thank you|thanks': [
        "You're welcome!",
        "Happy to help!",
        "Anytime!"
    ],
    r'help': [
        "I'm here to assist with your studies! Ask me anything about math, science, or English.",
        "Sure! I can help answer your educational questions."
    ],
    r'error|issue': [
        "Looks like you're facing an issue. Could you explain it in more detail?",
        "Let me know what problem you're facing. I'll do my best to help!"
    ]
}

default_responses = [
    "I'm not sure I understand. Could you rephrase that?",
    "I don't have an answer for that yet.",
    "That's interesting, but I'm not sure how to respond."
]

# ======================= Bot Response Logic =======================
def generate_bot_response(user_input: str) -> str:
    user_input_lower = user_input.lower().strip()

    # First: Check FAQ knowledge base (exact or partial match)
    for question, answer in faq_knowledge.items():
        if question in user_input_lower:
            return answer

    # Second: Check regex pattern-based responses
    for pattern, replies in responses.items():
        if re.search(pattern, user_input_lower):
            return random.choice(replies)

    # Default fallback
    return random.choice(default_responses)

# ======================= Endpoints =======================
@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Chatbot is online!"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    user_id = req.user_id
    user_message = Message(role="user", content=req.message)

    bot_reply = generate_bot_response(req.message)
    bot_message = Message(role="bot", content=bot_reply)

    if user_id not in conversations:
        conversations[user_id] = []
    conversations[user_id].extend([user_message, bot_message])

    return ChatResponse(
        response=bot_reply,
        conversation_history=conversations[user_id]
    )

@app.get("/history/{user_id}", response_model=List[Message])
def get_history(user_id: str):
    if user_id not in conversations:
        raise HTTPException(status_code=404, detail="User not found")
    return conversations[user_id]

@app.delete("/reset/{user_id}")
def reset_conversation(user_id: str):
    if user_id in conversations:
        conversations[user_id] = []
        return {"message": f"Conversation for user '{user_id}' has been reset."}
    else:
        return {"message": f"No conversation history found for user '{user_id}'."}
