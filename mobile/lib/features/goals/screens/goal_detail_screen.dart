import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../../core/api/api_service.dart';
import '../../../app/routes.dart';

class GoalDetailScreen extends StatefulWidget {
  const GoalDetailScreen({super.key});

  @override
  State<GoalDetailScreen> createState() => _GoalDetailScreenState();
}

class _GoalDetailScreenState extends State<GoalDetailScreen> {
  Map<String, dynamic>? _goal;
  List<Map<String, dynamic>> _processes = [];
  bool _isLoading = true;
  bool _isDeleting = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is Map<String, dynamic> && _goal == null) {
      _goal = args;
      _loadProcesses();
    }
  }

  Future<void> _loadProcesses() async {
    if (_goal == null) return;

    setState(() => _isLoading = true);
    try {
      final apiService = context.read<ApiService>();
      final processes = await apiService.getProcessesForGoal(_goal!['id']);
      setState(() {
        _processes = List<Map<String, dynamic>>.from(processes);
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _deleteGoal() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('حذف الهدف'),
        content: const Text(
          'هل أنت متأكد من حذف هذا الهدف؟ سيتم حذف جميع العمليات المرتبطة.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('حذف'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    setState(() => _isDeleting = true);
    try {
      final apiService = context.read<ApiService>();
      await apiService.deleteGoal(_goal!['id']);
      if (mounted) {
        Navigator.pop(context, true);
      }
    } catch (e) {
      setState(() => _isDeleting = false);
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('خطأ: $e')));
      }
    }
  }

  Color _getStatusColor(String? status) {
    switch (status?.toLowerCase()) {
      case 'active':
        return Colors.green;
      case 'completed':
        return Colors.blue;
      case 'paused':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_goal == null) {
      return const Scaffold(body: Center(child: Text('لا توجد بيانات')));
    }

    final deadline = _goal!['target_date'] != null
        ? DateFormat(
            'dd MMMM yyyy',
          ).format(DateTime.parse(_goal!['target_date']))
        : 'غير محدد';

    return Scaffold(
      appBar: AppBar(
        title: const Text('تفاصيل الهدف'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () {
              // TODO: Navigate to edit screen
            },
          ),
          IconButton(
            icon: _isDeleting
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.delete),
            onPressed: _isDeleting ? null : _deleteGoal,
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Theme.of(context).colorScheme.primary,
                    Theme.of(context).colorScheme.primary.withOpacity(0.7),
                  ],
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          _goal!['status'] ?? 'draft',
                          style: const TextStyle(color: Colors.white),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    _goal!['title'] ?? '',
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      const Icon(
                        Icons.calendar_today,
                        color: Colors.white70,
                        size: 16,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        deadline,
                        style: const TextStyle(color: Colors.white70),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // Purpose
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildSection(
                    'الغرض',
                    Icons.lightbulb_outline,
                    _goal!['purpose'] ?? 'غير محدد',
                  ),
                  const SizedBox(height: 16),
                  if (_goal!['description'] != null)
                    _buildSection(
                      'الوصف',
                      Icons.description,
                      _goal!['description'],
                    ),
                ],
              ),
            ),

            const Divider(),

            // Processes Section
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'العمليات',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      TextButton.icon(
                        onPressed: () async {
                          final result = await Navigator.pushNamed(
                            context,
                            AppRoutes.processCreate,
                            arguments: _goal,
                          );
                          if (result == true) _loadProcesses();
                        },
                        icon: const Icon(Icons.add),
                        label: const Text('إضافة'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  if (_isLoading)
                    const Center(child: CircularProgressIndicator())
                  else if (_processes.isEmpty)
                    Center(
                      child: Padding(
                        padding: const EdgeInsets.all(32),
                        child: Column(
                          children: [
                            Icon(
                              Icons.account_tree,
                              size: 48,
                              color: Colors.grey.shade400,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'لا توجد عمليات',
                              style: TextStyle(color: Colors.grey.shade600),
                            ),
                          ],
                        ),
                      ),
                    )
                  else
                    ...(_processes.map(
                      (process) => _ProcessCard(
                        process: process,
                        onTap: () {
                          Navigator.pushNamed(
                            context,
                            AppRoutes.processDetail,
                            arguments: process,
                          );
                        },
                      ),
                    )),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(String title, IconData icon, String content) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 20, color: Theme.of(context).colorScheme.primary),
            const SizedBox(width: 8),
            Text(
              title,
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          content,
          style: TextStyle(color: Colors.grey.shade700, height: 1.5),
        ),
      ],
    );
  }
}

class _ProcessCard extends StatelessWidget {
  final Map<String, dynamic> process;
  final VoidCallback onTap;

  const _ProcessCard({required this.process, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        onTap: onTap,
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.primaryContainer,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            Icons.account_tree,
            color: Theme.of(context).colorScheme.primary,
          ),
        ),
        title: Text(process['name'] ?? 'عملية'),
        subtitle: Text('${process['steps_count'] ?? 0} خطوات'),
        trailing: const Icon(Icons.chevron_right),
      ),
    );
  }
}
