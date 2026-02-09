import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../../core/api/api_service.dart';
import '../../../core/database/database_service.dart';
import '../../../core/services/notification_service.dart';
import 'package:uuid/uuid.dart';

class DailyOperationsScreen extends StatefulWidget {
  const DailyOperationsScreen({super.key});

  @override
  State<DailyOperationsScreen> createState() => _DailyOperationsScreenState();
}

class _DailyOperationsScreenState extends State<DailyOperationsScreen> {
  List<dynamic> _logs = [];
  List<dynamic> _steps = [];
  bool _loading = true;
  DateTime _selectedDate = DateTime.now();

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final api = context.read<ApiService>();
    final db = context.read<DatabaseService>();
    final dateStr = DateFormat('yyyy-MM-dd').format(_selectedDate);

    setState(() => _loading = true);

    try {
      // Try API first, fall back to cache
      final logs = await api.getDailyLogs(dateStr).catchError((_) async {
        return await db.getLogsByDate(dateStr);
      });

      final steps = await api.getTodaySteps().catchError((_) async {
        return await db.getCachedSteps();
      });

      setState(() {
        _logs = logs;
        _steps = steps;
        _loading = false;
      });

      _scheduleReminders(logs, steps);
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  Future<void> _scheduleReminders(
    List<dynamic> logs,
    List<dynamic> steps,
  ) async {
    final notificationService = NotificationService();
    // Cancel existing to avoid duplicates
    await notificationService.cancelAll();

    for (final log in logs) {
      if (log['status'] != 'pending') continue;

      final plannedStartStr = log['planned_start'];
      if (plannedStartStr == null) continue;

      final plannedStart = DateTime.parse(plannedStartStr);
      final now = DateTime.now();

      // If it's in the past, don't schedule
      if (plannedStart.isBefore(now)) continue;

      // Find step details
      final step = steps.firstWhere(
        (s) => s['id'] == log['step_id'],
        orElse: () => null,
      );

      if (step == null) continue;

      // Schedule 10 mins before
      final scheduledTime = plannedStart.subtract(const Duration(minutes: 10));

      if (scheduledTime.isAfter(now)) {
        // Create a unique ID from the log ID (hashCode is simple but might collide, strict app would use int map)
        // For MVP, hashCode of string UUID is okay-ish.
        await notificationService.scheduleNotification(
          id: log['id'].hashCode,
          title: 'Upcoming Task: ${step['name']}',
          body: 'Starts at ${DateFormat('HH:mm').format(plannedStart)}',
          scheduledDate: scheduledTime,
        );
      }
    }
  }

  Future<void> _startStep(Map<String, dynamic> step) async {
    final api = context.read<ApiService>();
    final db = context.read<DatabaseService>();
    final dateStr = DateFormat('yyyy-MM-dd').format(_selectedDate);
    final now = DateTime.now().toIso8601String();
    final uuid = const Uuid();

    // Create log
    final logData = {
      'id': uuid.v4(),
      'step_id': step['id'],
      'execution_date': dateStr,
      'actual_start': now,
      'status': 'in_progress',
    };

    // Save locally first
    await db.saveDailyLog(logData);

    // Try to sync
    try {
      await api.createDailyLog(logData);
      await api.startLog(logData['id']!, now);
    } catch (e) {
      // Will sync later
    }

    await _loadData();

    if (mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Started: ${step['name']}')));
    }
  }

  Future<void> _completeStep(
    Map<String, dynamic> log,
    Map<String, dynamic> step,
  ) async {
    final result = await _showQualityDialog(step);
    if (result == null) return;

    final qualityScore = result['score'] as double;
    final actualOutput = result['output'] as String;

    final api = context.read<ApiService>();
    final db = context.read<DatabaseService>();
    final now = DateTime.now().toIso8601String();

    final updatedLog = {
      ...log,
      'actual_end': now,
      'status': 'completed',
      'quality_score': qualityScore,
      'actual_execution': actualOutput,
    };

    await db.saveDailyLog(updatedLog);

    try {
      await api.completeLog(log['id'], {
        'actual_end': now,
        'actual_execution': actualOutput,
        'quality_score': qualityScore,
      });
    } catch (e) {
      // Will sync later
    }

    await _loadData();
  }

  Future<Map<String, dynamic>?> _showQualityDialog(
    Map<String, dynamic> step,
  ) async {
    double score = 0.8;
    final outputController = TextEditingController();

    return showDialog<Map<String, dynamic>>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('فحص الجودة'),
        content: StatefulBuilder(
          builder: (context, setState) => SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (step['quality_criteria'] != null) ...[
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.amber.shade50,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.amber.shade200),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'معايير الجودة المطلوبة:',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.amber,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(step['quality_criteria']),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                TextField(
                  controller: outputController,
                  decoration: InputDecoration(
                    labelText: 'ماذا أنجزت فعلياً؟',
                    hintText: step['expected_output'] != null
                        ? 'المتوقع: ${step['expected_output']}'
                        : 'صف المخرج النهائي...',
                    border: const OutlineInputBorder(),
                  ),
                  maxLines: 2,
                ),
                const SizedBox(height: 16),

                Text(
                  'مستوى الجودة: ${(score * 100).toInt()}%',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Slider(
                  value: score,
                  onChanged: (v) => setState(() => score = v),
                  divisions: 10,
                  label: '${(score * 100).toInt()}%',
                  activeColor: score < 0.5 ? Colors.red : Colors.green,
                ),
                if (score < 0.6)
                  const Text(
                    '⚠️ جودة منخفضة تعني الحاجة للتحسين',
                    style: TextStyle(color: Colors.red, fontSize: 12),
                  ),
              ],
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, {
              'score': score,
              'output': outputController.text.isEmpty
                  ? 'تم الإنجاز'
                  : outputController.text,
            }),
            child: const Text('تأكيد الإنجاز'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Daily Operations'),
        actions: [
          IconButton(
            icon: const Icon(Icons.calendar_today),
            onPressed: () async {
              final date = await showDatePicker(
                context: context,
                initialDate: _selectedDate,
                firstDate: DateTime.now().subtract(const Duration(days: 30)),
                lastDate: DateTime.now().add(const Duration(days: 7)),
              );
              if (date != null) {
                setState(() => _selectedDate = date);
                _loadData();
              }
            },
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadData,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  // Date header
                  Text(
                    DateFormat('EEEE, MMMM d').format(_selectedDate),
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 16),

                  // Today's Steps
                  if (_steps.isEmpty)
                    const Card(
                      child: Padding(
                        padding: EdgeInsets.all(24),
                        child: Column(
                          children: [
                            Icon(
                              Icons.check_circle,
                              size: 48,
                              color: Colors.green,
                            ),
                            SizedBox(height: 8),
                            Text('No steps scheduled for today'),
                          ],
                        ),
                      ),
                    )
                  else
                    ..._steps.map((step) {
                      final log = _logs.firstWhere(
                        (l) => l['step_id'] == step['id'],
                        orElse: () => null,
                      );
                      final status = log?['status'] ?? 'pending';

                      return Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  _StatusIcon(status: status),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          step['name'] ?? 'Step',
                                          style: const TextStyle(
                                            fontWeight: FontWeight.w600,
                                            fontSize: 16,
                                          ),
                                        ),
                                        if (step['action_verb'] != null)
                                          Text(
                                            step['action_verb'],
                                            style: TextStyle(
                                              color: Theme.of(
                                                context,
                                              ).colorScheme.primary,
                                              fontSize: 12,
                                            ),
                                          ),
                                      ],
                                    ),
                                  ),
                                  if (step['estimated_duration_minutes'] !=
                                      null)
                                    Chip(
                                      label: Text(
                                        '${step['estimated_duration_minutes']} min',
                                      ),
                                      visualDensity: VisualDensity.compact,
                                    ),
                                ],
                              ),
                              if (step['quality_criteria'] != null) ...[
                                const SizedBox(height: 8),
                                Text(
                                  'Quality: ${step['quality_criteria']}',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.grey.shade600,
                                  ),
                                ),
                              ],
                              const SizedBox(height: 12),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.end,
                                children: [
                                  if (status == 'pending')
                                    ElevatedButton.icon(
                                      onPressed: () => _startStep(step),
                                      icon: const Icon(Icons.play_arrow),
                                      label: const Text('Start'),
                                    ),
                                  if (status == 'in_progress')
                                    ElevatedButton.icon(
                                      onPressed: () =>
                                          _completeStep(log!, step),
                                      icon: const Icon(Icons.check),
                                      label: const Text('Complete'),
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: Colors.green,
                                      ),
                                    ),
                                  if (status == 'completed')
                                    const Chip(
                                      label: Text('Completed'),
                                      backgroundColor: Colors.green,
                                      labelStyle: TextStyle(
                                        color: Colors.white,
                                      ),
                                    ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      );
                    }),
                ],
              ),
            ),
    );
  }
}

class _StatusIcon extends StatelessWidget {
  final String status;

  const _StatusIcon({required this.status});

  @override
  Widget build(BuildContext context) {
    IconData icon;
    Color color;

    switch (status) {
      case 'completed':
        icon = Icons.check_circle;
        color = Colors.green;
        break;
      case 'in_progress':
        icon = Icons.play_circle;
        color = Colors.blue;
        break;
      case 'skipped':
        icon = Icons.skip_next;
        color = Colors.orange;
        break;
      default:
        icon = Icons.circle_outlined;
        color = Colors.grey;
    }

    return Icon(icon, color: color, size: 28);
  }
}
