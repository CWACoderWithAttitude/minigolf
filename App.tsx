import React, {useState, useCallback} from 'react';
import {
  SafeAreaView,
  StyleSheet,
  ScrollView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StatusBar,
  Alert,
} from 'react-native';
import {Player} from './src/types';

const HOLE_COUNT = 18;

const App = (): React.JSX.Element => {
  const [players, setPlayers] = useState<Player[]>([]);
  const [newPlayerName, setNewPlayerName] = useState('');

  // Spieler hinzufügen
  const addPlayer = useCallback(() => {
    if (newPlayerName.trim().length === 0) {
      Alert.alert('Fehler', 'Bitte gib einen Namen ein.');
      return;
    }
    const newPlayer: Player = {
      id: Date.now().toString(),
      name: newPlayerName.trim(),
      scores: Array(HOLE_COUNT).fill(null),
    };
    setPlayers(prev => [...prev, newPlayer]);
    setNewPlayerName('');
  }, [newPlayerName]);

  // Score aktualisieren
  const updateScore = (playerId: string, holeIndex: number, score: number) => {
    setPlayers(prev =>
      prev.map(p => {
        if (p.id !== playerId) {
          return p;
        }
        const newScores = [...p.scores];
        // Verhindere negative Scores
        newScores[holeIndex] = Math.max(1, score);
        return {...p, scores: newScores};
      }),
    );
  };

  // Gesamtpunktzahl berechnen
  const calculateTotal = (scores: (number | null)[]) => {
    return scores.reduce((acc, curr) => (acc || 0) + (curr || 0), 0) || 0;
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />
      <View style={styles.header}>
        <Text style={styles.title}>Minigolf Manager ⛳️</Text>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Spieler Hinzufügen Sektion */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Spieler hinzufügen</Text>
          <View style={styles.inputRow}>
            <TextInput
              style={styles.input}
              placeholder="Name des Spielers"
              value={newPlayerName}
              onChangeText={setNewPlayerName}
            />
            <TouchableOpacity style={styles.addButton} onPress={addPlayer}>
              <Text style={styles.addButtonText}>+</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Scorecard */}
        {players.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Scorecard</Text>
            {players.map(player => (
              <View key={player.id} style={styles.playerCard}>
                <View style={styles.playerHeader}>
                  <Text style={styles.playerName}>{player.name}</Text>
                  <Text style={styles.playerTotal}>
                    Gesamt: {calculateTotal(player.scores)}
                  </Text>
                </View>

                {/* Löcher Liste für diesen Spieler */}
                <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                  {player.scores.map((score, index) => (
                    <View key={index} style={styles.holeContainer}>
                      <Text style={styles.holeLabel}>Loch {index + 1}</Text>
                      <View style={styles.scoreControl}>
                        <TouchableOpacity
                          onPress={() =>
                            updateScore(player.id, index, (score || 0) - 1)
                          }>
                          <Text style={styles.controlButton}>-</Text>
                        </TouchableOpacity>
                        <Text style={styles.scoreValue}>{score || '-'}</Text>
                        <TouchableOpacity
                          onPress={() =>
                            updateScore(player.id, index, (score || 0) + 1)
                          }>
                          <Text style={styles.controlButton}>+</Text>
                        </TouchableOpacity>
                      </View>
                    </View>
                  ))}
                </ScrollView>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  scrollContent: {
    padding: 20,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
    color: '#444',
  },
  inputRow: {
    flexDirection: 'row',
  },
  input: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
    marginRight: 10,
  },
  addButton: {
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
    borderRadius: 8,
  },
  addButtonText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  playerCard: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  playerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    paddingBottom: 8,
  },
  playerName: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  playerTotal: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  holeContainer: {
    alignItems: 'center',
    marginRight: 16,
    backgroundColor: '#f9f9f9',
    padding: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#eee',
  },
  holeLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  scoreControl: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  controlButton: {
    fontSize: 20,
    paddingHorizontal: 8,
    color: '#007AFF',
  },
  scoreValue: {
    fontSize: 18,
    fontWeight: 'bold',
    width: 30,
    textAlign: 'center',
  },
});

export default App;