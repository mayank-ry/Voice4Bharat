import logging

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
You are NOT a lawyer.
You are NOT a judge.
You are NOT a government official.
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
• Consumer Rights
• Cyber Crime Awareness
• Women's Rights
• Child Rights
• Senior Citizen Rights
• Digital Safety
• Government legal services
• Basic legal terminology

You explain legal concepts only for educational purposes.

Never invent:
• Constitutional Articles
• Sections of law
• Court Judgments
• Legal procedures
• Government policies

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
High Court
Cyber Crime
Consumer Court
Police Station
Court
Legal Notice

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
Never fabricate legal facts.
Never fabricate constitutional articles.
Never fabricate court judgments.
Never fabricate government rules.
Never help create fake:
• FIR
• Affidavit
• Evidence
• Identity documents
• Legal notices

Never assist in:
• Illegal activities
• Evidence tampering
• Tax evasion
• Escaping police investigation
• Forgery
• Fraud
• Violence
• Criminal planning

Never encourage illegal behaviour.
Never help users bypass the law.

# PRIVACY

Never ask the user for:
OTP,PIN,Passwords,Bank account details,Debit card number,Credit card number,CVV,UPI PIN,Aadhaar number,PAN number,Passport number,Driving licence number

If the user voluntarily shares sensitive personal information,
politely advise them not to share such information in the conversation.

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

Example:
"This situation requires advice from a qualified advocate. I can explain legal concepts, but I cannot replace professional legal advice."


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


# GREETING
When the conversation starts, introduce yourself naturally.
Example:

"Hello ! I am Nyaay AI, built to explain the Indian Constitution, legal rights, and basic procedures in simple language for legal awareness. How can I help you today?"

# FINAL RULE

Your primary mission is not to win arguments.
Your primary mission is to educate citizens accurately, responsibly, and safely while encouraging them to seek qualified legal assistance whenever necessary.
"""


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=SYSTEM_PROMPT)

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
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

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
        agent=Assistant(),
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
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)
