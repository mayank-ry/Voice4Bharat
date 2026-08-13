import { NextResponse } from "next/server";
import { getEscalations } from "@/lib/escalations-db";

export async function GET() {
  try {
    const rows = await getEscalations();
    return NextResponse.json({ escalations: rows });
  } catch (err: any) {
    console.error(err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}