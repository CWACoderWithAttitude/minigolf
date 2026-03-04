export interface Player {
  id: string;
  name: string;
  // Ein Array mit 18 Einträgen für die Löcher.
  // null bedeutet, dass das Loch noch nicht gespielt wurde.
  scores: (number | null)[];
}