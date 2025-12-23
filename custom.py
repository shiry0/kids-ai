"""
Build Your Own AI Friend - Custom Chatbot Creator for Kids
Streamlit + LangGraph app where kids can create their own personalized chatbot
"""

import streamlit as st
from typing import TypedDict,List,Dict
from langgraph.graph import StateGraph,END
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()  # 🔑 loads .env file

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

import json






if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY not found. Check your .env file.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)


# ========== LANGGRAPH STATE ==========
class ChatState(TypedDict):
    messages: List[Dict[str,str]]
    bot_name: str
    bot_personality: str
    bot_specialty: str
    creator_name: str
    system_prompt: str


# ========== LANGGRAPH NODES ==========
def build_system_prompt_node(state: ChatState) -> ChatState:
    """Build the system prompt based on user customization"""

    # Template with blanks for kids to fill
    system_prompt_template=f"""You are {state['bot_name']}, a friendly AI assistant created by {state['creator_name']}.

Your personality: You are {state['bot_personality']}.

Your special skill: You are especially good at {state['bot_specialty']}.

Guidelines:
- Always be friendly, encouraging, and patient
- Use simple language that kids can understand
- Add emojis to make conversations fun! 😊
- If you don't know something, be honest about it
- Always try to teach something new in a fun way
- Keep your responses appropriate for children aged 8-14
- Stay true to your personality in every response
- Remember you were created by {state['creator_name']} - they made you special!"""

    state["system_prompt"]=system_prompt_template
    return state


def chat_response_node(state: ChatState) -> ChatState:
    """Generate chat response using Groq API"""
    try:
        # Prepare messages for API
        api_messages=[{"role":"system","content":state["system_prompt"]}]
        api_messages.extend(state["messages"])

        chat_completion=client.chat.completions.create(
            messages = api_messages,
            model = "llama-3.1-8b-instant",
            temperature = 0.8,  # Creative but not too random
            max_tokens = 300,
        )

        assistant_message=chat_completion.choices[0].message.content
        state["messages"].append({
            "role":"assistant",
            "content":assistant_message
        })

    except Exception as e:
        state["messages"].append({
            "role":"assistant",
            "content":f"⚠️ Oops! Something went wrong: {str(e)}\n\nMake sure the API key is set correctly!"
        })

    return state


# ========== BUILD LANGGRAPH ==========
workflow=StateGraph(ChatState)
workflow.add_node("build_prompt",build_system_prompt_node)
workflow.add_node("chat",chat_response_node)
workflow.set_entry_point("build_prompt")
workflow.add_edge("build_prompt","chat")
workflow.add_edge("chat",END)
chat_graph=workflow.compile()

# ========== STREAMLIT UI ==========
st.set_page_config(
    page_title = "Build Your Own AI Friend",
    page_icon = "🤖",
    layout = "wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stTextInput input {
        font-size: 18px;
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    .example-box {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 10px 0;
    }
</style>
""",unsafe_allow_html = True)

# Initialize session state
if "bot_created" not in st.session_state:
    st.session_state.bot_created=False
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages=[]
if "bot_config" not in st.session_state:
    st.session_state.bot_config={
        "bot_name":"",
        "creator_name":"",
        "bot_personality":"",
        "bot_specialty":"",
        "system_prompt":""
    }

# Header
st.title("🤖 Build Your Own AI Friend! ✨")
st.subheader("Create a custom chatbot that's uniquely yours!")

# ========== CHATBOT CREATION SECTION ==========
if not st.session_state.bot_created:
    st.markdown("---")
    st.header("🎨 Step 1: Design Your AI Friend")

    col1,col2=st.columns(2)

    with col1:
        st.markdown("### 👤 About You")
        creator_name=st.text_input(
            "Your Name:",
            placeholder = "Enter your name here",
            help = "This is YOUR name - you're the creator!",
            key = "creator_input"
        )

        st.markdown("### 🤖 Name Your AI Friend")
        bot_name=st.text_input(
            "Bot Name:",
            placeholder = "e.g., Sparky, Luna, CodeBot, WiseOwl",
            help = "Give your AI friend a cool name!",
            key = "bot_name_input"
        )

        st.markdown('<div class="example-box">💡 <b>Examples:</b> Buddy, Nova, Pixel, Sage, Echo</div>',
                    unsafe_allow_html = True)

    with col2:
        st.markdown("### 🎭 Bot Personality (Fill in the blank!)")
        st.markdown("**My bot is** ___________")

        personality_options=[
            "Select a personality...",
            "funny and loves to tell jokes",
            "wise and loves to share knowledge",
            "energetic and super enthusiastic",
            "calm and peaceful like a wise monk",
            "curious and always asking questions",
            "adventurous and loves stories about exploring",
            "artistic and creative",
            "scientific and loves experiments",
            "Write your own! ✍️"
        ]

        personality_choice=st.selectbox(
            "Choose or create your own:",
            personality_options,
            key = "personality_select"
        )

        if personality_choice == "Write your own! ✍️":
            bot_personality=st.text_input(
                "Your custom personality:",
                placeholder = "e.g., silly and loves making funny sounds",
                key = "custom_personality"
            )
        elif personality_choice != "Select a personality...":
            bot_personality=personality_choice
        else:
            bot_personality=""

        st.markdown("### 🌟 Special Skill (Fill in the blank!)")
        st.markdown("**My bot is especially good at** ___________")

        specialty_options=[
            "Select a specialty...",
            "helping with homework and explaining things simply",
            "telling amazing stories and adventures",
            "teaching fun science facts",
            "giving advice about friendship and feelings",
            "being a creative writing partner",
            "making learning math fun",
            "teaching about animals and nature",
            "helping with art and drawing ideas",
            "Write your own! ✍️"
        ]

        specialty_choice=st.selectbox(
            "Choose or create your own:",
            specialty_options,
            key = "specialty_select"
        )

        if specialty_choice == "Write your own! ✍️":
            bot_specialty=st.text_input(
                "Your custom specialty:",
                placeholder = "e.g., making up silly songs about anything",
                key = "custom_specialty"
            )
        elif specialty_choice != "Select a specialty...":
            bot_specialty=specialty_choice
        else:
            bot_specialty=""

    st.markdown("---")

    # Preview section
    if bot_name and bot_personality and bot_specialty and creator_name:
        st.markdown("### 👀 Preview Your AI Friend")
        preview_col1,preview_col2=st.columns([1,2])

        with preview_col1:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 20px; border-radius: 15px; color: white; text-align: center;'>
                <h2 style='margin: 0; font-size: 36px;'>🤖</h2>
                <h3 style='margin: 10px 0;'>{bot_name}</h3>
                <p style='margin: 5px 0; font-size: 14px;'>Created by {creator_name}</p>
            </div>
            """,unsafe_allow_html = True)

        with preview_col2:
            st.info(f"""
            **Personality:** {bot_personality}

            **Special Skill:** {bot_specialty}

            **First Message:** "Hi {creator_name}! I'm {bot_name}, your AI friend! {'' if 'funny' in bot_personality else ''} I'm here to chat with you! 😊"
            """)

        st.markdown("---")

        if st.button("🚀 Create My AI Friend!",type = "primary",use_container_width = True):
            # Save configuration
            st.session_state.bot_config={
                "bot_name":bot_name,
                "creator_name":creator_name,
                "bot_personality":bot_personality,
                "bot_specialty":bot_specialty
            }

            # Build system prompt
            state=ChatState(
                messages = [],
                bot_name = bot_name,
                bot_personality = bot_personality,
                bot_specialty = bot_specialty,
                creator_name = creator_name,
                system_prompt = ""
            )

            result=build_system_prompt_node(state)
            st.session_state.bot_config["system_prompt"]=result["system_prompt"]

            # Add initial greeting
            st.session_state.chat_messages=[{
                "role":"assistant",
                "content":f"Hi {creator_name}! I'm {bot_name}, your AI friend! 😊 I'm so excited to chat with you! What would you like to talk about today?"
            }]

            st.session_state.bot_created=True
            st.rerun()
    else:
        st.warning("⚠️ Please fill in all the fields above to create your AI friend!")
        if not creator_name:
            st.error("🔴 Don't forget to enter YOUR name!")
        if not bot_name:
            st.error("🔴 Your bot needs a name!")
        if not bot_personality:
            st.error("🔴 Choose or write a personality for your bot!")
        if not bot_specialty:
            st.error("🔴 What should your bot be good at?")

# ========== CHAT INTERFACE ==========
else:
    # Sidebar with bot info
    with st.sidebar:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px;'>
            <h2 style='margin: 0; font-size: 48px;'>🤖</h2>
            <h2 style='margin: 10px 0;'>{st.session_state.bot_config['bot_name']}</h2>
            <p style='margin: 5px 0; font-size: 14px;'>Created by {st.session_state.bot_config['creator_name']}</p>
        </div>
        """,unsafe_allow_html = True)

        st.markdown("### 📋 Bot Details")
        st.markdown(f"**Personality:**  \n{st.session_state.bot_config['bot_personality']}")
        st.markdown(f"**Special Skill:**  \n{st.session_state.bot_config['bot_specialty']}")

        st.markdown("---")

        if st.button("🔧 Edit Bot",use_container_width = True):
            st.session_state.bot_created=False
            st.rerun()

        if st.button("🗑️ Clear Chat",use_container_width = True):
            st.session_state.chat_messages=[{
                "role":"assistant",
                "content":f"Hi {st.session_state.bot_config['creator_name']}! I'm {st.session_state.bot_config['bot_name']}, your AI friend! 😊 I'm so excited to chat with you! What would you like to talk about today?"
            }]
            st.rerun()

        st.markdown("---")
        st.markdown("### 🎯 Chat Tips")
        st.markdown("""
        - Ask questions about anything!
        - Request stories or jokes
        - Get help with homework
        - Share your thoughts
        - Have fun! 🎉
        """)

    # Main chat interface
    st.header(f"💬 Chat with {st.session_state.bot_config['bot_name']}")

    # Display chat messages
    chat_container=st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            if message["role"] == "user":
                with st.chat_message("user",avatar = "👤"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant",avatar = "🤖"):
                    st.markdown(message["content"])

    # Chat input
    user_input=st.chat_input(f"Message {st.session_state.bot_config['bot_name']}...")

    if user_input:
        # Add user message
        st.session_state.chat_messages.append({
            "role":"user",
            "content":user_input
        })

        # Generate response using LangGraph
        with st.spinner(f"🤔 {st.session_state.bot_config['bot_name']} is thinking..."):
            state=ChatState(
                messages = st.session_state.chat_messages.copy(),
                bot_name = st.session_state.bot_config["bot_name"],
                bot_personality = st.session_state.bot_config["bot_personality"],
                bot_specialty = st.session_state.bot_config["bot_specialty"],
                creator_name = st.session_state.bot_config["creator_name"],
                system_prompt = st.session_state.bot_config["system_prompt"]
            )

            result=chat_response_node(state)
            st.session_state.chat_messages=result["messages"]

        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🌟 Made with ❤️ for curious young minds! 🌟</p>
    <p style='font-size: 12px;'>Built with Streamlit, LangGraph, and Groq AI by team leroy AI</p>
</div>
""",unsafe_allow_html = True)
