import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:aaroha_app/core/constants.dart';

class SkillGapScreen extends StatefulWidget {
  final String userId;
  const SkillGapScreen({super.key, required this.userId});

  @override
  State<SkillGapScreen> createState() => _SkillGapScreenState();
}

class _SkillGapScreenState extends State<SkillGapScreen> {
  final TextEditingController _jobController = TextEditingController(
    text: "Senior Data Scientist",
  );
  bool _isLoading = false;

  List<dynamic> _missingSkills = [];
  List<dynamic> _recommendedCourses = [];
  List<dynamic> _recommendedProjects = [];
  String _estimatedTime = "";
  bool _hasSearched = false;

  Future<void> _checkSkillGap() async {
    if (_jobController.text.trim().isEmpty) return;
    setState(() {
      _isLoading = true;
    });

    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/career/skill-gap'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "dream_job": _jobController.text.trim(),
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _missingSkills = data['missing_skills'] ?? [];
          _recommendedCourses = data['recommended_courses'] ?? [];
          _recommendedProjects = data['recommended_projects'] ?? [];
          _estimatedTime = data['estimated_time'] ?? "";
          _hasSearched = true;
        });
      }
    } catch (e) {
      debugPrint("Skill Gap failed: $e");
    } finally {
      if (mounted)
        setState(() {
          _isLoading = false;
        });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "Skill Gap Analysis",
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
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(15),
              ),
              child: Column(
                children: [
                  TextField(
                    controller: _jobController,
                    style: const TextStyle(color: Colors.white),
                    decoration: const InputDecoration(
                      labelText: "Dream Job Role",
                      labelStyle: TextStyle(color: Colors.purpleAccent),
                      hintText: "e.g., Senior Data Scientist",
                      hintStyle: TextStyle(color: Colors.white30),
                      border: OutlineInputBorder(),
                      enabledBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.white24),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: ElevatedButton.icon(
                      onPressed: _isLoading ? null : _checkSkillGap,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.purpleAccent,
                      ),
                      icon: const Icon(Icons.psychology, color: Colors.white),
                      label: Text(
                        _isLoading ? "Analyzing..." : "Analyze Skill Gaps",
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            if (_isLoading)
              const Center(
                child: CircularProgressIndicator(color: Colors.purpleAccent),
              )
            else if (_hasSearched) ...[
              if (_estimatedTime.isNotEmpty) ...[
                Card(
                  color: const Color(0xFF1E1B4B),
                  child: ListTile(
                    leading: const Icon(
                      Icons.hourglass_empty,
                      color: Colors.amberAccent,
                    ),
                    title: const Text(
                      "Learning Timeline",
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                    subtitle: Text(
                      _estimatedTime,
                      style: const TextStyle(
                        color: Colors.amberAccent,
                        fontSize: 13,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 20),
              ],

              const Text(
                "⚠️ MISSING TECH SKILLS",
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 8),
              if (_missingSkills.isEmpty)
                const Text(
                  "No missing skills! You match perfectly.",
                  style: TextStyle(color: Colors.greenAccent),
                )
              else
                Wrap(
                  spacing: 8,
                  runSpacing: 4,
                  children: _missingSkills
                      .map(
                        (s) => Chip(
                          label: Text(
                            s.toString(),
                            style: const TextStyle(
                              color: Colors.redAccent,
                              fontSize: 12,
                            ),
                          ),
                          backgroundColor: Colors.red.withOpacity(0.1),
                          side: const BorderSide(color: Colors.redAccent),
                        ),
                      )
                      .toList(),
                ),
              const SizedBox(height: 24),

              const Text(
                "📚 RECOMMENDED COURSES",
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 8),
              ..._recommendedCourses.map(
                (course) => Card(
                  color: const Color(0xFF1E293B),
                  child: ListTile(
                    leading: const Icon(Icons.school, color: Colors.tealAccent),
                    title: Text(
                      course.toString(),
                      style: const TextStyle(color: Colors.white, fontSize: 14),
                    ),
                    trailing: const Icon(
                      Icons.arrow_forward,
                      color: Colors.white30,
                      size: 16,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 24),

              const Text(
                "🛠️ PORTFOLIO PROJECTS",
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 8),
              ..._recommendedProjects.map(
                (project) => Card(
                  color: const Color(0xFF1E293B),
                  child: ListTile(
                    leading: const Icon(
                      Icons.build,
                      color: Colors.purpleAccent,
                    ),
                    title: Text(
                      project.toString(),
                      style: const TextStyle(color: Colors.white, fontSize: 14),
                    ),
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
