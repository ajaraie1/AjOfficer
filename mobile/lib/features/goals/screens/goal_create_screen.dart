import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_service.dart';

class GoalCreateScreen extends StatefulWidget {
  const GoalCreateScreen({super.key});

  @override
  State<GoalCreateScreen> createState() => _GoalCreateScreenState();
}

class _GoalCreateScreenState extends State<GoalCreateScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _purposeController = TextEditingController();
  final _descriptionController = TextEditingController();
  DateTime? _targetDate;
  bool _isLoading = false;
  String? _error;

  @override
  void dispose() {
    _titleController.dispose();
    _purposeController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _targetDate ?? DateTime.now().add(const Duration(days: 30)),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365 * 5)),
    );
    if (picked != null) {
      setState(() => _targetDate = picked);
    }
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final apiService = context.read<ApiService>();
      await apiService.createGoal({
        'title': _titleController.text,
        'purpose': _purposeController.text,
        'description': _descriptionController.text,
        'target_date': _targetDate?.toIso8601String(),
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
      appBar: AppBar(title: const Text('إنشاء هدف جديد')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Title
              TextFormField(
                controller: _titleController,
                decoration: const InputDecoration(
                  labelText: 'عنوان الهدف *',
                  hintText: 'مثال: إطلاق منتج جديد',
                  prefixIcon: Icon(Icons.flag),
                ),
                validator: (v) => v?.isEmpty ?? true ? 'مطلوب' : null,
              ),
              const SizedBox(height: 16),

              // Purpose
              TextFormField(
                controller: _purposeController,
                decoration: const InputDecoration(
                  labelText: 'الغرض (لماذا؟) *',
                  hintText: 'لماذا هذا الهدف مهم؟',
                  prefixIcon: Icon(Icons.lightbulb_outline),
                ),
                maxLines: 3,
                validator: (v) => v?.isEmpty ?? true ? 'مطلوب' : null,
              ),
              const SizedBox(height: 16),

              // Description
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'الوصف',
                  hintText: 'تفاصيل إضافية عن الهدف',
                  prefixIcon: Icon(Icons.description),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 16),

              // Target Date
              ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.calendar_today),
                title: const Text('تاريخ الإنجاز'),
                subtitle: Text(
                  _targetDate != null
                      ? '${_targetDate!.day}/${_targetDate!.month}/${_targetDate!.year}'
                      : 'اختر تاريخ',
                ),
                trailing: IconButton(
                  icon: const Icon(Icons.edit_calendar),
                  onPressed: _selectDate,
                ),
                onTap: _selectDate,
              ),
              const Divider(),
              const SizedBox(height: 24),

              // Error
              if (_error != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: Text(
                    _error!,
                    style: const TextStyle(color: Colors.red),
                    textAlign: TextAlign.center,
                  ),
                ),

              // Submit Button
              ElevatedButton.icon(
                onPressed: _isLoading ? null : _submit,
                icon: _isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.check),
                label: Text(_isLoading ? 'جاري الحفظ...' : 'إنشاء الهدف'),
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
