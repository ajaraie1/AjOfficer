import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_service.dart';
import '../../../app/routes.dart';

class ProcessesListScreen extends StatefulWidget {
  const ProcessesListScreen({super.key});

  @override
  State<ProcessesListScreen> createState() => _ProcessesListScreenState();
}

class _ProcessesListScreenState extends State<ProcessesListScreen> {
  List<Map<String, dynamic>> _processes = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadProcesses();
  }

  Future<void> _loadProcesses() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final apiService = context.read<ApiService>();
      final processes = await apiService.getProcesses();
      setState(() {
        _processes = List<Map<String, dynamic>>.from(processes);
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('العمليات'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadProcesses,
          ),
        ],
      ),
      body: _buildBody(),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          final result = await Navigator.pushNamed(
            context,
            AppRoutes.processCreate,
          );
          if (result == true) _loadProcesses();
        },
        icon: const Icon(Icons.add),
        label: const Text('عملية جديدة'),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.red.shade300),
            const SizedBox(height: 16),
            Text(
              'خطأ في التحميل',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _loadProcesses,
              icon: const Icon(Icons.refresh),
              label: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      );
    }

    if (_processes.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.account_tree_outlined,
              size: 80,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              'لا توجد عمليات',
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadProcesses,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _processes.length,
        itemBuilder: (context, index) {
          final process = _processes[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primaryContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  Icons.account_tree,
                  color: Theme.of(context).colorScheme.primary,
                ),
              ),
              title: Text(process['name'] ?? 'عملية'),
              subtitle: Text(
                '${process['steps_count'] ?? 0} خطوات • ${process['frequency'] ?? 'يومي'}',
              ),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                Navigator.pushNamed(
                  context,
                  AppRoutes.processDetail,
                  arguments: process,
                );
              },
            ),
          );
        },
      ),
    );
  }
}
