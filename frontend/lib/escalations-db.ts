import initSqlJs from "sql.js";
import fs from "fs";
import path from "path";

const DB_PATH = path.join(process.cwd(), "..", "backend", "src", "NyaAI_Memory.db");
const WASM_PATH = path.join(process.cwd(), "node_modules", "sql.js", "dist", "sql-wasm.wasm");

let SQL: any = null;

async function getDb() {
  if (!SQL) {
    const wasmBinary = fs.readFileSync(WASM_PATH);
    SQL = await initSqlJs({ wasmBinary });
  }
  const fileBuffer = fs.readFileSync(DB_PATH);
  return new SQL.Database(fileBuffer);
}

export async function getEscalations() {
  const db = await getDb();
  const res = db.exec("SELECT * FROM escalations ORDER BY created_at DESC");
  db.close();
  if (!res[0]) return [];
  const { columns, values } = res[0];
  return values.map((row: any[]) =>
    Object.fromEntries(row.map((v, i) => [columns[i], v]))
  );
}

export async function updateEscalationStatus(id: number, status: string) {
  const db = await getDb();
  db.run("UPDATE escalations SET status = ? WHERE id = ?", [status, id]);
  const data = db.export();
  fs.writeFileSync(DB_PATH, Buffer.from(data));
  db.close();
}