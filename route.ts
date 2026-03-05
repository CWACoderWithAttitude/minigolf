import { NextRequest, NextResponse } from 'next/server';
import db from '@/lib/db';

// Neues Spiel starten
export async function POST() {
  const stmt = db.prepare('INSERT INTO matches DEFAULT VALUES');
  const info = stmt.run();
  return NextResponse.json({ id: info.lastInsertRowid });
}

// Punkte speichern (PUT)
export async function PUT(request: NextRequest) {
  const { matchId, playerId, hole, strokes } = await request.json();
  
  if (!matchId || !playerId || !hole || strokes === undefined) {
    return NextResponse.json({ error: 'Missing fields' }, { status: 400 });
  }

  // Prüfen, ob Eintrag existiert
  const existing = db.prepare(
    'SELECT id FROM scores WHERE match_id = ? AND player_id = ? AND hole = ?'
  ).get(matchId, playerId, hole) as { id: number } | undefined;

  if (existing) {
    db.prepare(
      'UPDATE scores SET strokes = ? WHERE id = ?'
    ).run(strokes, existing.id);
  } else {
    db.prepare(
      'INSERT INTO scores (match_id, player_id, hole, strokes) VALUES (?, ?, ?, ?)'
    ).run(matchId, playerId, hole, strokes);
  }

  return NextResponse.json({ success: true });
}