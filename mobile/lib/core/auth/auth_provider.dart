import 'package:flutter/foundation.dart';
import '../api/api_service.dart';

class AuthProvider extends ChangeNotifier {
  final ApiService _apiService;

  Map<String, dynamic>? _user;
  bool _isLoading = false;
  String? _error;

  AuthProvider(this._apiService);

  Map<String, dynamic>? get user => _user;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isAuthenticated => _user != null;

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final tokenData = await _apiService.login(email, password);
      await _apiService.setToken(tokenData['access_token']);

      _user = await _apiService.getMe();
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = 'Login failed: ${e.toString()}';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> loginAsGuest() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    const demoEmail = 'demo@igams.app';
    const demoPassword = 'demo123456';
    const demoName = 'Demo User';

    try {
      // Try to login first
      final tokenData = await _apiService.login(demoEmail, demoPassword);
      await _apiService.setToken(tokenData['access_token']);
      _user = await _apiService.getMe();
    } catch (e) {
      // If login fails, register first then login
      try {
        await _apiService.register(demoEmail, demoPassword, demoName);
        final tokenData = await _apiService.login(demoEmail, demoPassword);
        await _apiService.setToken(tokenData['access_token']);
        _user = await _apiService.getMe();
      } catch (e2) {
        _error = 'Demo login failed: ${e2.toString()}';
      }
    }

    _isLoading = false;
    notifyListeners();
  }

  Future<bool> register(String email, String password, String fullName) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _apiService.register(email, password, fullName);
      return await login(email, password);
    } catch (e) {
      _error = 'Registration failed: ${e.toString()}';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    await _apiService.clearToken();
    _user = null;
    notifyListeners();
  }

  Future<void> checkAuth() async {
    if (_apiService.isAuthenticated) {
      try {
        _user = await _apiService.getMe();
        notifyListeners();
      } catch (e) {
        await _apiService.clearToken();
      }
    }
  }
}
