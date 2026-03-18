import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

class MapPage extends StatefulWidget {
  final double userLat;
  final double userLon;
  final List spots;
  final int? selectedIndex;

  const MapPage({
    super.key,
    required this.userLat,
    required this.userLon,
    required this.spots,
    this.selectedIndex,
  });

  @override
  State<MapPage> createState() => _MapPageState();
}

class _MapPageState extends State<MapPage> {
  int? currentSelectedIndex;
  final MapController _mapController = MapController();

  @override
  void initState() {
    super.initState();
    currentSelectedIndex = widget.selectedIndex;
  }

  @override
  Widget build(BuildContext context) {
    Map<String, dynamic>? selectedSpot;

    if (currentSelectedIndex != null &&
        currentSelectedIndex! >= 0 &&
        currentSelectedIndex! < widget.spots.length) {
      selectedSpot =
          Map<String, dynamic>.from(widget.spots[currentSelectedIndex!]);
    }

    final centerLat = selectedSpot != null
        ? (selectedSpot["lat"] as num?)?.toDouble() ?? widget.userLat
        : widget.userLat;

    final centerLon = selectedSpot != null
        ? (selectedSpot["lon"] as num?)?.toDouble() ?? widget.userLon
        : widget.userLon;

    final markers = <Marker>[
      Marker(
        point: LatLng(widget.userLat, widget.userLon),
        width: 80,
        height: 80,
        child: const Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.person_pin_circle, size: 36),
            Text(
              "You",
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    ];

    const double offsetStep = 0.00012;

    for (int i = 0; i < widget.spots.length; i++) {
      final spot = widget.spots[i];
      final lat = (spot["lat"] as num?)?.toDouble();
      final lon = (spot["lon"] as num?)?.toDouble();

      if (lat == null || lon == null) continue;

      final isSelected = i == currentSelectedIndex;

      final row = i ~/ 3;
      final col = i % 3;

      final adjustedLat = lat + (row * offsetStep);
      final adjustedLon = lon + (col * offsetStep);

      markers.add(
        Marker(
          point: LatLng(adjustedLat, adjustedLon),
          width: 110,
          height: 90,
          child: GestureDetector(
            onTap: () {
              setState(() {
                currentSelectedIndex = i;
              });

              _mapController.move(
                LatLng(adjustedLat - 0.0002, adjustedLon),
                17,
              );
            },
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.location_on,
                  size: isSelected ? 40 : 32,
                  color: isSelected ? Colors.red : Colors.blue,
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.black12),
                  ),
                  child: Text(
                    "#${i + 1}",
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }

    final matchedTerms = selectedSpot != null
        ? List<String>.from(selectedSpot["matched_terms"] ?? const [])
        : <String>[];

    return Scaffold(
      appBar: AppBar(title: const Text("Map View")),
      body: Column(
        children: [
          Expanded(
            child: FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                initialCenter: LatLng(centerLat, centerLon),
                initialZoom: 16,
              ),
              children: [
                TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.cs125studybuddies.app',
                ),
                MarkerLayer(markers: markers),
                RichAttributionWidget(
                  attributions: [
                    TextSourceAttribution('© OpenStreetMap contributors'),
                  ],
                ),
              ],
            ),
          ),
          if (selectedSpot != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Theme.of(context).cardColor,
                boxShadow: const [
                  BoxShadow(
                    blurRadius: 6,
                    color: Colors.black12,
                    offset: Offset(0, -2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    "#${currentSelectedIndex! + 1} ${selectedSpot["space_name"] ?? "Unknown Space"}",
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    selectedSpot["room_name"] ?? "Unknown Room",
                    style: const TextStyle(fontSize: 20),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    "Capacity: ${selectedSpot["capacity"]} | Start: ${selectedSpot["start_time"]}",
                  ),
                  const SizedBox(height: 4),
                  Text(
                    "Score: ${selectedSpot["score"] ?? selectedSpot["match_count"]}",
                  ),
                  if (matchedTerms.isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Wrap(
                      spacing: 6,
                      runSpacing: 6,
                      children: matchedTerms
                          .map((term) => Chip(label: Text(term)))
                          .toList(),
                    ),
                  ],
                ],
              ),
            )
          else
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              child: const Text(
                "Tap a map marker to view room details.",
                textAlign: TextAlign.center,
              ),
            ),
        ],
      ),
    );
  }
}