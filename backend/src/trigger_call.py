import asyncio, json
from livekit import api
from dotenv import load_dotenv

load_dotenv(".env.local")

async def main():
    lkapi = api.LiveKitAPI()
    await lkapi.agent_dispatch.create_dispatch(
        api.CreateAgentDispatchRequest(
            agent_name="my-agent",
            room="outbound-test-room",
            metadata=json.dumps({
                "sip_address": "myancray@sip.linphone.org"
            }),
        )
    )
    await lkapi.aclose()
asyncio.run(main())