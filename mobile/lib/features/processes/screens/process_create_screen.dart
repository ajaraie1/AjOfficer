import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_service.dart';

class ProcessCreateScreen extends StatefulWidget {
  const ProcessCreateScreen({super.key});

  @override
  State<ProcessCreateScreen> createState() => _ProcessCreateScreenState();
}

class _ProcessCreateScreenState extends State<ProcessCreateScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  String _frequency = 'daily';
  Map<String, dynamic>? _selectedGoal;
  bool _isLoading = false;
  String? _error;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is Map<String, dynamic> && _selectedGoal == null) {
      _selectedGoal = args;
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final apiService = context.read<ApiService>();
      await apiService.createProcess({
        'name': _nameController.text,
        'description': _descriptionController.text,
        'frequency': _frequency,
        'goal_id': _selectedGoal?['id'],
        'status': 'active',
      });

      if (mounted) {
        Navigator.pop(context, true);
      }
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
      appBar: AppBar(title: const Text('إنشاء عملية جديدة')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (_selectedGoal != null)
                Card(
                  color: Theme.of(context).colorScheme.primaryContainer,
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Row(
                      children: [
                        const Icon(Icons.flag),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'مرتبطة بـ: ${_selectedGoal!['title']}',
                            style: const TextStyle(fontWeight: FontWeight.w500),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              const SizedBox(height: 16),

              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'اسم العملية *',
                  hintText: 'مثال: مراجعة المهام اليومية',
                  prefixIcon: Icon(Icons.account_tree),
                ),
                validator: (v) => v?.isEmpty ?? true ? 'مطلوب' : null,
              ),
              const SizedBox(height: 16),

              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'الوصف',
                  prefixIcon: Icon(Icons.description),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 16),

              DropdownButtonFormField<String>(
                value: _frequency,
                decoration: const InputDecoration(
                  labelText: 'التكرار',
                  prefixIcon: Icon(Icons.repeat),
                ),
                items: const [
                  DropdownMenuItem(value: 'daily', child: Text('يومي')),
                  DropdownMenuItem(value: 'weekly', child: Text('أسبوعي')),
                  DropdownMenuItem(value: 'monthly', child: Text('شهري')),
                ],
                onChanged: (v) => setState(() => _frequency = v!),
              ),
              const SizedBox(height: 24),

              if (_error != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: Text(
                    _error!,
                    style: const TextStyle(color: Colors.red),
                  ),
                ),

              ElevatedButton.icon(
                onPressed: _isLoading ? null : _submit,
                icon: _isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.check),
                label: Text(_isLoading ? 'جاري الحفظ...' : 'إنشاء العملية'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
