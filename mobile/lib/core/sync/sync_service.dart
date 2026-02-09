import 'package:connectivity_plus/connectivity_plus.dart';
import '../api/api_service.dart';
import '../database/database_service.dart';

class SyncService {
  final ApiService _apiService;
  final DatabaseService _databaseService;

  SyncService(this._apiService, this._databaseService);

  Future<bool> isOnline() async {
    final result = await Connectivity().checkConnectivity();
    return result != ConnectivityResult.none;
  }

  Future<void> syncAll() async {
    if (!await isOnline()) return;

    // Sync unsynced logs
    await syncLogs();

    // Refresh cached data
    await refreshCache();
  }

  Future<void> syncLogs() async {
    if (!await isOnline()) return;

    final unsyncedLogs = await _databaseService.getUnsyncedLogs();

    for (final log in unsyncedLogs) {
      try {
        // Create or update log on server
        await _apiService.createDailyLog(log);
        await _databaseService.markLogSynced(log['id']);
      } catch (e) {
        // Keep for next sync attempt
        print('Failed to sync log ${log['id']}: $e');
      }
    }
  }

  Future<void> refreshCache() async {
    if (!await isOnline()) return;

    try {
      // Cache today's steps
      final steps = await _apiService.getTodaySteps();
      await _databaseService.cacheSteps(steps.cast<Map<String, dynamic>>());
    } catch (e) {
      print('Failed to refresh cache: $e');
    }
  }
}
