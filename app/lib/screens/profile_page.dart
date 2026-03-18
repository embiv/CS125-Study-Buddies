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
  late TextEditingController latController;
  late TextEditingController lonController;

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

    latController = TextEditingController(
      text: widget.preferences.userLat.toString(),
    );
    lonController = TextEditingController(
      text: widget.preferences.userLon.toString(),
    );
  }

  @override
  void dispose() {
    latController.dispose();
    lonController.dispose();
    super.dispose();
  }

  void setPresetLocation(double lat, double lon) {
    setState(() {
      latController.text = lat.toString();
      lonController.text = lon.toString();
    });
  }

  void savePreferences() {
    final parsedLat = double.tryParse(latController.text.trim());
    final parsedLon = double.tryParse(lonController.text.trim());

    if (parsedLat == null || parsedLon == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Please enter valid latitude and longitude."),
        ),
      );
      return;
    }

    widget.onPreferencesChanged(
      UserPreferences(
        preferredLibrary: preferredLibrary,
        maxCapacity: maxCapacity,
        duration: duration,
        features: features,
        userLat: parsedLat,
        userLon: parsedLon,
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

          const Text(
            "Test User Location",
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            "Set a latitude and longitude to simulate a different user location.",
          ),
          const SizedBox(height: 12),

          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              OutlinedButton(
                onPressed: () => setPresetLocation(33.6446, -117.8435),
                child: const Text("Infinity Fountain"),
              ),
              OutlinedButton(
                onPressed: () => setPresetLocation(33.6441, -117.8400),
                child: const Text("ECT"),
              ),
              OutlinedButton(
                onPressed: () => setPresetLocation(33.6496, -117.8427),
                child: const Text("Student Center"),
              ),
              OutlinedButton(
                onPressed: () => setPresetLocation(33.643, -117.8465),
                child: const Text("Lot 16"),
              ),
            ],
          ),

          const SizedBox(height: 12),

          TextField(
            controller: latController,
            keyboardType: const TextInputType.numberWithOptions(
              decimal: true,
              signed: true,
            ),
            decoration: const InputDecoration(
              labelText: "Latitude",
              border: OutlineInputBorder(),
            ),
          ),

          const SizedBox(height: 12),

          TextField(
            controller: lonController,
            keyboardType: const TextInputType.numberWithOptions(
              decimal: true,
              signed: true,
            ),
            decoration: const InputDecoration(
              labelText: "Longitude",
              border: OutlineInputBorder(),
            ),
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