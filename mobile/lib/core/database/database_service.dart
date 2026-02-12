import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:flutter/foundation.dart';
import 'package:sqflite_common_ffi_web/sqflite_ffi_web.dart';

class DatabaseService {
  static Database? _database;

  Future<void> init() async {
    if (_database != null) return;

    try {
      String path;
      if (kIsWeb) {
        databaseFactory = databaseFactoryFfiWeb;
        path = 'igams.db';
      } else {
        final databasePath = await getDatabasesPath();
        path = join(databasePath, 'igams.db');
      }

      _database = await openDatabase(
        path,
        version: 1,
        onCreate: (db, version) async {
          // Daily logs table for offline storage
          await db.execute('''
            CREATE TABLE daily_logs (
              id TEXT PRIMARY KEY,
              step_id TEXT NOT NULL,
              execution_date TEXT NOT NULL,
              status TEXT NOT NULL,
              planned_start TEXT,
              actual_start TEXT,
              actual_end TEXT,
              actual_execution TEXT,
              output_produced TEXT,
              quality_score REAL,
              quality_notes TEXT,
              synced INTEGER DEFAULT 0,
              created_at TEXT NOT NULL,
              updated_at TEXT
            )
          ''');

          // Steps cache
          await db.execute('''
            CREATE TABLE steps_cache (
              id TEXT PRIMARY KEY,
              process_id TEXT NOT NULL,
              name TEXT NOT NULL,
              description TEXT,
              action_verb TEXT,
              sequence_order INTEGER,
              frequency TEXT,
              estimated_duration_minutes INTEGER,
              quality_criteria TEXT,
              expected_output TEXT,
              is_active INTEGER DEFAULT 1,
              cached_at TEXT NOT NULL
            )
          ''');

          // Goals cache
          await db.execute('''
            CREATE TABLE goals_cache (
              id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              description TEXT,
              purpose TEXT NOT NULL,
              status TEXT NOT NULL,
              cached_at TEXT NOT NULL
            )
          ''');
        },
      );
    } catch (e) {
      print('Database initialization failed: $e');
      // On web, if DB fails, we might just want to continue without it for now
      // to avoid white screen.
      if (kIsWeb) {
        print('Proceeding without database on web.');
        return;
      }
      rethrow;
    }
  }

  Database get db {
    if (_database == null) {
      throw Exception('Database not initialized. Call init() first.');
    }
    return _database!;
  }

  // Daily Logs CRUD
  Future<void> saveDailyLog(Map<String, dynamic> log) async {
    await db.insert('daily_logs', {
      ...log,
      'synced': 0,
      'created_at': DateTime.now().toIso8601String(),
    }, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<List<Map<String, dynamic>>> getUnsyncedLogs() async {
    return await db.query('daily_logs', where: 'synced = 0');
  }

  Future<void> markLogSynced(String id) async {
    await db.update(
      'daily_logs',
      {'synced': 1},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<List<Map<String, dynamic>>> getLogsByDate(String date) async {
    return await db.query(
      'daily_logs',
      where: 'execution_date = ?',
      whereArgs: [date],
    );
  }

  // Steps cache
  Future<void> cacheSteps(List<Map<String, dynamic>> steps) async {
    final batch = db.batch();
    for (final step in steps) {
      batch.insert('steps_cache', {
        ...step,
        'cached_at': DateTime.now().toIso8601String(),
      }, conflictAlgorithm: ConflictAlgorithm.replace);
    }
    await batch.commit();
  }

  Future<List<Map<String, dynamic>>> getCachedSteps() async {
    return await db.query('steps_cache', where: 'is_active = 1');
  }

  // Clear cache
  Future<void> clearCache() async {
    await db.delete('steps_cache');
    await db.delete('goals_cache');
  }
}
