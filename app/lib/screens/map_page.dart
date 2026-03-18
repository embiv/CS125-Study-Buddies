import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

class MapPage extends StatelessWidget {
  final double userLat;
  final double userLon;
  final List spots;
  final int selectedIndex;

  const MapPage({
    super.key,
    required this.userLat,
    required this.userLon,
    required this.spots,
    required this.selectedIndex,
  });

  @override
  Widget build(BuildContext context) {
    final selectedSpot = spots[selectedIndex];
    final selectedLat = (selectedSpot["lat"] as num?)?.toDouble() ?? userLat;
    final selectedLon = (selectedSpot["lon"] as num?)?.toDouble() ?? userLon;

    final markers = <Marker>[
      Marker(
        point: LatLng(userLat, userLon),
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

    for (int i = 0; i < spots.length; i++) {
      final spot = spots[i];
      final lat = (spot["lat"] as num?)?.toDouble();
      final lon = (spot["lon"] as num?)?.toDouble();

      if (lat == null || lon == null) continue;

      final isSelected = i == selectedIndex;

      markers.add(
        Marker(
          point: LatLng(lat, lon),
          width: 110,
          height: 90,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.location_on,
                size: isSelected ? 40 : 32,
                color: isSelected ? Colors.red : Colors.blue,
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
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
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text("Map View")),
      body: FlutterMap(
        options: MapOptions(
          initialCenter: LatLng(selectedLat, selectedLon),
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
            ])
        ],
      ),
    );
  }
}