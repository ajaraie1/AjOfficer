import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../../core/auth/auth_provider.dart';
import '../../../core/api/api_service.dart';
import '../../../app/routes.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Map<String, dynamic>? _metrics;
  List<dynamic> _goals = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final api = context.read<ApiService>();
    final today = DateFormat('yyyy-MM-dd').format(DateTime.now());

    try {
      final results = await Future.wait([
        api.getDailyMetrics(today).catchError((_) => {}),
        api.getGoals().catchError((_) => []),
      ]);

      setState(() {
        _metrics = results[0] as Map<String, dynamic>?;
        _goals = results[1] as List<dynamic>;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('IGAMS'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await authProvider.logout();
              if (mounted) {
                Navigator.pushReplacementNamed(context, AppRoutes.login);
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
                  // Welcome
                  Text(
                    'Hello, ${authProvider.user?['full_name'] ?? 'User'}',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Focus on process quality, not just completion',
                    style: TextStyle(color: Colors.grey.shade600),
                  ),
                  const SizedBox(height: 24),

                  // Metrics Cards
                  Row(
                    children: [
                      Expanded(
                        child: _MetricCard(
                          title: 'Execution',
                          value: _formatPercent(
                            _metrics?['execution_accuracy'],
                          ),
                          color: Colors.blue,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _MetricCard(
                          title: 'Quality',
                          value: _formatPercent(
                            _metrics?['quality_compliance'],
                          ),
                          color: Colors.green,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _MetricCard(
                          title: 'Time',
                          value: _formatPercent(_metrics?['time_deviation']),
                          color: Colors.orange,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _MetricCard(
                          title: 'Efficiency',
                          value: _formatPercent(
                            _metrics?['process_efficiency'],
                          ),
                          color: Colors.purple,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 32),

                  // Quick Actions
                  Text(
                    'Quick Actions',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _ActionCard(
                          icon: Icons.play_circle,
                          label: 'Daily Operations',
                          color: Colors.blue,
                          onTap: () => Navigator.pushNamed(
                            context,
                            AppRoutes.dailyOperations,
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _ActionCard(
                          icon: Icons.analytics,
                          label: 'Measurements',
                          color: Colors.green,
                          onTap: () => Navigator.pushNamed(
                            context,
                            AppRoutes.measurement,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 32),

                  // Active Goals
                  Text(
                    'Active Goals',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 12),
                  if (_goals.isEmpty)
                    const Card(
                      child: Padding(
                        padding: EdgeInsets.all(24),
                        child: Text(
                          'No goals yet. Create goals in the web dashboard.',
                          textAlign: TextAlign.center,
                        ),
                      ),
                    )
                  else
                    ...(_goals
                        .take(3)
                        .map(
                          (goal) => Card(
                            child: ListTile(
                              leading: const CircleAvatar(
                                child: Icon(Icons.flag),
                              ),
                              title: Text(goal['title'] ?? 'Untitled'),
                              subtitle: Text(
                                goal['purpose'] ?? '',
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                              trailing: Chip(
                                label: Text(
                                  goal['status'] ?? 'draft',
                                  style: const TextStyle(fontSize: 12),
                                ),
                              ),
                            ),
                          ),
                        )),
                ],
              ),
            ),
    );
  }

  String _formatPercent(dynamic value) {
    if (value == null) return '--';
    return '${((value as num) * 100).toStringAsFixed(0)}%';
  }
}

class _MetricCard extends StatelessWidget {
  final String title;
  final String value;
  final Color color;

  const _MetricCard({
    required this.title,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
            ),
            const SizedBox(height: 4),
            Text(
              value,
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

class _ActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ActionCard({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              Icon(icon, size: 32, color: color),
              const SizedBox(height: 8),
              Text(
                label,
                style: const TextStyle(fontWeight: FontWeight.w500),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
