import 'package:flutter/material.dart';
import 'package:frontend/models/answer_model.dart';
import 'package:frontend/services/api_service.dart';

class ReviewScreen extends StatefulWidget {
  final int questionnaireId;

  const ReviewScreen({super.key, required this.questionnaireId});

  @override
  State<ReviewScreen> createState() => _ReviewScreenState();
}

class _ReviewScreenState extends State<ReviewScreen> {
  List<AnswerModel> _answers = [];
  bool _isLoading = true;
  String? _error;

  // Track which answers are being saved
  final Map<int, bool> _savingMap = {};
  // Controllers for edit fields
  final Map<int, TextEditingController> _editControllers = {};

  @override
  void initState() {
    super.initState();
    _loadAnswers();
  }

  Future<void> _loadAnswers() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final data = await ApiService.getReviewAnswers(widget.questionnaireId);
      final items = (data['items'] as List)
          .map((item) => AnswerModel.fromJson(item))
          .toList();
      setState(() => _answers = items);

      // Initialize controllers
      for (final ans in _answers) {
        _editControllers[ans.answerId] = TextEditingController(
          text: ans.editedAnswer ?? ans.generatedAnswer,
        );
      }
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _saveAnswer(AnswerModel answer) async {
    final controller = _editControllers[answer.answerId];
    if (controller == null) return;

    setState(() => _savingMap[answer.answerId] = true);
    try {
      await ApiService.editAnswer(answer.answerId, controller.text);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Answer ${answer.questionNumber} saved')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Error: ${e.toString().replaceFirst("Exception: ", "")}',
            ),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _savingMap[answer.answerId] = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Review — Questionnaire ${widget.questionnaireId}'),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return Center(
        child: Text(
          'Error: $_error',
          style: const TextStyle(color: Colors.red),
        ),
      );
    }
    if (_answers.isEmpty) {
      return const Center(child: Text('No answers found.'));
    }

    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: _answers.length,
      separatorBuilder: (context, index) => const Divider(height: 32),
      itemBuilder: (context, index) {
        final answer = _answers[index];
        final isSaving = _savingMap[answer.answerId] ?? false;
        String cleanQuestion = answer.question.replaceFirst(
          RegExp(r'^\d+[\.\)\s]\s*'),
          '',
        );

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Question header
            Text(
              'Q${answer.questionNumber}. $cleanQuestion',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),

            // Generated answer (read-only)
            Text(
              'Generated Answer:',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 4),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(answer.generatedAnswer),
            ),
            const SizedBox(height: 12),

            // Editable answer field
            Text(
              'Your Answer:',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 4),
            TextField(
              controller: _editControllers[answer.answerId],
              maxLines: 4,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Edit your answer here...',
              ),
            ),
            const SizedBox(height: 8),

            // Save button
            Align(
              alignment: Alignment.centerRight,
              child: ElevatedButton.icon(
                onPressed: isSaving ? null : () => _saveAnswer(answer),
                icon: isSaving
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.save, size: 18),
                label: const Text('Save'),
              ),
            ),
          ],
        );
      },
    );
  }

  @override
  void dispose() {
    for (final controller in _editControllers.values) {
      controller.dispose();
    }
    super.dispose();
  }
}
