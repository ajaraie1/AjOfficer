import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  late Dio _dio;
  String? _token;

  // Configure for your backend URL
  static const String baseUrl = 'http://192.168.11.101:8000/api';

  ApiService() {
    _dio = Dio(
      BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        headers: {'Content-Type': 'application/json'},
      ),
    );

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          if (_token != null) {
            options.headers['Authorization'] = 'Bearer $_token';
          }
          handler.next(options);
        },
      ),
    );

    _loadToken();
  }

  Future<void> _loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('auth_token');
  }

  Future<void> setToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }

  Future<void> clearToken() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }

  bool get isAuthenticated => _token != null;

  // Auth endpoints
  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await _dio.post(
      '/auth/login',
      data: 'username=$email&password=$password',
      options: Options(contentType: 'application/x-www-form-urlencoded'),
    );
    return response.data;
  }

  Future<Map<String, dynamic>> register(
    String email,
    String password,
    String fullName,
  ) async {
    final response = await _dio.post(
      '/auth/register',
      data: {'email': email, 'password': password, 'full_name': fullName},
    );
    return response.data;
  }

  Future<Map<String, dynamic>> getMe() async {
    final response = await _dio.get('/auth/me');
    return response.data;
  }

  // Goals endpoints
  Future<List<dynamic>> getGoals() async {
    final response = await _dio.get('/inputs/goals');
    return response.data;
  }

  // Daily Operations endpoints
  Future<List<dynamic>> getDailyLogs(String date) async {
    final response = await _dio.get(
      '/operations/logs',
      queryParameters: {'execution_date': date},
    );
    return response.data;
  }

  Future<Map<String, dynamic>> createDailyLog(Map<String, dynamic> data) async {
    final response = await _dio.post('/operations/logs', data: data);
    return response.data;
  }

  Future<Map<String, dynamic>> startLog(
    String logId,
    String actualStart,
  ) async {
    final response = await _dio.post(
      '/operations/logs/$logId/start',
      data: {'actual_start': actualStart},
    );
    return response.data;
  }

  Future<Map<String, dynamic>> completeLog(
    String logId,
    Map<String, dynamic> data,
  ) async {
    final response = await _dio.post(
      '/operations/logs/$logId/complete',
      data: data,
    );
    return response.data;
  }

  // Measurements endpoints
  Future<Map<String, dynamic>> getDailyMetrics(String date) async {
    final response = await _dio.get('/measurements/daily/$date');
    return response.data;
  }

  // Process steps endpoints
  Future<List<dynamic>> getTodaySteps() async {
    final response = await _dio.get('/processes/today/steps');
    return response.data;
  }

  // Goals CRUD
  Future<Map<String, dynamic>> createGoal(Map<String, dynamic> data) async {
    final response = await _dio.post('/inputs/goals', data: data);
    return response.data;
  }

  Future<Map<String, dynamic>> updateGoal(
    String goalId,
    Map<String, dynamic> data,
  ) async {
    final response = await _dio.put('/inputs/goals/$goalId', data: data);
    return response.data;
  }

  Future<void> deleteGoal(String goalId) async {
    await _dio.delete('/inputs/goals/$goalId');
  }

  // Processes endpoints
  Future<List<dynamic>> getProcesses() async {
    final response = await _dio.get('/processes');
    return response.data;
  }

  Future<List<dynamic>> getProcessesForGoal(String goalId) async {
    final response = await _dio.get(
      '/processes',
      queryParameters: {'goal_id': goalId},
    );
    return response.data;
  }

  Future<Map<String, dynamic>> createProcess(Map<String, dynamic> data) async {
    final response = await _dio.post('/processes', data: data);
    return response.data;
  }

  Future<Map<String, dynamic>> getProcess(String processId) async {
    final response = await _dio.get('/processes/$processId');
    return response.data;
  }

  Future<void> deleteProcess(String processId) async {
    await _dio.delete('/processes/$processId');
  }

  // Process Steps
  Future<List<dynamic>> getProcessSteps(String processId) async {
    final response = await _dio.get('/processes/$processId/steps');
    return response.data;
  }

  Future<Map<String, dynamic>> createProcessStep(
    String processId,
    Map<String, dynamic> data,
  ) async {
    final response = await _dio.post('/processes/$processId/steps', data: data);
    return response.data;
  }

  // Control & Analytics
  Future<Map<String, dynamic>> getAnalytics() async {
    final response = await _dio.get('/measurements/summary');
    return response.data;
  }

  Future<List<dynamic>> getImprovements() async {
    final response = await _dio.get('/control/improvements');
    return response.data;
  }

  Future<Map<String, dynamic>> analyzeAndSuggest() async {
    final response = await _dio.post('/control/analyze');
    return response.data;
  }
}
