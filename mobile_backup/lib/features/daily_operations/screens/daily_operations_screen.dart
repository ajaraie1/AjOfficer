import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../../core/api/api_service.dart';
import '../../../core/database/database_service.dart';
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
    } catch (e) {
      setState(() => _loading = false);
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

  Future<void> _completeStep(Map<String, dynamic> log) async {
    final qualityScore = await _showQualityDialog();
    if (qualityScore == null) return;

    final api = context.read<ApiService>();
    final db = context.read<DatabaseService>();
    final now = DateTime.now().toIso8601String();

    final updatedLog = {
      ...log,
      'actual_end': now,
      'status': 'completed',
      'quality_score': qualityScore,
    };

    await db.saveDailyLog(updatedLog);

    try {
      await api.completeLog(log['id'], {
        'actual_end': now,
        'actual_execution': 'Completed via mobile',
        'quality_score': qualityScore,
      });
    } catch (e) {
      // Will sync later
    }

    await _loadData();
  }

  Future<double?> _showQualityDialog() async {
    double score = 0.8;
    return showDialog<double>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Rate Quality'),
        content: StatefulBuilder(
          builder: (context, setState) => Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'How well did the execution meet quality criteria?',
                style: TextStyle(color: Colors.grey.shade600),
              ),
              const SizedBox(height: 16),
              Slider(
                value: score,
                onChanged: (v) => setState(() => score = v),
                divisions: 10,
                label: '${(score * 100).toInt()}%',
              ),
              Text(
                '${(score * 100).toInt()}%',
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, score),
            child: const Text('Save'),
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
                                      onPressed: () => _completeStep(log),
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
