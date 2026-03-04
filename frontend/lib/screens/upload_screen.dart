import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:frontend/services/api_service.dart';
import 'package:frontend/widgets/primary_button.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  bool _isUploadingRef = false;
  bool _isUploadingQ = false;

  void _showSnackBar(String message, {int durationSeconds = 3}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: Duration(seconds: durationSeconds),
      ),
    );
  }

  Future<void> _uploadReference() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
      withData: true, // Required for web — loads bytes into memory
    );
    if (result == null || result.files.single.bytes == null) return;

    final fileBytes = result.files.single.bytes!;
    final fileName = result.files.single.name;

    setState(() => _isUploadingRef = true);
    _showSnackBar('Uploading and processing document...', durationSeconds: 60);

    try {
      final response = await ApiService.uploadReference(fileBytes, fileName);
      if (!mounted) return;
      ScaffoldMessenger.of(context).clearSnackBars();
      _showSnackBar(response['message'] ?? 'Document uploaded successfully');
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).clearSnackBars();
      _showSnackBar('Error: ${e.toString().replaceFirst("Exception: ", "")}');
    } finally {
      if (mounted) setState(() => _isUploadingRef = false);
    }
  }

  Future<void> _uploadQuestionnaire() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
      withData: true, // Required for web — loads bytes into memory
    );
    if (result == null || result.files.single.bytes == null) return;

    final fileBytes = result.files.single.bytes!;
    final fileName = result.files.single.name;

    setState(() => _isUploadingQ = true);
    try {
      final response = await ApiService.uploadQuestionnaire(
        fileBytes,
        fileName,
      );
      if (!mounted) return;
      _showSnackBar('Questionnaire uploaded: ${response['file_name']}');
    } catch (e) {
      if (!mounted) return;
      _showSnackBar('Error: ${e.toString().replaceFirst("Exception: ", "")}');
    } finally {
      if (mounted) setState(() => _isUploadingQ = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Upload Documents')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            PrimaryButton(
              label: 'Upload Reference Document',
              icon: Icons.description,
              onPressed: _uploadReference,
              isLoading: _isUploadingRef,
            ),
            const SizedBox(height: 24),
            PrimaryButton(
              label: 'Upload Questionnaire',
              icon: Icons.quiz,
              onPressed: _uploadQuestionnaire,
              isLoading: _isUploadingQ,
            ),
          ],
        ),
      ),
    );
  }
}
