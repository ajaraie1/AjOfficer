import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_service.dart';

class ProcessDetailScreen extends StatefulWidget {
  const ProcessDetailScreen({super.key});

  @override
  State<ProcessDetailScreen> createState() => _ProcessDetailScreenState();
}

class _ProcessDetailScreenState extends State<ProcessDetailScreen> {
  Map<String, dynamic>? _process;
  List<Map<String, dynamic>> _steps = [];
  bool _isLoading = true;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is Map<String, dynamic> && _process == null) {
      _process = args;
      _loadSteps();
    }
  }

  Future<void> _loadSteps() async {
    if (_process == null) return;

    try {
      final apiService = context.read<ApiService>();
      final steps = await apiService.getProcessSteps(
        _process!['id'].toString(),
      );
      setState(() {
        _steps = List<Map<String, dynamic>>.from(steps);
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _addStep() async {
    final nameController = TextEditingController();
    final criteriaController = TextEditingController();
    final outputController = TextEditingController();
    final durationController = TextEditingController();

    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('إضافة خطوة ذكية'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: const InputDecoration(
                  labelText: 'اسم الخطوة *',
                  hintText: 'مثال: مراجعة البريد',
                  prefixIcon: Icon(Icons.task_alt),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: criteriaController,
                decoration: const InputDecoration(
                  labelText: 'معيار الجودة (كيف ننفذ صح؟)',
                  hintText: 'مثال: الرد خلال 24 ساعة، نبرة مهنية',
                  prefixIcon: Icon(Icons.verified_user),
                ),
                maxLines: 2,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: outputController,
                decoration: const InputDecoration(
                  labelText: 'المخرج المتوقع (ما النتيجة؟)',
                  hintText: 'مثال: صندوق وارد فارغ، 5 ردود مرسلة',
                  prefixIcon: Icon(Icons.output),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: durationController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'المدة المقدرة (دقيقة)',
                  hintText: 'مثال: 15',
                  prefixIcon: Icon(Icons.timer),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('إضافة'),
          ),
        ],
      ),
    );

    if (result == true && nameController.text.isNotEmpty) {
      try {
        final apiService = context.read<ApiService>();
        await apiService.createProcessStep(_process!['id'].toString(), {
          'name': nameController.text,
          'quality_criteria': criteriaController.text,
          'expected_output': outputController.text,
          'estimated_duration_minutes': int.tryParse(durationController.text),
          'order_index': _steps.length,
        });
        _loadSteps();
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(SnackBar(content: Text('خطأ: $e')));
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_process == null) {
      return const Scaffold(body: Center(child: Text('لا توجد بيانات')));
    }

    return Scaffold(
      appBar: AppBar(title: Text(_process!['name'] ?? 'العملية')),
      body: Column(
        children: [
          // Header
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            color: Theme.of(context).colorScheme.primaryContainer,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _process!['name'] ?? '',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                if (_process!['description'] != null) ...[
                  const SizedBox(height: 8),
                  Text(_process!['description']),
                ],
                const SizedBox(height: 8),
                Chip(
                  label: Text(_process!['frequency'] ?? 'يومي'),
                  avatar: const Icon(Icons.repeat, size: 16),
                ),
              ],
            ),
          ),

          // Steps
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _steps.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.list_alt,
                          size: 64,
                          color: Colors.grey.shade400,
                        ),
                        const SizedBox(height: 16),
                        const Text('لا توجد خطوات'),
                        const SizedBox(height: 16),
                        ElevatedButton.icon(
                          onPressed: _addStep,
                          icon: const Icon(Icons.add),
                          label: const Text('إضافة خطوة'),
                        ),
                      ],
                    ),
                  )
                : ReorderableListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _steps.length,
                    onReorder: (oldIndex, newIndex) {
                      setState(() {
                        if (newIndex > oldIndex) newIndex--;
                        final step = _steps.removeAt(oldIndex);
                        _steps.insert(newIndex, step);
                      });
                    },
                    itemBuilder: (context, index) {
                      final step = _steps[index];
                      return Card(
                        key: ValueKey(step['id']),
                        margin: const EdgeInsets.only(bottom: 8),
                        child: ListTile(
                          leading: CircleAvatar(child: Text('${index + 1}')),
                          title: Text(step['name'] ?? 'خطوة'),
                          subtitle: step['quality_criteria'] != null
                              ? Text(step['quality_criteria'])
                              : null,
                          trailing: const Icon(Icons.drag_handle),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _addStep,
        child: const Icon(Icons.add),
      ),
    );
  }
}
