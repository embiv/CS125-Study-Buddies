import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = "http://10.0.2.2:5000";

  static Future<Map<String, dynamic>> getStudySpots({
    required String query,
    required double lat,
    required double lon,
    int? cap,
    int dur = 30,
  }) async {
    final uri = Uri.parse(
      "$baseUrl/study-spots?q=$query&lat=$lat&lon=$lon&dur=$dur${cap != null ? '&cap=$cap' : ''}",
    );

    final response = await http.get(uri);

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Failed to load study spots");
    }
  }
}