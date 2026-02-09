import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../../core/api/api_service.dart';

class MeasurementScreen extends StatefulWidget {
  const MeasurementScreen({super.key});

  @override
  State<MeasurementScreen> createState() => _MeasurementScreenState();
}

class _MeasurementScreenState extends State<MeasurementScreen> {
  Map<String, dynamic>? _metrics;
  Map<String, dynamic>? _issues;
  bool _loading = true;
  DateTime _selectedDate = DateTime.now();

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final api = context.read<ApiService>();
    final dateStr = DateFormat('yyyy-MM-dd').format(_selectedDate);

    setState(() => _loading = true);

    try {
      final metrics = await api.getDailyMetrics(dateStr);
      setState(() {
        _metrics = metrics;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _metrics = null;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Measurements'),
        actions: [
          IconButton(
            icon: const Icon(Icons.calendar_today),
            onPressed: () async {
              final date = await showDatePicker(
                context: context,
                initialDate: _selectedDate,
                firstDate: DateTime.now().subtract(const Duration(days: 90)),
                lastDate: DateTime.now(),
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
                  const SizedBox(height: 8),
                  Text(
                    'Process Quality Metrics',
                    style: TextStyle(color: Colors.grey.shade600),
                  ),
                  const SizedBox(height: 24),

                  if (_metrics == null)
                    const Card(
                      child: Padding(
                        padding: EdgeInsets.all(24),
                        child: Column(
                          children: [
                            Icon(
                              Icons.analytics_outlined,
                              size: 48,
                              color: Colors.grey,
                            ),
                            SizedBox(height: 8),
                            Text('No measurements for this date'),
                          ],
                        ),
                      ),
                    )
                  else ...[
                    // Core Metrics
                    _MetricRow(
                      icon: Icons.check_circle,
                      label: 'Execution Accuracy',
                      description: 'Planned vs Actual steps ratio',
                      value: _metrics!['execution_accuracy'],
                      color: Colors.blue,
                    ),
                    const SizedBox(height: 12),
                    _MetricRow(
                      icon: Icons.star,
                      label: 'Quality Compliance',
                      description: 'Meeting quality criteria',
                      value: _metrics!['quality_compliance'],
                      color: Colors.green,
                    ),
                    const SizedBox(height: 12),
                    _MetricRow(
                      icon: Icons.timer,
                      label: 'Time Deviation',
                      description: 'Planned vs Actual time ratio',
                      value: _metrics!['time_deviation'],
                      color: _getTimeColor(_metrics!['time_deviation']),
                    ),
                    const SizedBox(height: 12),
                    _MetricRow(
                      icon: Icons.trending_up,
                      label: 'Process Efficiency',
                      description: 'Output/Effort ratio',
                      value: _metrics!['process_efficiency'],
                      color: Colors.purple,
                    ),
                    const SizedBox(height: 24),

                    // Key Insights
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Key Insights',
                              style: TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: 16,
                              ),
                            ),
                            const SizedBox(height: 12),
                            _InsightItem(
                              isPositive:
                                  (_metrics!['execution_accuracy'] ?? 0) >= 0.7,
                              text: _getExecutionInsight(
                                _metrics!['execution_accuracy'],
                              ),
                            ),
                            const SizedBox(height: 8),
                            _InsightItem(
                              isPositive:
                                  (_metrics!['quality_compliance'] ?? 0) >= 0.7,
                              text: _getQualityInsight(
                                _metrics!['quality_compliance'],
                              ),
                            ),
                            const SizedBox(height: 8),
                            _InsightItem(
                              isPositive:
                                  (_metrics!['time_deviation'] ?? 1) <= 1.2,
                              text: _getTimeInsight(
                                _metrics!['time_deviation'],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Focus Note
                    Card(
                      color: Colors.blue.shade50,
                      child: const Padding(
                        padding: EdgeInsets.all(16),
                        child: Row(
                          children: [
                            Icon(Icons.info_outline, color: Colors.blue),
                            SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                'Focus on HOW you execute, not just WHAT you complete. Quality matters more than quantity.',
                                style: TextStyle(
                                  color: Colors.blue,
                                  fontSize: 13,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
    );
  }

  Color _getTimeColor(dynamic value) {
    if (value == null) return Colors.grey;
    if (value <= 1.0) return Colors.green;
    if (value <= 1.2) return Colors.orange;
    return Colors.red;
  }

  String _getExecutionInsight(dynamic value) {
    if (value == null) return 'No execution data available';
    if (value >= 0.9) return 'Excellent execution accuracy';
    if (value >= 0.7) return 'Good execution, room for improvement';
    if (value >= 0.5) return 'Moderate execution - review your process';
    return 'Low execution - consider simplifying steps';
  }

  String _getQualityInsight(dynamic value) {
    if (value == null) return 'No quality data available';
    if (value >= 0.9) return 'Outstanding quality compliance';
    if (value >= 0.7) return 'Quality standards mostly met';
    if (value >= 0.5) return 'Quality needs attention';
    return 'Quality below threshold - simplify criteria';
  }

  String _getTimeInsight(dynamic value) {
    if (value == null) return 'No time data available';
    if (value <= 1.0) return 'Time estimates accurate or under';
    if (value <= 1.2) return 'Slightly over estimated time';
    if (value <= 1.5) return 'Significant time overrun';
    return 'Major time deviation - consider splitting steps';
  }
}

class _MetricRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String description;
  final dynamic value;
  final Color color;

  const _MetricRow({
    required this.icon,
    required this.label,
    required this.description,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final percent = value != null ? ((value as num) * 100).toInt() : 0;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: const TextStyle(fontWeight: FontWeight.w600),
                  ),
                  Text(
                    description,
                    style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                  ),
                ],
              ),
            ),
            Text(
              value != null ? '$percent%' : '--',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InsightItem extends StatelessWidget {
  final bool isPositive;
  final String text;

  const _InsightItem({required this.isPositive, required this.text});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(
          isPositive ? Icons.check_circle : Icons.info_outline,
          size: 16,
          color: isPositive ? Colors.green : Colors.orange,
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            text,
            style: TextStyle(fontSize: 13, color: Colors.grey.shade700),
          ),
        ),
      ],
    );
  }
}
