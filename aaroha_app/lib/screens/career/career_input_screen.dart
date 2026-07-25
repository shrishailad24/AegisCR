import 'dart:convert';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:aaroha_app/core/constants.dart';
import 'package:aaroha_app/screens/career/vault_viewer_screen.dart';

class CareerInputScreen extends StatefulWidget {
  const CareerInputScreen({super.key});

  @override
  State<CareerInputScreen> createState() => _CareerInputScreenState();
}

class _CareerInputScreenState extends State<CareerInputScreen> {
  final TextEditingController _skillsController = TextEditingController();
  final TextEditingController _salaryController = TextEditingController();
  bool _isRemote = true;
  bool _isLoading = false;

  final String _baseUrl = AppConstants.baseUrl;

  Future<void> _analyzeCareerProfile() async {
    if (_salaryController.text.isEmpty || _skillsController.text.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Please fill all fields")));
      return;
    }
    setState(() => _isLoading = true);
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/analyze-scenario'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": "test_user",
          "salary": int.tryParse(_salaryController.text) ?? 0,
          "skills": _skillsController.text,
          "is_remote": _isRemote,
        }),
      );
      if (!mounted) return;
      if (response.statusCode == 200) {
        var data = jsonDecode(response.body);
        _showResultDialog(data['decision']);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text("Error: $e")));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _pickAndUploadFile() async {
    setState(() => _isLoading = true);
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf', 'doc', 'docx'],
      );

      if (result == null) {
        if (mounted) setState(() => _isLoading = false);
        return;
      }

      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$_baseUrl/upload-doc'),
      );

      if (result.files.single.bytes != null) {
        // Web / certain conditions
        request.files.add(
          http.MultipartFile.fromBytes(
            'file',
            result.files.single.bytes!,
            filename: result.files.single.name,
          ),
        );
      } else if (result.files.single.path != null) {
        // Mobile
        request.files.add(
          await http.MultipartFile.fromPath('file', result.files.single.path!),
        );
      } else {
        throw Exception("Could not get file data");
      }

      request.fields['user_id'] = "test_user";
      request.fields['category'] = "resumes";

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (!mounted) return;
      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("File Uploaded!"),
            backgroundColor: Colors.green,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Upload Failed: ${response.statusCode}"),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Error: $e"), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _showResultDialog(String decision) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "AI Analysis Result",
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        content: SingleChildScrollView(
          child: Text(decision, style: const TextStyle(color: Colors.white70)),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("OK"),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "Career Brain",
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(
              controller: _skillsController,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(
                labelText: "Skills",
                labelStyle: TextStyle(color: Colors.white60),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _salaryController,
              style: const TextStyle(color: Colors.white),
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: "Expected Salary",
                labelStyle: TextStyle(color: Colors.white60),
              ),
            ),
            const SizedBox(height: 12),
            SwitchListTile(
              title: const Text(
                "Remote Option?",
                style: TextStyle(color: Colors.white),
              ),
              value: _isRemote,
              onChanged: (val) => setState(() => _isRemote = val),
              activeColor: Colors.purpleAccent,
            ),
            const SizedBox(height: 30),
            if (_isLoading)
              const CircularProgressIndicator(color: Colors.purpleAccent)
            else ...[
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _pickAndUploadFile,
                  icon: const Icon(Icons.upload_file),
                  label: const Text("Upload Resume"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blueAccent,
                    foregroundColor: Colors.white,
                  ),
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _analyzeCareerProfile,
                  icon: const Icon(Icons.psychology),
                  label: const Text("Analyze Scenario"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.purpleAccent,
                    foregroundColor: Colors.white,
                  ),
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const VaultViewerScreen(),
                    ),
                  ),
                  icon: const Icon(Icons.folder_open),
                  label: const Text("View Vault"),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.white,
                    side: const BorderSide(color: Colors.white24),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
