import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'app/app.dart';
import 'core/auth/auth_provider.dart';
import 'core/api/api_service.dart';
import 'core/database/database_service.dart';
import 'core/sync/sync_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize services
  final databaseService = DatabaseService();
  await databaseService.init();
  
  final apiService = ApiService();
  final syncService = SyncService(apiService, databaseService);
  
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider(apiService)),
        Provider.value(value: apiService),
        Provider.value(value: databaseService),
        Provider.value(value: syncService),
      ],
      child: const IGAMSApp(),
    ),
  );
}
