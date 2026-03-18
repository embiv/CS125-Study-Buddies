import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/user_preferences.dart';

class StudySpotsPage extends StatefulWidget {
  final UserPreferences preferences;
  final int searchTrigger;

  const StudySpotsPage({
    super.key,
    required this.preferences,
    required this.searchTrigger,
  });

  @override
  State<StudySpotsPage> createState() => _StudySpotsPageState();
}

class _StudySpotsPageState extends State<StudySpotsPage> {
  final TextEditingController controller = TextEditingController();
  Map<String, dynamic>? data;
  bool loading = false;

  @override
  void didUpdateWidget(covariant StudySpotsPage oldWidget) {
    super.didUpdateWidget(oldWidget);

    if (widget.searchTrigger != oldWidget.searchTrigger) {
      if (controller.text.trim().isNotEmpty) {
        search();
      }
    }
  }

  Future<void> search() async {
    setState(() => loading = true);

    final result = await ApiService.getStudySpots(
      query: controller.text.trim(),
      lat: 33.643,
      lon: -117.8465,
      cap: widget.preferences.maxCapacity,
      dur: widget.preferences.duration,
      preferredLibrary: widget.preferences.preferredLibrary,
      features: widget.preferences.features.toList(),
    );

    setState(() {
      data = result;
      loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final results = data?["results"] ?? [];

    return Scaffold(
      appBar: AppBar(title: const Text("Study Spots")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                labelText: "Search (e.g. group, quiet)",
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),
            ElevatedButton(
              onPressed: search,
              child: const Text("Search"),
            ),
            const SizedBox(height: 10),

            if (loading) const CircularProgressIndicator(),

            if (data != null) ...[
              Text("Closest: ${data!["closest_library"]}"),
              const SizedBox(height: 10),

              Expanded(
                child: ListView.builder(
                  itemCount: results.length,
                  itemBuilder: (context, index) {
                    final room = results[index];
                    final matchedTerms = List<String>.from(room["matched_terms"] ?? []); 

                    return Card(
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              room["space_name"] ?? "Unkwown Space",
                              style: const TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              room["room_name"] ?? "Unkown",
                              style: const TextStyle(fontSize: 20),
                            ),
                            const SizedBox(height: 6),
                            Text("Capacity: ${room["capacity"]} | Start: ${room["start_time"]}"),
                            const SizedBox(height: 4),
                            Text(
                              "Score: ${room["score"] ?? room["match_count"]}",
                            ),
                            const SizedBox(height: 8),
                            Wrap(
                              spacing: 6,
                              runSpacing: 6,
                              children: matchedTerms
                                    .map((term) => Chip(label: Text(term)))
                                    .toList(),
                            ),
                          ],
                        ),
                      )
                    );
                  },
                ),
              ),
            ]
          ],
        ),
      ),
    );
  }
}