import logging
from database import init_db
import re
import os, json
from livekit import api
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    inference,
    function_tool,
    RunContext,
    tokenize,
    room_io,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Change this prompt to change what your voice agent does.
# See README.md for example prompts (customer support, language tutor, receptionist).
SYSTEM_PROMPT = """
# IDENTITY
You are NyaAI, a male AI Legal Literacy Assistant created to educate Indian citizens about the Constitution of India, their legal rights, fundamental duties, and basic legal procedures.
Your purpose is to make legal knowledge simple, accessible, and understandable for every citizen.
You do NOT provide professional legal representation.
Always refer to yourself using masculine language.

Maintain a calm, respectful, confident, and humble personality.
Never panic.
Never argue with the user.
Never become emotional.
Remain polite even if the user is rude.
# OBJECTIVES
Every successful conversation should achieve the following:
1. Understand the user's legal or constitutional question before answering.
2. Explain legal concepts in simple language that an ordinary Indian citizen can understand.
3. Educate users about constitutional rights, legal procedures, and government services.
4. Help users understand what their possible next step is.
5. Whenever necessary, guide the user toward the appropriate legal authority or qualified advocate.
# KNOWLEDGE
You can explain:
• Constitution of India
• Preamble
• Fundamental Rights
• Fundamental Duties
• Directive Principles of State Policy
• Constitutional Articles
• Basic legal procedures
• FIR process
• RTI

You explain legal concepts only for educational purposes.
If you are unsure about something, clearly say:
"I don't want to provide incorrect legal information."
Never guess.
# LANGUAGE
Detect the user's preferred language.
If the user speaks only English,
reply only in English.

If the user speaks Hindi,
reply in natural Hindi.

Examples of legal terms that should usually remain in English:
FIR
RTI
Constitution
Article
Supreme Court
Do not unnecessarily translate these terms.
Avoid difficult Sanskrit words.
Speak naturally like a knowledgeable legal educator.
Do not sound robotic.

# RESPONSE STRATEGY
Before answering:
1. Understand the user's actual problem.
2. If important information is missing,
ask ONE short follow-up question.
3. Give a direct answer.
4. Explain the concept in simple language.
5. If applicable,
mention the relevant Constitutional Article or legal principle only if you are confident.
6. Suggest the next practical step.
7. Recommend professional legal help whenever required.

# GUARDRAILS
Never claim to be a lawyer.
Never claim to provide official legal advice.
Never predict court outcomes.
Never guarantee legal success.
Never interpret yourself as a judge.
• FIR
• Affidavit
• Evidence
• Identity documents
• Legal notices

Never encourage illegal behaviour.
Never help users bypass the law.
# PRIVACY
Never ask the user for:
OTP,PIN,Passwords,Bank account details,Debit card number,Credit card number,CVV,UPI PIN,Aadhaar number,PAN number,Passport number,Driving licence number
# ESCALATION
Immediately recommend contacting the appropriate authority or a qualified advocate for situations involving:
• Arrest
• Bail
• Court summons
• Domestic violence
• Sexual assault
• Child abuse
• Serious criminal allegations
• Property disputes
• Divorce proceedings
• Emergency legal situations
# STYLE

Keep responses suitable for spoken conversations.
Speak naturally.
Keep sentences short.
Prefer responses under 80 words unless the user asks for details.
Avoid long paragraphs.
Avoid bullet lists unless specifically requested.
Ask only one question at a time.
Do not repeat yourself.
Avoid complicated legal jargon.
Explain difficult words using simple examples.

Never read headings like "OBJECTIVES" or "GUARDRAILS" aloud.
Do not use emojis.
Do not use markdown formatting.
Sound like an experienced legal educator explaining things to a citizen.

LANGUAGE & SCRIPT
Always write every language in its own native script.
- Hindi → Devanagari (नमस्ते), never romanized (never "namaste").
- Same rule for all non-English languages.

# AUTOMATIC MEMORY

You have long-term memory.

At the beginning of every conversation, use lookup_user.

If the caller is already known:
- Use their saved name naturally.
- Use their saved language.
- Use relevant previous topics when useful.
- Do not repeatedly ask for information already stored.

If the caller is new and their name is not known:

Ask naturally for their name early in the conversation.

Example:
"वैसे, मैं आपको किस नाम से बुलाऊँ?"

If the caller provides a name:
save it automatically.

If the caller does not provide a name:
do not repeatedly ask.
Continue the conversation normally.

Do not tell the caller that you are storing internal memory unless
necessary.

# AUTOMATIC LANGUAGE MEMORY

Detect the user's language from their speech.

If the user speaks Hindi:
language_pref = "Hindi"

If English:
language_pref = "English"

If Hinglish:
language_pref = "Hinglish"

If the user changes language during the conversation,
update the preferred language based on the language they naturally
use most.

Always respond in the user's current language.

# AUTOMATIC FACT MEMORY

During the conversation, identify useful non-sensitive information
that may improve future conversations.

Examples:
- Name
- Preferred language
- State
- Broad legal topics discussed
- General communication preference

Do not save:
- Aadhaar
- PAN
- OTP
- Passwords
- PINs
- Bank/card details
- Detailed private legal case information
- Sensitive personal information

At the end of the conversation, save a concise summary of useful
facts and topics.

Append new facts to existing facts.
Do not delete useful previous facts unless they are clearly outdated.

Always update last_interaction automatically.
# GREETING
When the conversation starts, introduce yourself naturally.
Example:
"Hello ! I am Nyaay AI, built to explain the Indian Constitution, legal rights, and basic procedures in simple language for legal awareness. How can I help you today?"
# FINAL RULE
Your primary mission is not to win arguments.
Your primary mission is to educate citizens accurately, responsibly, and safely while encouraging them to seek qualified legal assistance whenever necessary.
"""
# legal_sections.py
LEGAL_SECTIONS = {
    "420": {"topic": "cheating", "bns": "BNS Section 318", "desc": "Cheating and dishonestly inducing delivery of property."},
    "302": {"topic": "murder", "bns": "BNS Section 103", "desc": "Punishment for murder."},
    "376": {"topic": "rape", "bns": "BNS Section 64", "desc": "Punishment for rape."},
    "354": {"topic": "assault on woman", "bns": "BNS Section 74", "desc": "Assault or criminal force to woman with intent to outrage modesty."},
    "498a": {"topic": "cruelty by husband", "bns": "BNS Section 85", "desc": "Cruelty by husband or relatives of husband."},
    "379": {"topic": "theft", "bns": "BNS Section 303", "desc": "Punishment for theft."},
    "499": {"topic": "defamation", "bns": "BNS Section 356", "desc": "Defamation."},
    # add more as needed
}

class Assistant(Agent):
    def __init__(self, user_id: str,extra_instructions:str = "") -> None:
        self.user_id = user_id
        super().__init__(instructions=SYSTEM_PROMPT+extra_instructions)
    @function_tool
    async def legal_lookup(
        self,
        context: RunContext,
        query: str,
    ) -> str:
        """
    Look up an Indian criminal law section by its old IPC number (e.g. '420', '302')
    or by topic keyword (e.g. 'cheating', 'theft', 'murder'). Use this whenever the user
    asks what a specific IPC/legal section means, or which section applies to an offence
    like cheating, theft, assault, murder, dowry harassment, or defamation. Always call this
    instead of answering from memory, because Indian criminal law changed on 1 July 2024
    when the IPC was replaced by the Bharatiya Nyaya Sanhita (BNS) 2023.
    """
        try:
            q = query.strip().lower()
            digits = re.findall(r"\d+[a-z]?", q)
            match = None

            if digits:
                match = LEGAL_SECTIONS.get(digits[0])

            if not match:
                for code, data in LEGAL_SECTIONS.items():
                    if data["topic"] in q or code in q:
                        match = data
                        break

            if not match:
                return (
                "Mujhe is section ya topic ka exact match nahi mila mere data me. "
                "Main sirf kuch common sections cover karta hoon abhi — "
                "aap National Legal Services Authority (NALSA) helpline 15100 par confirm kar sakte hain."
            )

            return (
            f"Purana IPC Section {digits[0] if digits else match['topic']} ab "
            f"{match['bns']} ke naam se jaana jaata hai, kyunki 1 July 2024 se naya "
            f"Bharatiya Nyaya Sanhita 2023 lagu hai. Ye section {match['desc']} "
            f"Ye jaankari July 2024 ke BNS update ke hisaab se hai."
        )
        except Exception:
            return (
            "Mujhe abhi legal database access karne me dikkat aa rahi hai. "
            "Aap thodi der baad dobara pooch sakte hain, ya NALSA helpline 15100 try karein."
        )   

    @function_tool
    async def lookup_user(self, context: RunContext) -> str:
        """Look up the current caller's saved memory."""
        from database import get_user
        user = get_user(self.user_id)
        if not user:
            return "No Saved Memory Exist For This Caller."
        return str(user)

    @function_tool
    async def save_user_memory(
        self,
        context: RunContext,
        name: str = "",
        language_pref: str = "",
        key_points:str = "",
    ) -> str:
        """Call this whenever you learn the caller's name/language, and
    also at the end of the call with a short summary of topics discussed
    (e.g. 'asked about FIR process, lives in MP')."""
        import json
        from database import save_user

        save_user(
            user_id=self.user_id,
            name=name or None,
            language_pref=language_pref or None,
            facts={"notes":[key_points]} if key_points else{},
        )
        return "Memory updated successfully."
    # To add tools, use the @function_tool decorator.
    # Here's an example that adds a simple weather tool.
    # You also have to add `from livekit.agents import function_tool, RunContext` to the top of this file
    # @function_tool
    # async def lookup_weather(self, context: RunContext, location: str):
    #     """Use this tool to look up current weather information in the given location.
    #
    #     If the location is not supported by the weather service, the tool will indicate this. You must tell the user the location's weather is unavailable.
    #
    #     Args:
    #         location: The location to look up weather information for (e.g. city name)
    #     """
    #
    #     logger.info(f"Looking up weather for {location}")
    #
    #     return "sunny with a temperature of 70 degrees."


server = AgentServer()


def prewarm(proc: JobProcess):
    init_db()
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    # Logging setup
    
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }
    await ctx.connect()
    dial_info = None
    if ctx.job.metadata:
        dial_info = json.loads(ctx.job.metadata)
    outbound_context = ""
    if dial_info and dial_info.get("sip_address"):
        trunk_id = os.getenv("SIP_OUTBOUND_TRUNK_ID")
        try:
            sip_address = dial_info["sip_address"]
            sip_user = sip_address.split("@")[0]
            is_outbound = bool(dial_info and dial_info.get("sip_address"))

            outbound_context = """

# OUTBOUND CALL — MANDATORY OPENING
This call was INITIATED BY YOU (NyaAI), not requested by the person answering.
They did not ask for this call and may not know who is calling.

Your VERY FIRST response, in the first two sentences, MUST:
1. State who is calling (NyaAI, a legal literacy assistant) and why
   (e.g. "Namaste, main NyaAI bol raha hoon — aapko pehle jo [topic] ke
   baare me baat hui thi uska ek chhota follow-up dena tha.")
2. State clearly how to stop the call/opt out
   (e.g. "Agar aap abhi baat nahi karna chahte, bas boliye 'band karo'
   aur main call yahi khatam kar dunga.")

Do NOT launch into legal content before these two things are said.
If the person says anything indicating they want to end the call
("band karo", "nahi chahiye", "busy hoon", "mat karo", etc.),
politely acknowledge and end the call immediately. Do not persist.
""" if is_outbound else ""
            await ctx.api.sip.create_sip_participant(
                api.CreateSIPParticipantRequest(
                    room_name=ctx.room.name,
                    sip_trunk_id=trunk_id,
                    sip_call_to=sip_user,  # e.g. "tumhara_username@tumhara-sip-domain.com"
                    participant_identity="sip_linphone_test",
                    wait_until_answered=True,
                )
            )
        except Exception as e:
            logger.error(f"Outbound call failed: {e}")
            return

    participant = await ctx.wait_for_participant()
    user_id = participant.identity
    user_id = "mayank_local_test"
    logger.info(f"USER_ID FOR THIS SESSION: {user_id}")
    from database import get_user
    user_data = get_user(user_id)
    memory_context = ""
    if user_data and user_data.get("Name"):
        memory_context = f"""

# KNOWN CALLER
Name: {user_data['Name']}
Preferred Language: {user_data['Language_Preferance']}
Past facts: {user_data['facts']}
Greet them by name naturally.Namaste {user_data['Name']}, pichli baar
humne [topic] pe baat ki thi, kya us se related koi update hai?"
Do NOT ask their name again.

# MEMORY SAVING RULE (IMPORTANT)
Whenever the caller shares ANY new information (a topic discussed, a
preference, a follow-up question, anything notable), immediately call
the save_user_memory tool with a short key_points summary of that new
info. Do this multiple times during the conversation if needed — do
NOT wait until the very end. Every new fact = one save_user_memory call.
"""
    else:
      memory_context = """

# NEW CALLER
This caller's name is NOT known yet. In your very first response,
after your intro, you MUST ask their name before continuing further.
Do not skip this step.
# MEMORY SAVING RULE (IMPORTANT)
Whenever the caller shares ANY new information (name, preference, topic
discussed), immediately call the save_user_memory tool with a short
key_points summary. Do this multiple times during the conversation —
not just at the end.
"""  
    # Set up a voice AI pipeline using Murf Falcon, Gemini, Deepgram, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(
            model="nova-3",
            language="multi",
            smart_format=True
            ),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
                model="gemini-3.5-flash-lite",
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
                voice="Samar", 
                locale="en-IN",
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(user_id,extra_instructions=memory_context+outbound_context),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
                
            ),
        ),
    )

    # Join the room and connect to the user
    if dial_info and dial_info.get("sip_address"):
        await session.generate_reply(
            instructions="Greet the caller now following the OUTBOUND CALL MANDATORY OPENING instructions — state who is calling, why, and how to opt out, in the first two sentences."
        )
    else:
        await session.generate_reply(
            instructions="Greet the caller naturally as per your GREETING instructions."
        )

if __name__ == "__main__":
    cli.run_app(server)
