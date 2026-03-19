import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService { 
  static const String baseUrl = "http://10.0.2.2:5000"; // for andoird emulator
  //static const String baseUrl = "http://localhost:8000"; // for local development

  static Future<Map<String, dynamic>> getStudySpots({
    required String query,
    required double lat,
    required double lon,
    int? cap,
    int dur = 30,
    int k = 5,
    String? preferredLibrary,
    List<String>? features,
  }) async {
    final queryParams = <String, String>{
      'q': query,
      'lat': lat.toString(),
      'lon': lon.toString(),
      'dur': dur.toString(),
      'k': k.toString(),
    };

    if (cap != null) {
      queryParams['cap'] = cap.toString();
    }

    if (preferredLibrary != null && preferredLibrary != "Any") {
      queryParams['preferred_library'] = preferredLibrary;
    }

    if (features != null && features.isNotEmpty) {
      queryParams['features'] = features.join(',');
    }

    final uri = Uri.parse("$baseUrl/study-spots")
        .replace(queryParameters: queryParams);

    final response = await http.get(uri);

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Failed to load study spots");
    }
  }
}