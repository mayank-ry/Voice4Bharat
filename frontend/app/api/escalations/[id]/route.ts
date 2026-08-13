import { NextResponse } from "next/server";
import { updateEscalationStatus } from "@/lib/escalations-db";

export async function PATCH(req: Request, { params }: { params: { id: string } }) {
  try {
    const { status } = await req.json();
    await updateEscalationStatus(parseInt(params.id), status);
    return NextResponse.json({ success: true });
  } catch (err: any) {
    console.error(err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}