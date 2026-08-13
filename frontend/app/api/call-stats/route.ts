import { NextResponse } from "next/server";
import initSqlJs from "sql.js";
import fs from "fs";
import path from "path";

const DB_PATH = path.join(process.cwd(), "..", "backend", "src", "NyaAI_Memory.db");
const WASM_PATH = path.join(process.cwd(), "node_modules", "sql.js", "dist", "sql-wasm.wasm");

export async function GET() {
  try {
    const wasmBinary = fs.readFileSync(WASM_PATH);
    const SQL = await initSqlJs({ wasmBinary });
    const db = new SQL.Database(fs.readFileSync(DB_PATH));

    const totalRes = db.exec("SELECT COUNT(*) c FROM calls WHERE outcome != 'in_progress'");
    const successRes = db.exec("SELECT COUNT(*) c FROM calls WHERE outcome = 'success'");
    const failedRes = db.exec("SELECT COUNT(*) c FROM calls WHERE outcome = 'failed'");
    const recentRes = db.exec("SELECT call_id, channel, started_at, outcome FROM calls WHERE outcome != 'in_progress' ORDER BY started_at DESC LIMIT 10");

    db.close();

    const total = totalRes[0]?.values[0][0] || 0;
    const success = successRes[0]?.values[0][0] || 0;
    const failed = failedRes[0]?.values[0][0] || 0;
    const recent = recentRes[0]
      ? recentRes[0].values.map((row: any[]) =>
          Object.fromEntries(row.map((v, i) => [recentRes[0].columns[i], v]))
        )
      : [];

    return NextResponse.json({ total, success, failed, recent });
  } catch (err: any) {
    console.error(err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}