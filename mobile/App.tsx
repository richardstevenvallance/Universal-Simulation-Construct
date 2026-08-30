import React, { useState } from "react";
import {
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

const tabs = ["Dex", "GO", "Scan", "Collection", "Market", "Play", "AR"] as const;
type Tab = (typeof tabs)[number];

export default function App() {
  const [tab, setTab] = useState<Tab>("Dex");
  return (
    <SafeAreaView style={styles.root}>
      <View style={styles.header}>
        <Text style={styles.title}>DexForge</Text>
        <Text style={styles.subtitle}>
          Pokédex • GO • cards • swaps • marketplace • TCG • AR
        </Text>
      </View>
      <ScrollView horizontal contentContainerStyle={styles.tabs}>
        {tabs.map((item) => (
          <TouchableOpacity
            key={item}
            onPress={() => setTab(item)}
            style={[styles.tab, tab === item && styles.activeTab]}
          >
            <Text style={styles.tabText}>{item}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
      <ScrollView contentContainerStyle={styles.body}>
        <Panel tab={tab} />
      </ScrollView>
    </SafeAreaView>
  );
}

function Panel({ tab }: { tab: Tab }) {
  const copy: Record<Tab, [string, string[]]> = {
    Dex: [
      "Research Pokédex",
      [
        "Search species, moves, types and evolution",
        "Use the Pi as a local cache",
        "Evidence/source links for imported data",
      ],
    ],
    GO: [
      "GO Companion",
      [
        "Log walks, catches and raids",
        "Plan teams and tasks",
        "No spoofing or private gameplay API",
      ],
    ],
    Scan: [
      "Card Reader + Grader",
      [
        "Capture front/back",
        "Identify printing",
        "Measure centering/corners/edges/surface",
        "Return provisional grade + confidence",
      ],
    ],
    Collection: [
      "Collection + Decks",
      [
        "Track owned copies and condition",
        "Build 60-card decks",
        "Move a scanned card into swaps or play",
      ],
    ],
    Market: [
      "Swaps + Marketplace",
      [
        "List cards for swap, sale, or both",
        "Offer cards plus an optional cash balance",
        "Use provider-hosted checkout; DexForge never stores raw card details",
        "Track offers, reservations and payment state",
      ],
    ],
    Play: [
      "TCG Table",
      [
        "Two-player match state",
        "Turn/action log",
        "Grow the rules engine from structured card effects",
      ],
    ],
    AR: [
      "Augmented Reality",
      [
        "Inspect scanned cards in 3D",
        "Project a tabletop battle or collection gallery",
        "Support persistent location anchors through a later Niantic Spatial client",
        "Keep provider tokens and private location data off the public frontend",
      ],
    ],
  };

  return (
    <View style={styles.card}>
      <Text style={styles.heading}>{copy[tab][0]}</Text>
      {copy[tab][1].map((line) => (
        <Text key={line} style={styles.line}>• {line}</Text>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#111827" },
  header: { padding: 20 },
  title: { fontSize: 28, fontWeight: "800", color: "white" },
  subtitle: { color: "#cbd5e1", marginTop: 4 },
  tabs: { paddingHorizontal: 12, gap: 8 },
  tab: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 999,
    backgroundColor: "#1f2937",
  },
  activeTab: { backgroundColor: "#374151" },
  tabText: { color: "white", fontWeight: "700" },
  body: { padding: 16 },
  card: { backgroundColor: "#1f2937", borderRadius: 18, padding: 18 },
  heading: { fontSize: 22, fontWeight: "800", color: "white", marginBottom: 12 },
  line: { fontSize: 16, color: "#e5e7eb", marginVertical: 6, lineHeight: 22 },
});
