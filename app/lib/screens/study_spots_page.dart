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
      search();

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
    final results = List<Map<String, dynamic>>.from(data?["results"] ?? []);
    final isEmptyQuery = controller.text.trim().isEmpty;

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

            if (loading)
              const Expanded(
                child: Center(
                  child: CircularProgressIndicator(),
                ),
              )
            else if (data != null && results.isEmpty)
              Expanded(
                child: Center(
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.grey.shade100,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.grey.shade300),
                    ),
                    child: Text(
                      "No results found.\n\nTry changing your search or relaxing your preferences like maximum capacity or preferred library.",
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 16),
                    ),
                  ),
                ),
              )
            else if (data != null) ...[
              Text("Closest: ${data!["closest_library"]}"),
              const SizedBox(height: 10),

              Expanded(
                child: Column(
                  children: [
                    if (isEmptyQuery)
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(12),
                        margin: const EdgeInsets.only(bottom: 10),
                        decoration: BoxDecoration(
                          color: Colors.blue.shade50,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.blue.shade100),
                        ),
                        child: const Text(
                          "Showing recommended rooms based on your preferences.",
                          style: TextStyle(fontSize: 14),
                        ),
                      ),

                    Expanded(
                      child: ListView.builder(
                        itemCount: results.length,
                        itemBuilder: (context, index) {
                          final room = results[index];
                          final matchedTerms =
                              List<String>.from(room["matched_terms"] ?? []);

                          return Card(
                            child: Padding(
                              padding: const EdgeInsets.all(12),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    room["space_name"] ?? "Unknown Space",
                                    style: const TextStyle(
                                      fontSize: 14,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    room["room_name"] ?? "Unknown",
                                    style: const TextStyle(fontSize: 20),
                                  ),
                                  const SizedBox(height: 6),
                                  Text(
                                    "Capacity: ${room["capacity"]} | Start: ${room["start_time"]}",
                                  ),
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
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}