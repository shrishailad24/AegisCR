import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:aaroha_app/core/constants.dart';

class ResumeBuilderScreen extends StatefulWidget {
  final String userId;
  const ResumeBuilderScreen({super.key, required this.userId});

  @override
  State<ResumeBuilderScreen> createState() => _ResumeBuilderScreenState();
}

class _ResumeBuilderScreenState extends State<ResumeBuilderScreen> {
  final TextEditingController _jdController = TextEditingController();
  final TextEditingController _companyController = TextEditingController();
  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _versionNameController = TextEditingController();

  bool _isAnalyzing = false;
  bool _isGeneratingLetter = false;

  int? _atsScore;
  List<dynamic> _missingKeywords = [];
  List<dynamic> _improvements = [];
  String _generatedCoverLetter = "";
  Map<String, dynamic> _savedVersions = {};

  @override
  void initState() {
    super.initState();
    _loadResumeVersions();
  }

  Future<void> _loadResumeVersions() async {
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/list-resume-versions/${widget.userId}'),
      );
      if (response.statusCode == 200) {
        setState(() {
          _savedVersions = jsonDecode(response.body);
        });
      }
    } catch (e) {
      debugPrint("Error loading versions: $e");
    }
  }

  Future<void> _runATSCheck() async {
    if (_jdController.text.trim().isEmpty) return;
    setState(() {
      _isAnalyzing = true;
    });

    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/analyze-ats'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "job_description": _jdController.text.trim(),
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _atsScore = data['ats_score'];
          _missingKeywords = data['missing_keywords'] ?? [];
          _improvements = data['improvements'] ?? [];
        });
      }
    } catch (e) {
      debugPrint("ATS check failed: $e");
    } finally {
      if (mounted)
        setState(() {
          _isAnalyzing = false;
        });
    }
  }

  Future<void> _createCoverLetter() async {
    if (_jdController.text.trim().isEmpty ||
        _companyController.text.isEmpty ||
        _titleController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Please enter Company, Title, and Job Description first!',
          ),
        ),
      );
      return;
    }
    setState(() {
      _isGeneratingLetter = true;
    });

    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/generate-cover-letter'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "company_name": _companyController.text.trim(),
          "job_title": _titleController.text.trim(),
          "job_description": _jdController.text.trim(),
        }),
      );

      if (response.statusCode == 200) {
        setState(() {
          _generatedCoverLetter =
              jsonDecode(response.body)['cover_letter'] ?? "";
        });
      }
    } catch (e) {
      debugPrint("Cover Letter optimization failed: $e");
    } finally {
      if (mounted)
        setState(() {
          _isGeneratingLetter = false;
        });
    }
  }

  Future<void> _saveVariant(String name) async {
    if (name.trim().isEmpty) return;
    final String baseUrl = AppConstants.baseUrl;

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/save-resume-version'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "version_name": name.trim(),
          "resume_data": {
            "target_role": _titleController.text,
            "target_company": _companyController.text,
            "associated_score": _atsScore ?? 0,
            "optimized_on": DateTime.now().toIso8601String(),
          },
        }),
      );

      if (response.statusCode == 200) {
        _versionNameController.clear();
        _loadResumeVersions();
        if (mounted) Navigator.pop(context);
      }
    } catch (e) {
      debugPrint("Failed saving custom profile matrix: $e");
    }
  }

  void _showSaveVariantDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          'Save Variant Configuration',
          style: TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        content: TextField(
          controller: _versionNameController,
          style: const TextStyle(color: Colors.white),
          decoration: const InputDecoration(
            hintText: 'e.g., Senior Dev - Google Variant',
            hintStyle: TextStyle(color: Colors.white38),
            enabledBorder: UnderlineInputBorder(
              borderSide: BorderSide(color: Colors.white24),
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => _saveVariant(_versionNameController.text),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.indigo),
            child: const Text('Commit', style: TextStyle(color: Colors.white)),
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
        title: const Text(
          'AI Resume Optimizer',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF1E293B),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20.0),
        children: [
          Card(
            color: const Color(0xFF1E293B),
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(15),
            ),
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '🎯 JOB CONTEXT ENGINE',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: Colors.indigoAccent,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _companyController,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      labelText: 'Company Name',
                      labelStyle: const TextStyle(color: Colors.white60),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: Colors.white12),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(
                          color: Colors.indigoAccent,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _titleController,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      labelText: 'Job Title',
                      labelStyle: const TextStyle(color: Colors.white60),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: Colors.white12),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(
                          color: Colors.indigoAccent,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _jdController,
                    maxLines: 5,
                    style: const TextStyle(color: Colors.white, fontSize: 14),
                    decoration: InputDecoration(
                      labelText: 'Paste Job Description',
                      labelStyle: const TextStyle(color: Colors.white60),
                      alignLabelWithHint: true,
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(color: Colors.white12),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(
                          color: Colors.indigoAccent,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton(
                          onPressed: _isAnalyzing ? null : _runATSCheck,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.indigo,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                          ),
                          child: Text(
                            _isAnalyzing ? 'Scanning...' : 'ATS Check',
                            style: const TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: _isGeneratingLetter
                              ? null
                              : _createCoverLetter,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.deepPurple,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                          ),
                          child: Text(
                            _isGeneratingLetter ? 'Writing...' : 'Cover Letter',
                            style: const TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          if (_atsScore != null) ...[
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(15),
              ),
              child: Column(
                children: [
                  const Text(
                    'ATS ALIGNMENT METRIC',
                    style: TextStyle(
                      color: Colors.white60,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '$_atsScore%',
                    style: TextStyle(
                      color: _atsScore! >= 75
                          ? Colors.greenAccent
                          : Colors.amberAccent,
                      fontSize: 36,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: 12),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(10),
                    child: LinearProgressIndicator(
                      value: _atsScore! / 100,
                      minHeight: 8,
                      color: _atsScore! >= 75
                          ? Colors.greenAccent
                          : Colors.amberAccent,
                      backgroundColor: Colors.white10,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            if (_missingKeywords.isNotEmpty) ...[
              const Text(
                '⚠️ MISSING KEYWORDS',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: Colors.redAccent,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: _missingKeywords
                    .map(
                      (tag) => Chip(
                        label: Text(
                          tag.toString(),
                          style: const TextStyle(
                            fontSize: 11,
                            color: Colors.redAccent,
                          ),
                        ),
                        backgroundColor: Colors.red.withOpacity(0.1),
                        side: const BorderSide(color: Colors.redAccent),
                        visualDensity: VisualDensity.compact,
                      ),
                    )
                    .toList(),
              ),
              const SizedBox(height: 20),
            ],
            if (_improvements.isNotEmpty) ...[
              const Text(
                '💡 ENHANCEMENTS',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: Colors.indigoAccent,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 8),
              ..._improvements.map(
                (tip) => Padding(
                  padding: const EdgeInsets.only(bottom: 8.0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(
                        Icons.check_circle,
                        color: Colors.indigoAccent,
                        size: 16,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          tip.toString(),
                          style: const TextStyle(
                            fontSize: 13,
                            color: Colors.white70,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _showSaveVariantDialog,
                  icon: const Icon(Icons.bookmark, size: 18),
                  label: const Text('Save Variant'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.teal,
                    foregroundColor: Colors.white,
                  ),
                ),
              ),
              const SizedBox(height: 24),
            ],
          ],

          if (_generatedCoverLetter.isNotEmpty) ...[
            const Text(
              '📄 COVER LETTER DRAFT',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Colors.deepPurpleAccent,
                letterSpacing: 1.2,
              ),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(15),
                border: Border.all(
                  color: Colors.deepPurpleAccent.withOpacity(0.2),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _generatedCoverLetter,
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 13,
                      height: 1.5,
                    ),
                  ),
                  const Divider(color: Colors.white12, height: 24),
                  Align(
                    alignment: Alignment.centerRight,
                    child: TextButton.icon(
                      onPressed: () {
                        Clipboard.setData(
                          ClipboardData(text: _generatedCoverLetter),
                        );
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Copied!')),
                        );
                      },
                      icon: const Icon(Icons.copy, size: 18),
                      label: const Text('Copy Text'),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
          ],

          if (_savedVersions.isNotEmpty) ...[
            const Text(
              '📂 TAILORED VARIANTS VAULT',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Colors.white60,
                letterSpacing: 1.2,
              ),
            ),
            const SizedBox(height: 8),
            ..._savedVersions.entries.map(
              (item) => Card(
                color: const Color(0xFF1E293B),
                child: ListTile(
                  leading: const Icon(
                    Icons.history_edu,
                    color: Colors.indigoAccent,
                  ),
                  title: Text(
                    item.key,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      fontSize: 14,
                    ),
                  ),
                  subtitle: Text(
                    "${item.value['target_role']} @ ${item.value['target_company']}\nScore: ${item.value['associated_score']}%",
                    style: const TextStyle(color: Colors.white60, fontSize: 11),
                  ),
                  isThreeLine: true,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
