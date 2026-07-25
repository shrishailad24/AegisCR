import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:aaroha_app/core/constants.dart';

class DocumentHubScreen extends StatefulWidget {
  final String userId;
  const DocumentHubScreen({super.key, required this.userId});

  @override
  State<DocumentHubScreen> createState() => _DocumentHubScreenState();
}

class _DocumentHubScreenState extends State<DocumentHubScreen> {
  final Map<String, List<String>> _categorizedFiles = {
    'resumes': [],
    'certificates': [],
    'offer_letters': [],
  };
  List<dynamic> _expiryReminders = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadAllDocuments();
  }

  void _loadAllDocuments() {
    _fetchExpiryReminders();
    for (String category in _categorizedFiles.keys) {
      _fetchCategoryFiles(category);
    }
  }

  Future<void> _fetchExpiryReminders() async {
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/check-expiries/${widget.userId}'),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _expiryReminders = data['reminders'] ?? [];
        });
      }
    } catch (e) {
      debugPrint("Error fetching reminders: $e");
    }
  }

  Future<void> _fetchCategoryFiles(String category) async {
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/list-docs/${widget.userId}/$category'),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List<String> allFiles = List<String>.from(data['files']);
        final visibleFiles = allFiles
            .where((file) => !file.endsWith('_meta.json'))
            .toList();

        setState(() {
          _categorizedFiles[category] = visibleFiles;
        });
      }
    } catch (e) {
      debugPrint("Error fetching $category: $e");
    }
  }

  Future<void> _viewDocument(String category, String filename) async {
    final String baseUrl = AppConstants.baseUrl;
    final String urlPath =
        '$baseUrl/view-doc/${widget.userId}/$category/$filename';
    final Uri url = Uri.parse(urlPath);

    try {
      if (await canLaunchUrl(url)) {
        await launchUrl(url, mode: LaunchMode.externalApplication);
      } else {
        throw 'Could not open streaming pipeline for $urlPath';
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to open document: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _uploadWithAI() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'doc', 'docx', 'txt', 'jpg', 'png'],
    );

    if (result == null) return;

    setState(() {
      _isLoading = true;
    });
    final String baseUrl = AppConstants.baseUrl;

    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/upload-smart-doc'),
      );
      if (kIsWeb) {
        request.files.add(
          http.MultipartFile.fromBytes(
            'file',
            result.files.first.bytes!,
            filename: result.files.first.name,
          ),
        );
      } else {
        request.files.add(
          await http.MultipartFile.fromPath('file', result.files.first.path!),
        );
      }

      request.fields['user_id'] = widget.userId;
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final resultData = jsonDecode(response.body);
        final analysis = resultData['analysis'];

        if (mounted) {
          _showAIFeedbackDialog(
            analysis['category'] ?? 'resumes',
            analysis['owner'] ?? 'Unknown',
            analysis['expiry_date'],
            analysis['summary'] ?? 'Processed successfully.',
          );
        }
        _loadAllDocuments();
      } else {
        throw Exception('AI classification loop failed.');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('AI Processing Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  void _showAIFeedbackDialog(
    String cat,
    String owner,
    String? expiry,
    String summary,
  ) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.psychology, color: Colors.purple),
            SizedBox(width: 8),
            Text('AI Organizer Results'),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '📁 Auto-Category: ',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Text(cat.toUpperCase()),
              const SizedBox(height: 8),
              const Text(
                '👤 Detected Owner: ',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Text(owner),
              const SizedBox(height: 8),
              const Text(
                '📅 Expiration Date: ',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Text(expiry ?? 'None detected'),
              const SizedBox(height: 8),
              const Text(
                '📝 AI Summary: ',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Text(summary),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Awesome'),
          ),
        ],
      ),
    );
  }

  Future<void> _pickAndUploadManual(String category) async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'doc', 'docx', 'jpg', 'png'],
    );

    if (result == null) return;

    setState(() {
      _isLoading = true;
    });
    final String baseUrl = AppConstants.baseUrl;

    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/upload-doc'),
      );
      if (kIsWeb) {
        request.files.add(
          http.MultipartFile.fromBytes(
            'file',
            result.files.first.bytes!,
            filename: result.files.first.name,
          ),
        );
      } else {
        request.files.add(
          await http.MultipartFile.fromPath('file', result.files.first.path!),
        );
      }

      request.fields['category'] = category;
      request.fields['user_id'] = widget.userId;

      var response = await request.send();
      if (response.statusCode == 200) {
        _loadAllDocuments();
      }
    } catch (e) {
      debugPrint("Manual upload structural failure: $e");
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Smart Document Hub'),
        backgroundColor: Colors.teal,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16.0),
              children: [
                Card(
                  color: Colors.purple.shade50,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: BorderSide(color: Colors.purple.shade200, width: 1.5),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      children: [
                        const Text(
                          "✨ AI Document Organizer",
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.purple,
                          ),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          "Upload any file. The AI system will automatically detect its category and file it.",
                          textAlign: TextAlign.center,
                          style: TextStyle(fontSize: 13, color: Colors.black54),
                        ),
                        const SizedBox(height: 12),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            onPressed: _uploadWithAI,
                            icon: const Icon(Icons.auto_awesome),
                            label: const Text('Upload & Scan with AI'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.purple,
                              foregroundColor: Colors.white,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                if (_expiryReminders.isNotEmpty) ...[
                  const Text(
                    "📅 Expiration Reminders",
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.orange,
                    ),
                  ),
                  const SizedBox(height: 8),
                  ..._expiryReminders.map(
                    (reminder) => Card(
                      color: Colors.orange.shade50,
                      margin: const EdgeInsets.only(bottom: 8.0),
                      child: ListTile(
                        leading: const Icon(
                          Icons.warning_amber_rounded,
                          color: Colors.orange,
                          size: 28,
                        ),
                        title: Text(
                          reminder['filename'],
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Text("Expires: ${reminder['expiry_date']}"),
                        trailing: IconButton(
                          icon: const Icon(
                            Icons.visibility,
                            color: Colors.teal,
                          ),
                          onPressed: () => _viewDocument(
                            reminder['category'],
                            reminder['filename'],
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                _buildCategoryCard('Resumes', 'resumes', Icons.description),
                _buildCategoryCard(
                  'Certificates',
                  'certificates',
                  Icons.verified,
                ),
                _buildCategoryCard(
                  'Offer Letters',
                  'offer_letters',
                  Icons.mail,
                ),
              ],
            ),
    );
  }

  Widget _buildCategoryCard(String title, String key, IconData icon) {
    final List<String> files = _categorizedFiles[key] ?? [];
    return Card(
      margin: const EdgeInsets.only(bottom: 16.0),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ExpansionTile(
        leading: Icon(icon, color: Colors.teal, size: 30),
        title: Text(
          title,
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        subtitle: Text('${files.length} files saved'),
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: 16.0,
              vertical: 8.0,
            ),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _pickAndUploadManual(key),
                icon: const Icon(Icons.upload_file),
                label: Text('Manual Upload to $title'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.teal,
                  foregroundColor: Colors.white,
                ),
              ),
            ),
          ),
          if (files.isEmpty)
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: Text(
                'No documents added yet.',
                style: TextStyle(color: Colors.grey),
              ),
            ),
          ...files.map(
            (filename) => ListTile(
              leading: const Icon(Icons.insert_drive_file, color: Colors.grey),
              title: Text(filename, style: const TextStyle(fontSize: 14)),
              trailing: IconButton(
                icon: const Icon(
                  Icons.open_in_new,
                  color: Colors.teal,
                  size: 20,
                ),
                onPressed: () => _viewDocument(key, filename),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
