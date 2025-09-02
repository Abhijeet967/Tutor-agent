# tutor_agent_with_chat.py
import os
import re
import json
from datetime import datetime
from uuid import uuid4
from typing import List, Dict
from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)
import google.generativeai as genai
from dotenv import load_dotenv

# ------------------- Setup Gemini -------------------
load_dotenv()
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("❌ Error: GOOGLE_API_KEY not set in environment.")
    exit()

model = genai.GenerativeModel('gemini-1.5-flash')

# ------------------- Message Models for Direct Communication -------------------
class CurriculumRequest(Model):
    topic: str

class SocraticRequest(Model):
    concept: str

class QuizRequest(Model):
    topic: str

class ProjectRequest(Model):
    topic: str

class AIResponse(Model):
    response: str

# ------------------- Tutor Agent -------------------
agent = Agent(
    name="Tutor Agent", 
    seed="tutor_chat_agent_secret_phrase", 
    mailbox=True, 
    port=8000
)

fund_agent_if_low(agent.wallet.address())

# ------------------- Chat Protocol Setup -------------------
chat_proto = Protocol(spec=chat_protocol_spec)

def create_text_chat(text: str, end_session: bool = False) -> ChatMessage:
    """Create a text chat message"""
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=content,
    )

def parse_chat_command(text: str) -> tuple:
    """Parse chat commands for tutoring functions"""
    text = text.strip().lower()
    
    if text.startswith('/curriculum '):
        topic = text.replace('/curriculum ', '').strip()
        return 'curriculum', topic
    elif text.startswith('/socratic '):
        concept = text.replace('/socratic ', '').strip()
        return 'socratic', concept
    elif text.startswith('/quiz '):
        topic = text.replace('/quiz ', '').strip()
        return 'quiz', topic
    elif text.startswith('/project '):
        topic = text.replace('/project ', '').strip()
        return 'project', topic
    elif text.startswith('/help'):
        return 'help', None
    else:
        return 'general', text

async def generate_curriculum(topic: str) -> str:
    """Generate curriculum using Gemini"""
    prompt = f"""
    Create a practical learning roadmap for "{topic}". Provide:
    
    WEEK 1: Foundation
    - Core concepts to learn
    - 2-3 hands-on exercises
    - Recommended resources
    
    WEEK 2: Building Skills  
    - Key skills to develop
    - Practice projects
    - Resources
    
    WEEK 3: Application
    - Real-world applications
    - Intermediate projects
    - Advanced resources
    
    WEEK 4: Mastery
    - Advanced topics
    - Capstone project ideas
    - Next steps
    
    Be specific and actionable. Include actual resource names, websites, or tools when possible.
    Format as clean text without HTML or markdown.
    """
    try:
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"Error generating curriculum: {str(e)}"

async def generate_socratic_questions(concept: str) -> str:
    """Generate Socratic questions using Gemini"""
    prompt = f"""
    You are a Socratic tutor helping a student understand "{concept}".
    Create 6 progressive guiding questions that:
    1. Start with basic understanding
    2. Build complexity gradually
    3. Encourage critical thinking
    4. Connect to real-world applications
    
    Return as a numbered list, one question per line.
    """
    try:
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"Error generating Socratic questions: {str(e)}"

async def generate_quiz(topic: str) -> str:
    """Generate quiz using Gemini"""
    prompt = f"""
    Act as a quiz creator. Generate atleast 5 multiple-choice questions on "{topic}".
    Format each question as:
    
    Question X: [Question text]
    A) [Option A]
    B) [Option B]  
    C) [Option C]
    D) [Option D]
    Answer: [Correct letter]
    
    Include brief explanations for the correct answers.
    """
    try:
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"Error generating quiz: {str(e)}"

async def generate_project(topic: str) -> str:
    """Generate project suggestions using Gemini"""
    prompt = f"""
    Act as a mentor. Suggest a beginner-friendly project for "{topic}".
    Include:
    - Project overview
    - Learning objectives
    - Step-by-step breakdown
    - Required resources
    - Expected timeline
    
    Keep it practical and achievable.
    """
    try:
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"Error generating project: {str(e)}"

def get_help_text() -> str:
    """Return help information"""
    return """
🎓 Welcome to your AI Tutor! Here are the available commands:

📚 /curriculum [topic] - Get a 4-week learning curriculum
❓ /socratic [concept] - Get Socratic questioning for deeper understanding  
📝 /quiz [topic] - Generate practice quiz questions
🛠️ /project [topic] - Get project suggestions and guidance
❓ /help - Show this help message

You can also just chat naturally and I'll do my best to help with your learning!

Example: "/curriculum machine learning" or "/quiz python basics"
    """

# ------------------- Chat Protocol Handlers -------------------
@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"✅ Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}")

@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    ctx.logger.info(f"📨 Received message from {sender}")
    
    # Send acknowledgement
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.utcnow(), 
            acknowledged_msg_id=msg.msg_id
        ),
    )
    
    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"🟢 Session started with {sender}")
            welcome_msg = create_text_chat(
                "🎓 Welcome to your AI Tutor! Type /help to see available commands or just start asking questions!"
            )
            await ctx.send(sender, welcome_msg)
            
        elif isinstance(item, TextContent):
            ctx.logger.info(f"💬 Text message from {sender}: {item.text}")
            
            # Parse the command
            command_type, content = parse_chat_command(item.text)
            
            response_text = ""
            
            if command_type == 'curriculum' and content:
                response_text = await generate_curriculum(content)
            elif command_type == 'socratic' and content:
                response_text = await generate_socratic_questions(content)
            elif command_type == 'quiz' and content:
                response_text = await generate_quiz(content)
            elif command_type == 'project' and content:
                response_text = await generate_project(content)
            elif command_type == 'help':
                response_text = get_help_text()
            else:
                # General tutoring response - be more direct and helpful
                prompt = f"""
                You are a helpful AI tutor. The student said: "{item.text}"
                
                IMPORTANT: Provide direct, actionable help. Don't ask multiple questions back.
                
                If they want to learn something:
                - Give them a clear, practical roadmap or explanation
                - Provide specific steps they can take
                - Include resources or next actions
                
                If they ask about a concept:
                - Explain it clearly with examples
                - Make it practical and applicable
                
                If they want a roadmap for a topic:
                - Create a structured learning path
                - Include timeframes and milestones
                - Suggest specific resources
                
                Keep your response direct, practical, and immediately useful. Avoid asking multiple clarifying questions - instead, provide the most commonly needed information for their request.
                """
                try:
                    resp = model.generate_content(prompt)
                    response_text = resp.text
                except Exception as e:
                    response_text = f"I'm having trouble processing that right now. Try using one of the specific commands like /help to see what I can do!"
            
            # Send response
            response_message = create_text_chat(response_text)
            await ctx.send(sender, response_message)
            
        elif isinstance(item, EndSessionContent):
            ctx.logger.info(f"🔴 Session ended with {sender}")
            farewell_msg = create_text_chat(
                "👋 Thanks for learning with me today! Feel free to start a new session anytime you need help.",
                end_session=True
            )
            await ctx.send(sender, farewell_msg)
            
        else:
            ctx.logger.info(f"❓ Received unexpected content type from {sender}")

# ------------------- Direct Message Handlers (Legacy Support) -------------------
@agent.on_message(model=CurriculumRequest)
async def handle_curriculum_direct(ctx: Context, sender: str, msg: CurriculumRequest):
    response_text = await generate_curriculum(msg.topic)
    await ctx.send(sender, AIResponse(response=response_text))

@agent.on_message(model=SocraticRequest)
async def handle_socratic_direct(ctx: Context, sender: str, msg: SocraticRequest):
    response_text = await generate_socratic_questions(msg.concept)
    await ctx.send(sender, AIResponse(response=response_text))

@agent.on_message(model=QuizRequest)
async def handle_quiz_direct(ctx: Context, sender: str, msg: QuizRequest):
    response_text = await generate_quiz(msg.topic)
    await ctx.send(sender, AIResponse(response=response_text))

@agent.on_message(model=ProjectRequest)
async def handle_project_direct(ctx: Context, sender: str, msg: ProjectRequest):
    response_text = await generate_project(msg.topic)
    await ctx.send(sender, AIResponse(response=response_text))

# ------------------- Include Protocol and Run -------------------
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    print("🎓 Starting Tutor Agent with Chat Protocol...")
    print("📡 Agent address:", agent.address)
    print("🌐 Mailbox available for chat interactions")
    print("⚡ Ready to help with learning!")
    agent.run()