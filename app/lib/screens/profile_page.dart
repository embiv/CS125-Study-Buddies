import 'package:flutter/material.dart';
import '../models/user_preferences.dart';

class ProfilePage extends StatefulWidget {
  final UserPreferences preferences;
  final ValueChanged<UserPreferences> onPreferencesChanged;
  final VoidCallback onSavedGoToResults;

  const ProfilePage({
    super.key,
    required this.preferences,
    required this.onPreferencesChanged,
    required this.onSavedGoToResults,
  });

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  late String preferredLibrary;
  late int? maxCapacity;
  late int duration;
  late Set<String> features;

  final List<String> featureOptions = [
    "quiet",
    "whiteboard",
    "private",
    "group",
    "tech enhanced",
  ];

  @override
  void initState() {
    super.initState();
    preferredLibrary = widget.preferences.preferredLibrary;
    maxCapacity = widget.preferences.maxCapacity;
    duration = widget.preferences.duration;
    features = Set<String>.from(widget.preferences.features);
  }

  void savePreferences() {
    widget.onPreferencesChanged(
      UserPreferences(
        preferredLibrary: preferredLibrary,
        maxCapacity: maxCapacity,
        duration: duration,
        features: features,
      ),
    );

    widget.onSavedGoToResults();

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Preferences saved")),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Profile")),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            "Search Preferences",
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 20),

          const Text("Preferred Library"),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            value: preferredLibrary,
            items: const [
              DropdownMenuItem(value: "Any", child: Text("Any")),
              DropdownMenuItem(value: "Langson", child: Text("Langson")),
              DropdownMenuItem(value: "Science", child: Text("Science")),
            ],
            onChanged: (value) {
              setState(() {
                preferredLibrary = value!;
              });
            },
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
            ),
          ),

          const SizedBox(height: 20),

          const Text("Maximum Capacity"),
          const SizedBox(height: 8),
          DropdownButtonFormField<int?>(
            value: maxCapacity,
            items: const [
              DropdownMenuItem<int?>(value: null, child: Text("Any")),
              DropdownMenuItem<int?>(value: 1, child: Text("1")),
              DropdownMenuItem<int?>(value: 2, child: Text("2")),
              DropdownMenuItem<int?>(value: 4, child: Text("4")),
              DropdownMenuItem<int?>(value: 6, child: Text("6")),
              DropdownMenuItem<int?>(value: 8, child: Text("8")),
            ],
            onChanged: (value) {
              setState(() {
                maxCapacity = value;
              });
            },
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
            ),
          ),

          const SizedBox(height: 20),

          Text("Study Duration: $duration min"),
          Slider(
            value: duration.toDouble(),
            min: 30,
            max: 120,
            divisions: 6,
            label: "$duration min",
            onChanged: (value) {
              setState(() {
                duration = value.toInt();
              });
            },
          ),

          const SizedBox(height: 20),
          const Text("Preferred Features"),
          const SizedBox(height: 8),

          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: featureOptions.map((feature) {
              final selected = features.contains(feature);
              return FilterChip(
                label: Text(feature),
                selected: selected,
                onSelected: (isSelected) {
                  setState(() {
                    if (isSelected) {
                      features.add(feature);
                    } else {
                      features.remove(feature);
                    }
                  });
                },
              );
            }).toList(),
          ),

          const SizedBox(height: 30),

          ElevatedButton(
            onPressed: savePreferences,
            child: const Text("Save Preferences"),
          ),
        ],
      ),
    );
  }
}