from fastapi import FastAPI, HTTPException  # type: ignore
from pydantic import BaseModel  # type: ignore
from typing import List, Dict
import random
import re
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

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
    # Math - Basic & Advanced
    "what is a prime number": "A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself. Examples include 2, 3, 5, 7, 11.",
    "define prime number": "A prime number is a number greater than 1 that can only be divided evenly by 1 and itself.",
    "what is a fraction": "A fraction represents a part of a whole and is written as one number over another, like 1/2 or 3/4.",
    "what is addition": "Addition is the mathematical process of putting things together to get a total or sum.",
    "what is subtraction": "Subtraction means taking one quantity away from another.",
    "what is multiplication": "Multiplication is repeated addition of the same number multiple times.",
    "what is division": "Division is splitting a number into equal parts or groups.",
    "what is an equation": "An equation is a mathematical statement that asserts the equality of two expressions, like 2x + 3 = 7.",
    "what is an average": "The average is found by adding all the numbers and dividing by the total count of numbers.",
    "what is percentage": "A percentage is a number or ratio expressed as a fraction of 100. For example, 50% means 50 out of 100.",
    "what is pythagoras theorem": "The Pythagorean theorem states that in a right-angled triangle, a² + b² = c², where c is the hypotenuse.",
    "what is perimeter": "Perimeter is the total distance around the edge of a two-dimensional shape.",
    "what is area": "Area is the measure of the space inside a two-dimensional shape, like length × breadth for a rectangle.",

    # Science - Basic & Advanced
    "what is an atom": "An atom is the smallest unit of ordinary matter that forms a chemical element. It consists of protons, neutrons, and electrons.",
    "define atom": "An atom is the basic building block of matter.",
    "what is photosynthesis": "Photosynthesis is the process by which green plants use sunlight to make their own food from carbon dioxide and water.",
    "what is gravity": "Gravity is a force that attracts two bodies towards each other. It's what keeps us on the ground.",
    "what is matter": "Matter is anything that has mass and takes up space.",
    "what is energy": "Energy is the capacity to do work or cause change.",
    "what is force": "Force is a push or pull on an object that can cause it to move or change its shape.",
    "what is newton's first law": "Newton's First Law states that an object will remain at rest or in uniform motion unless acted upon by an external force.",
    "what is a cell": "A cell is the basic structural, functional, and biological unit of all living organisms.",
    "what is the solar system": "The solar system consists of the Sun and the celestial objects bound to it by gravity, including eight planets and their moons.",
    "what is respiration": "Respiration is the process by which organisms convert glucose and oxygen into energy, carbon dioxide, and water.",
    "what is digestion": "Digestion is the process of breaking down food into nutrients that the body can use.",
    "what is pollution": "Pollution is the introduction of harmful substances into the environment that cause adverse effects.",

    # English - Basic & Advanced
    "what is a noun": "A noun is a word that names a person, place, thing, or idea.",
    "what is a verb": "A verb is a word that describes an action or state.",
    "what is an adjective": "An adjective is a word that describes a noun or pronoun.",
    "what is a pronoun": "A pronoun is a word used in place of a noun, like he, she, it, or they.",
    "what is a sentence": "A sentence is a group of words that expresses a complete thought.",
    "what is a paragraph": "A paragraph is a group of related sentences that discuss one main idea.",
    "what is a synonym": "A synonym is a word that has the same or similar meaning as another word.",
    "what is an antonym": "An antonym is a word that means the opposite of another word.",
    "what is a conjunction": "A conjunction is a word that connects words, phrases, or clauses. Examples: and, but, or.",
    "what is punctuation": "Punctuation refers to symbols like periods, commas, and question marks that help structure sentences.",

    # General Knowledge (GK)
    "who is the president of india": "As of 2025, the President of India is Droupadi Murmu.",
    "who is the prime minister of india": "As of 2025, the Prime Minister of India is Narendra Modi.",
    "what is the capital of india": "The capital of India is New Delhi.",
    "how many states are there in india": "There are 28 states and 8 Union Territories in India.",
    "what is the national animal of india": "The national animal of India is the Bengal Tiger.",
    "what is the national bird of india": "The national bird of India is the Indian Peacock.",
    "what is the national flower of india": "The national flower of India is the Lotus.",
    "when is independence day celebrated": "Independence Day is celebrated on August 15th every year.",
    "when is republic day celebrated": "Republic Day is celebrated on January 26th every year.",
    "what is the currency of india": "The currency of India is the Indian Rupee (INR)."
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
