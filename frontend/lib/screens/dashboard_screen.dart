import 'package:flutter/material.dart';
import 'package:frontend/services/api_service.dart';
import 'package:frontend/widgets/primary_button.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  bool _isLoading = false;
  String _loadingAction = '';

  void _showSnackBar(String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  Future<void> _generateAnswers() async {
    final id = await ApiService.getQuestionnaireId();
    if (id == null) {
      _showSnackBar('No questionnaire uploaded yet. Please upload one first.');
      return;
    }

    setState(() {
      _isLoading = true;
      _loadingAction = 'generate';
    });
    try {
      final result = await ApiService.generateAnswers(id);
      _showSnackBar('Generated ${result['answers_generated']} answers');
    } catch (e) {
      _showSnackBar('Error: ${e.toString().replaceFirst("Exception: ", "")}');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _reviewAnswers() async {
    final id = await ApiService.getQuestionnaireId();
    if (id == null) {
      _showSnackBar('No questionnaire uploaded yet. Please upload one first.');
      return;
    }
    if (mounted) {
      Navigator.pushNamed(context, '/review', arguments: id);
    }
  }

  Future<void> _exportDocument() async {
    final id = await ApiService.getQuestionnaireId();
    if (id == null) {
      _showSnackBar('No questionnaire uploaded yet. Please upload one first.');
      return;
    }

    setState(() {
      _isLoading = true;
      _loadingAction = 'export';
    });
    try {
      final result = await ApiService.exportQuestionnaire(id);
      final exportFile = result['export_file'];
      final fullUrl = '${ApiService.baseUrl}/$exportFile';
      _showDialog(
        'Export Complete',
        'File saved!\n\nOpen in browser:\n$fullUrl',
      );
    } catch (e) {
      _showSnackBar('Error: ${e.toString().replaceFirst("Exception: ", "")}');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _logout() async {
    await ApiService.logout();
    if (mounted) {
      Navigator.pushReplacementNamed(context, '/login');
    }
  }

  void _showDialog(String title, String content) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(title),
        content: Text(content),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _logout,
            tooltip: 'Logout',
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Questionnaire AI',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            PrimaryButton(
              label: 'Upload Documents',
              icon: Icons.upload_file,
              onPressed: () => Navigator.pushNamed(context, '/upload'),
            ),

            const SizedBox(height: 12),
            PrimaryButton(
              label: 'Generate Answers',
              icon: Icons.auto_awesome,
              onPressed: _generateAnswers,
              isLoading: _isLoading && _loadingAction == 'generate',
            ),
            const SizedBox(height: 12),
            PrimaryButton(
              label: 'Review Answers',
              icon: Icons.rate_review,
              onPressed: _reviewAnswers,
            ),
            const SizedBox(height: 12),
            PrimaryButton(
              label: 'Export Document',
              icon: Icons.download,
              onPressed: _exportDocument,
              isLoading: _isLoading && _loadingAction == 'export',
            ),
          ],
        ),
      ),
    );
  }
}
