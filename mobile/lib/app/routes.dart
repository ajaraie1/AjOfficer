import 'package:flutter/material.dart';
import '../features/daily_operations/screens/daily_operations_screen.dart';
import '../features/daily_operations/screens/login_screen.dart';
import '../features/daily_operations/screens/main_screen.dart';
import '../features/measurement_input/screens/measurement_screen.dart';
import '../features/goals/screens/goals_list_screen.dart';
import '../features/goals/screens/goal_create_screen.dart';
import '../features/goals/screens/goal_detail_screen.dart';
import '../features/processes/screens/processes_list_screen.dart';
import '../features/processes/screens/process_create_screen.dart';
import '../features/processes/screens/process_detail_screen.dart';
import '../features/analytics/screens/analytics_screen.dart';
import '../features/control/screens/improvements_screen.dart';

class AppRoutes {
  static const String login = '/login';
  static const String home = '/home';
  static const String main = '/main';
  static const String dailyOperations = '/daily-operations';
  static const String measurement = '/measurement';

  // Goals
  static const String goals = '/goals';
  static const String goalCreate = '/goals/create';
  static const String goalDetail = '/goals/detail';

  // Processes
  static const String processes = '/processes';
  static const String processCreate = '/processes/create';
  static const String processDetail = '/processes/detail';

  // Analytics & Control
  static const String analytics = '/analytics';
  static const String improvements = '/improvements';

  static Map<String, WidgetBuilder> get routes => {
    login: (context) => const LoginScreen(),
    home: (context) => const MainScreen(),
    main: (context) => const MainScreen(),
    dailyOperations: (context) => const DailyOperationsScreen(),
    measurement: (context) => const MeasurementScreen(),

    // Goals
    goals: (context) => const GoalsListScreen(),
    goalCreate: (context) => const GoalCreateScreen(),
    goalDetail: (context) => const GoalDetailScreen(),

    // Processes
    processes: (context) => const ProcessesListScreen(),
    processCreate: (context) => const ProcessCreateScreen(),
    processDetail: (context) => const ProcessDetailScreen(),

    // Analytics & Control
    analytics: (context) => const AnalyticsScreen(),
    improvements: (context) => const ImprovementsScreen(),
  };
}
