import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:aaroha_app/core/constants.dart';

class ApiService {
  final String baseUrl = AppConstants.baseUrl;

  Future<String> analyzeScenario(
    String userId,
    int salary,
    String skills,
    bool isRemote,
  ) async {
    final url = Uri.parse('$baseUrl/analyze-scenario');

    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          "user_id": userId,
          "salary": salary,
          "skills": skills,
          "is_remote": isRemote,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['decision']; // Returns the AI's analysis
      } else {
        return 'Error: ${response.statusCode} - ${response.body}';
      }
    } catch (e) {
      return 'Connection Error: $e';
    }
  }
}
