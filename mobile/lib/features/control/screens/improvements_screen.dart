import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/api/api_service.dart';

class ImprovementsScreen extends StatefulWidget {
  const ImprovementsScreen({super.key});

  @override
  State<ImprovementsScreen> createState() => _ImprovementsScreenState();
}

class _ImprovementsScreenState extends State<ImprovementsScreen> {
  List<Map<String, dynamic>> _improvements = [];
  bool _isLoading = true;
  bool _isAnalyzing = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadImprovements();
  }

  Future<void> _loadImprovements() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final apiService = context.read<ApiService>();
      final data = await apiService.getImprovements();
      setState(() {
        _improvements = List<Map<String, dynamic>>.from(data);
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _analyzeAndSuggest() async {
    setState(() => _isAnalyzing = true);

    try {
      final apiService = context.read<ApiService>();
      await apiService.analyzeAndSuggest();
      await _loadImprovements();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('خطأ: $e')));
      }
    }

    setState(() => _isAnalyzing = false);
  }

  Color _getTypeColor(String? type) {
    switch (type?.toLowerCase()) {
      case 'simplify':
        return Colors.green;
      case 'remove':
        return Colors.red;
      case 'reorder':
        return Colors.blue;
      case 'alternative':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  IconData _getTypeIcon(String? type) {
    switch (type?.toLowerCase()) {
      case 'simplify':
        return Icons.compress;
      case 'remove':
        return Icons.delete_outline;
      case 'reorder':
        return Icons.swap_vert;
      case 'alternative':
        return Icons.alt_route;
      default:
        return Icons.lightbulb_outline;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('التحسينات المقترحة'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadImprovements,
          ),
        ],
      ),
      body: _buildBody(),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _isAnalyzing ? null : _analyzeAndSuggest,
        icon: _isAnalyzing
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              )
            : const Icon(Icons.auto_awesome),
        label: Text(_isAnalyzing ? 'جاري التحليل...' : 'تحليل بالذكاء'),
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
            const Text('خطأ في التحميل'),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _loadImprovements,
              icon: const Icon(Icons.refresh),
              label: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      );
    }

    if (_improvements.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.auto_awesome, size: 80, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(
              'لا توجد اقتراحات حالياً',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              'اضغط على "تحليل بالذكاء" للحصول على اقتراحات',
              style: TextStyle(color: Colors.grey.shade600),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadImprovements,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _improvements.length,
        itemBuilder: (context, index) {
          final improvement = _improvements[index];
          final color = _getTypeColor(improvement['type']);
          final icon = _getTypeIcon(improvement['type']);

          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: color.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Icon(icon, color: color),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              improvement['title'] ?? 'اقتراح',
                              style: Theme.of(context).textTheme.titleMedium
                                  ?.copyWith(fontWeight: FontWeight.bold),
                            ),
                            Text(
                              improvement['type'] ?? '',
                              style: TextStyle(color: color, fontSize: 12),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    improvement['description'] ?? '',
                    style: TextStyle(color: Colors.grey.shade700),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      TextButton(onPressed: () {}, child: const Text('تجاهل')),
                      const SizedBox(width: 8),
                      ElevatedButton(
                        onPressed: () {},
                        child: const Text('تطبيق'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
