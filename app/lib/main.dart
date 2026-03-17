import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() => runApp(const StudyBuddiesApp());

class StudyBuddiesApp extends StatelessWidget {
  const StudyBuddiesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Study Buddies',
      theme: ThemeData(useMaterial3: true),
      home: const SearchPage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class SearchPage extends StatefulWidget {
  const SearchPage({super.key});

  @override
  State<SearchPage> createState() => _SearchPageState();
}

class _SearchPageState extends State<SearchPage> {
  static const String baseUrl = "http://10.0.2.2:8000";

  final TextEditingController _q = TextEditingController(text: "langson");

  bool _loading = false;
  String? _error;
  List<dynamic> _results = [];

  Future<void> _search() async {
    final query = _q.text.trim();
    if (query.isEmpty) return;

    setState(() {
      _loading = true;
      _error = null;
      _results = [];
    });

    try {
      final uri = Uri.parse("$baseUrl/search").replace(queryParameters: {
        "q": query,
        "dur": "30",
        "k": "5",
      });

      final res = await http.get(uri);
      if (res.statusCode != 200) {
        throw Exception("HTTP ${res.statusCode}: ${res.body}");
      }

      final data = jsonDecode(res.body) as Map<String, dynamic>;
      setState(() {
        _results = (data["results"] as List<dynamic>?) ?? [];
      });
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  void dispose() {
    _q.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Study Buddies")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _q,
                    decoration: const InputDecoration(
                      labelText: "Search",
                      border: OutlineInputBorder(),
                    ),
                    onSubmitted: (_) => _search(),
                  ),
                ),
                const SizedBox(width: 12),
                ElevatedButton(
                  onPressed: _loading ? null : _search,
                  child: const Text("Go"),
                ),
              ],
            ),
            const SizedBox(height: 16),

            if (_loading) const LinearProgressIndicator(),
            if (_error != null) ...[
              const SizedBox(height: 12),
              Text(_error!, style: const TextStyle(color: Colors.red)),
            ],
            const SizedBox(height: 12),

            Expanded(
              child: ListView.separated(
                itemCount: _results.length,
                separatorBuilder: (_, __) => const Divider(),
                itemBuilder: (_, i) {
                  // Your backend returns: [roomId, score, startTime, [terms]]
                  final r = _results[i] as Map<String, dynamic>;
                  
                  final spaceName = r["space_name"] ?? "Unknown Space";
                  final roomName = r["room_name"] ?? "Unknown Room";
                  final capacity = r["capacity"] ?? "?";
                  final startTime = r["start_time"] ?? "Unknown";
                  final matchedTerms = (r["matched_terms"] as List<dynamic>? ?? []).join(", ")
                  final matchCount = r["match_count"] ?? 0;

                  return ListTile(
                    title: Text("$spaceName - $roomName"),
                    subtitle: Text(
                      "Capacity: $capacity\nMatched keywords: $matchedTerms\nStar time: $startTime",
                      ),
                    trailing: Text(matchCount.toString()),
                    isThreeLine: true,
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}