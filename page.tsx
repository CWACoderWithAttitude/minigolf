'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

type Player = { id: number; name: string };

export default function MatchPage({ params }: { params: { id: string } }) {
  const matchId = params.id;
  const searchParams = useSearchParams();
  const playerIds = searchParams.getAll('p').map(Number);
  
  const [players, setPlayers] = useState<Player[]>([]);
  const [currentHole, setCurrentHole] = useState(1);
  const [scores, setScores] = useState<Record<string, number>>({}); // key: "playerId-hole"

  useEffect(() => {
    // Spieler laden, um Namen anzuzeigen
    fetch('/api/players').then(res => res.json()).then((allPlayers: Player[]) => {
      setPlayers(allPlayers.filter(p => playerIds.includes(p.id)));
    });
  }, []);

  const updateScore = async (playerId: number, strokes: number) => {
    const key = `${playerId}-${currentHole}`;
    setScores(prev => ({ ...prev, [key]: strokes }));

    await fetch('/api/matches', {
      method: 'PUT',
      body: JSON.stringify({
        matchId,
        playerId,
        hole: currentHole,
        strokes
      })
    });
  };

  const getTotal = (playerId: number) => {
    let total = 0;
    for (let h = 1; h <= 18; h++) {
      total += scores[`${playerId}-${h}`] || 0;
    }
    return total;
  };

  return (
    <div className="p-4 max-w-md mx-auto pb-20">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-xl font-bold">Loch {currentHole} / 18</h1>
        <div className="flex gap-2">
          <button 
            disabled={currentHole <= 1}
            onClick={() => setCurrentHole(h => h - 1)}
            className="px-3 py-1 bg-gray-200 rounded disabled:opacity-30"
          >
            &lt;
          </button>
          <button 
            disabled={currentHole >= 18}
            onClick={() => setCurrentHole(h => h + 1)}
            className="px-3 py-1 bg-gray-200 rounded disabled:opacity-30"
          >
            &gt;
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {players.map(player => {
          const currentScore = scores[`${player.id}-${currentHole}`] || 0;
          return (
            <div key={player.id} className="bg-white p-4 rounded-lg shadow border">
              <div className="flex justify-between mb-2">
                <span className="font-bold">{player.name}</span>
                <span className="text-gray-500 text-sm">Gesamt: {getTotal(player.id)}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <button 
                  onClick={() => updateScore(player.id, Math.max(0, currentScore - 1))}
                  className="w-10 h-10 bg-red-100 text-red-600 rounded-full font-bold text-xl"
                >
                  -
                </button>
                <span className="text-3xl font-mono w-12 text-center">
                  {currentScore}
                </span>
                <button 
                  onClick={() => updateScore(player.id, Math.min(99, currentScore + 1))}
                  className="w-10 h-10 bg-green-100 text-green-600 rounded-full font-bold text-xl"
                >
                  +
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}