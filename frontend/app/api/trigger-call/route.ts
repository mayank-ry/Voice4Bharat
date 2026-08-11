import { NextRequest, NextResponse } from "next/server";
import {
  AgentDispatchClient,
  SipClient,
} from "livekit-server-sdk";

export async function POST(req: NextRequest) {
  try {
    const { sipAddress } = await req.json();

    if (!sipAddress) {
      return NextResponse.json(
        { error: "sipAddress is required" },
        { status: 400 }
      );
    }

    const livekitUrl = process.env.LIVEKIT_URL;
    const apiKey = process.env.LIVEKIT_API_KEY;
    const apiSecret = process.env.LIVEKIT_API_SECRET;

    if (!livekitUrl || !apiKey || !apiSecret) {
      return NextResponse.json(
        { error: "LiveKit environment variables are missing" },
        { status: 500 }
      );
    }

    const roomName = `outbound-${Date.now()}`;

    // Dispatch NyaAI agent
    const agentDispatch = new AgentDispatchClient(
      livekitUrl,
      apiKey,
      apiSecret
    );

    const dispatch = await agentDispatch.createDispatch(
      roomName,
      "my-agent",
      {
        metadata: JSON.stringify({
          sip_address: sipAddress,
        }),
      }
    );

    return NextResponse.json({
      success: true,
      roomName,
      dispatch,
    });
  } catch (err: any) {
    console.error("Trigger call failed:", err);

    return NextResponse.json(
      {
        error: err?.message || "Failed to trigger call",
      },
      { status: 500 }
    );
  }
}