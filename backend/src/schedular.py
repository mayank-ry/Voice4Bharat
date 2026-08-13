import asyncio, json, time
from livekit import api
from dotenv import load_dotenv
import os
from database import get_due_calls, mark_call_done, init_db

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env.local"))

async def check_and_dispatch():
    due = get_due_calls()
    if not due:
        return
    lkapi = api.LiveKitAPI()
    for call in due:
        try:
            await lkapi.agent_dispatch.create_dispatch(
                api.CreateAgentDispatchRequest(
                    agent_name="my-agent",
                    room=f"followup-{call['id']}",
                    metadata=json.dumps({
                        "sip_address": call["sip_address"],
                        "followup_topic": call["topic"],
                    }),
                )
            )
            mark_call_done(call["id"])
            print(f"Dispatched follow-up call #{call['id']} about {call['topic']}")
        except Exception as e:
            print(f"Failed to dispatch call #{call['id']}: {e}")
    await lkapi.aclose()

async def main():
    init_db()
    print("Scheduler running... checking every 30 seconds.")
    while True:
        await check_and_dispatch()
        await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())