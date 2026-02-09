import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../../core/auth/auth_provider.dart';
import '../../../core/api/api_service.dart';
import '../../../app/routes.dart';
import '../../goals/screens/goals_list_screen.dart';
import '../../processes/screens/processes_list_screen.dart';
import '../../analytics/screens/analytics_screen.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const _HomeTab(),
    const GoalsListScreen(),
    const ProcessesListScreen(),
    const AnalyticsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _currentIndex, children: _screens),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() => _currentIndex = index);
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'الرئيسية',
          ),
          NavigationDestination(
            icon: Icon(Icons.flag_outlined),
            selectedIcon: Icon(Icons.flag),
            label: 'الأهداف',
          ),
          NavigationDestination(
            icon: Icon(Icons.account_tree_outlined),
            selectedIcon: Icon(Icons.account_tree),
            label: 'العمليات',
          ),
          NavigationDestination(
            icon: Icon(Icons.analytics_outlined),
            selectedIcon: Icon(Icons.analytics),
            label: 'التحليلات',
          ),
        ],
      ),
    );
  }
}

class _HomeTab extends StatefulWidget {
  const _HomeTab();

  @override
  State<_HomeTab> createState() => _HomeTabState();
}

class _HomeTabState extends State<_HomeTab> {
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
        api.getDailyMetrics(today).catchError((_) => <String, dynamic>{}),
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

  String _formatPercent(dynamic value) {
    if (value == null) return '--';
    return '${((value as num) * 100).toStringAsFixed(0)}%';
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('IGAMS'),
        actions: [
          IconButton(
            icon: const Icon(Icons.auto_awesome),
            tooltip: 'التحسينات',
            onPressed: () =>
                Navigator.pushNamed(context, AppRoutes.improvements),
          ),
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
                    'مرحباً، ${authProvider.user?['full_name'] ?? 'User'}',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'ركز على جودة العمليات، وليس فقط الإنجاز',
                    style: TextStyle(color: Colors.grey.shade600),
                  ),
                  const SizedBox(height: 24),

                  // Metrics Cards
                  Row(
                    children: [
                      Expanded(
                        child: _MetricCard(
                          title: 'التنفيذ',
                          value: _formatPercent(
                            _metrics?['execution_accuracy'],
                          ),
                          color: Colors.blue,
                          icon: Icons.play_circle,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _MetricCard(
                          title: 'الجودة',
                          value: _formatPercent(
                            _metrics?['quality_compliance'],
                          ),
                          color: Colors.green,
                          icon: Icons.star,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _MetricCard(
                          title: 'الوقت',
                          value: _formatPercent(_metrics?['time_deviation']),
                          color: Colors.orange,
                          icon: Icons.timer,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _MetricCard(
                          title: 'الكفاءة',
                          value: _formatPercent(
                            _metrics?['process_efficiency'],
                          ),
                          color: Colors.purple,
                          icon: Icons.speed,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 32),

                  // Quick Actions
                  Text(
                    'الإجراءات السريعة',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _ActionCard(
                          icon: Icons.play_circle,
                          label: 'العمليات اليومية',
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
                          icon: Icons.add_chart,
                          label: 'القياسات',
                          color: Colors.green,
                          onTap: () => Navigator.pushNamed(
                            context,
                            AppRoutes.measurement,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _ActionCard(
                          icon: Icons.add_circle,
                          label: 'هدف جديد',
                          color: Colors.teal,
                          onTap: () => Navigator.pushNamed(
                            context,
                            AppRoutes.goalCreate,
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _ActionCard(
                          icon: Icons.auto_awesome,
                          label: 'التحسينات AI',
                          color: Colors.deepPurple,
                          onTap: () => Navigator.pushNamed(
                            context,
                            AppRoutes.improvements,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 32),

                  // Active Goals
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'الأهداف النشطة',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      TextButton(
                        onPressed: () =>
                            Navigator.pushNamed(context, AppRoutes.goals),
                        child: const Text('عرض الكل'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  if (_goals.isEmpty)
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(24),
                        child: Column(
                          children: [
                            Icon(
                              Icons.flag_outlined,
                              size: 48,
                              color: Colors.grey.shade400,
                            ),
                            const SizedBox(height: 8),
                            const Text(
                              'لا توجد أهداف بعد',
                              textAlign: TextAlign.center,
                            ),
                            const SizedBox(height: 12),
                            ElevatedButton.icon(
                              onPressed: () => Navigator.pushNamed(
                                context,
                                AppRoutes.goalCreate,
                              ),
                              icon: const Icon(Icons.add),
                              label: const Text('إنشاء هدف'),
                            ),
                          ],
                        ),
                      ),
                    )
                  else
                    ...(_goals
                        .take(3)
                        .map(
                          (goal) => Card(
                            margin: const EdgeInsets.only(bottom: 8),
                            child: ListTile(
                              leading: Container(
                                width: 40,
                                height: 40,
                                decoration: BoxDecoration(
                                  color: Theme.of(
                                    context,
                                  ).colorScheme.primaryContainer,
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Icon(
                                  Icons.flag,
                                  color: Theme.of(context).colorScheme.primary,
                                ),
                              ),
                              title: Text(goal['title'] ?? 'بدون عنوان'),
                              subtitle: Text(
                                goal['purpose'] ?? '',
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                              trailing: const Icon(Icons.chevron_right),
                              onTap: () => Navigator.pushNamed(
                                context,
                                AppRoutes.goalDetail,
                                arguments: goal,
                              ),
                            ),
                          ),
                        )),
                ],
              ),
            ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String title;
  final String value;
  final Color color;
  final IconData icon;

  const _MetricCard({
    required this.title,
    required this.value,
    required this.color,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 16, color: color),
                const SizedBox(width: 4),
                Text(
                  title,
                  style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 28,
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
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, size: 28, color: color),
              ),
              const SizedBox(height: 8),
              Text(
                label,
                style: const TextStyle(
                  fontWeight: FontWeight.w500,
                  fontSize: 13,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
