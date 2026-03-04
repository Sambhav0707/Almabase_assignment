import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // Use localhost for web/desktop, change to 10.0.2.2 for Android emulator
  static const String baseUrl = 'http://localhost:8000';
  static const String _tokenKey = 'jwt_token';
  static const String _questionnaireIdKey = 'active_questionnaire_id';

  // ── Token Management ──────────────────────────────────────

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  static Future<void> _saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_questionnaireIdKey);
  }

  static Future<void> saveQuestionnaireId(int id) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_questionnaireIdKey, id);
  }

  static Future<int?> getQuestionnaireId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt(_questionnaireIdKey);
  }

  static Future<Map<String, String>> _authHeaders() async {
    final token = await getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  // ── Auth ──────────────────────────────────────────────────

  static Future<Map<String, dynamic>> signup(
    String email,
    String password,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/signup'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );
    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    }
    throw Exception(jsonDecode(response.body)['detail'] ?? 'Signup failed');
  }

  static Future<Map<String, dynamic>> login(
    String email,
    String password,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await _saveToken(data['access_token']);
      return data;
    }
    throw Exception(jsonDecode(response.body)['detail'] ?? 'Login failed');
  }

  // ── File Upload (Web-compatible using bytes) ──────────────

  static Future<Map<String, dynamic>> uploadReference(
    Uint8List fileBytes,
    String fileName,
  ) async {
    return _uploadFile('/upload/reference', fileBytes, fileName);
  }

  static Future<Map<String, dynamic>> uploadQuestionnaire(
    Uint8List fileBytes,
    String fileName,
  ) async {
    final response = await _uploadFile(
      '/upload/questionnaire',
      fileBytes,
      fileName,
    );
    if (response['id'] != null) {
      await saveQuestionnaireId(response['id']);
    }
    return response;
  }

  static Future<Map<String, dynamic>> _uploadFile(
    String endpoint,
    Uint8List fileBytes,
    String fileName,
  ) async {
    final token = await getToken();
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl$endpoint'),
    );
    request.headers['Authorization'] = 'Bearer $token';
    request.files.add(
      http.MultipartFile.fromBytes('file', fileBytes, filename: fileName),
    );

    final streamed = await request.send();
    final response = await http.Response.fromStream(streamed);
    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    }
    throw Exception(jsonDecode(response.body)['detail'] ?? 'Upload failed');
  }

  // ── RAG Pipeline ──────────────────────────────────────────

  static Future<Map<String, dynamic>> generateAnswers(
    int questionnaireId,
  ) async {
    final headers = await _authHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl/rag/generate'),
      headers: headers,
      body: jsonEncode({'questionnaire_id': questionnaireId}),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    if (response.statusCode == 503) {
      throw Exception('AI service temporarily unavailable');
    }
    throw Exception(jsonDecode(response.body)['detail'] ?? 'Generation failed');
  }

  // ── Review ────────────────────────────────────────────────

  static Future<Map<String, dynamic>> getReviewAnswers(
    int questionnaireId,
  ) async {
    final headers = await _authHeaders();
    final response = await http.get(
      Uri.parse('$baseUrl/review/$questionnaireId'),
      headers: headers,
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception(
      jsonDecode(response.body)['detail'] ?? 'Failed to load answers',
    );
  }

  static Future<Map<String, dynamic>> editAnswer(
    int answerId,
    String editedAnswer,
  ) async {
    final headers = await _authHeaders();
    final response = await http.patch(
      Uri.parse('$baseUrl/review/$answerId'),
      headers: headers,
      body: jsonEncode({'edited_answer': editedAnswer}),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception(jsonDecode(response.body)['detail'] ?? 'Edit failed');
  }

  // ── Export ────────────────────────────────────────────────

  static Future<Map<String, dynamic>> exportQuestionnaire(
    int questionnaireId,
  ) async {
    final headers = await _authHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl/export/$questionnaireId'),
      headers: headers,
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception(jsonDecode(response.body)['detail'] ?? 'Export failed');
  }
}
