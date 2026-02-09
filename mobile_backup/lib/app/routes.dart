import 'package:flutter/material.dart';
import '../features/daily_operations/screens/daily_operations_screen.dart';
import '../features/daily_operations/screens/login_screen.dart';
import '../features/daily_operations/screens/home_screen.dart';
import '../features/measurement_input/screens/measurement_screen.dart';

class AppRoutes {
  static const String login = '/login';
  static const String home = '/home';
  static const String dailyOperations = '/daily-operations';
  static const String measurement = '/measurement';

  static Map<String, WidgetBuilder> get routes => {
    login: (context) => const LoginScreen(),
    home: (context) => const HomeScreen(),
    dailyOperations: (context) => const DailyOperationsScreen(),
    measurement: (context) => const MeasurementScreen(),
  };
}
