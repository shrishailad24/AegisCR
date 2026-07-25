import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:aaroha_app/core/constants.dart';
import 'package:aaroha_app/screens/education/learning_twin_screen.dart';
import 'package:aaroha_app/screens/education/study_planner_screen.dart';
import 'package:aaroha_app/screens/education/notes_tutor_screen.dart';
import 'package:aaroha_app/screens/education/quiz_game_screen.dart';
import 'package:aaroha_app/screens/education/study_circle_screen.dart';
import 'package:aaroha_app/screens/education/focus_mode_screen.dart';
import 'package:aaroha_app/screens/education/learning_hub_screen.dart';

class EducationPortalScreen extends StatefulWidget {
  final String userId;
  const EducationPortalScreen({super.key, required this.userId});

  @override
  State<EducationPortalScreen> createState() => _EducationPortalScreenState();
}

class _EducationPortalScreenState extends State<EducationPortalScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  // Student Profile Genome State
  final _branchC = TextEditingController(text: "Computer Science");
  final _semC = TextEditingController(text: "Semester 5");
  final _subjectsC = TextEditingController(
    text: "Data Structures, Database Management, Computer Networks",
  );
  final _goalsC = TextEditingController(text: "Master DSA, Ace Semester Exams");
  String _learningStyle = "Interactive"; // Visual | Text | Interactive

  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadStudentProfile();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  // API Call: Get Student Profile
  Future<void> _loadStudentProfile() async {
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/education/student-profile/${widget.userId}'),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data.containsKey("course_branch")) {
          setState(() {
            _branchC.text = data["course_branch"] ?? "";
            _semC.text = data["semester"] ?? "";
            _subjectsC.text = (data["subjects"] as List).join(", ");
            _goalsC.text = (data["goals"] as List).join(", ");
            _learningStyle = data["learning_style"] ?? "Interactive";
          });
        }
      }
    } catch (e) {
      debugPrint("Load Student profile failed: $e");
    }
  }

  // API Call: Save Student Profile
  Future<void> _saveStudentProfile() async {
    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      List<String> splitList(String text) => text
          .split(',')
          .map((e) => e.trim())
          .where((e) => e.isNotEmpty)
          .toList();
      final response = await http.post(
        Uri.parse('$baseUrl/education/student-profile'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "course_branch": _branchC.text,
          "semester": _semC.text,
          "subjects": splitList(_subjectsC.text),
          "goals": splitList(_goalsC.text),
          "learning_style": _learningStyle,
        }),
      );
      if (response.statusCode == 200) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text("Student Profile Saved!")),
          );
        }
      }
    } catch (e) {
      debugPrint("Save student profile failed: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "Education Brain Matrix",
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.blueAccent,
          unselectedLabelColor: Colors.white60,
          indicatorColor: Colors.blueAccent,
          tabs: const [
            Tab(icon: Icon(Icons.analytics), text: "Analytics & Tools"),
            Tab(icon: Icon(Icons.person), text: "Profile Genome"),
          ],
        ),
      ),
      body: SafeArea(
        child: Stack(
          children: [
            TabBarView(
              controller: _tabController,
              children: [_buildAnalyticsToolsTab(), _buildProfileGenomeTab()],
            ),
            if (_isLoading)
              const Positioned(
                top: 0,
                left: 0,
                right: 0,
                child: LinearProgressIndicator(
                  color: Colors.blueAccent,
                  backgroundColor: Colors.transparent,
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalyticsToolsTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Progress Dashboard Summary
          const Text(
            "ACADEMIC PROGRESS ENGINE",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF1E1B4B), Color(0xFF0F172A)],
              ),
              borderRadius: BorderRadius.circular(15),
              border: Border.all(color: Colors.blueAccent.withOpacity(0.2)),
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          "Syllabus Completion",
                          style: TextStyle(color: Colors.white70, fontSize: 14),
                        ),
                        SizedBox(height: 6),
                        Text(
                          "72 % Completed",
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    CircularProgressIndicator(
                      value: 0.72,
                      backgroundColor: Colors.white10,
                      valueColor: const AlwaysStoppedAnimation<Color>(
                        Colors.blueAccent,
                      ),
                      strokeWidth: 8,
                    ),
                  ],
                ),
                const Divider(color: Colors.white10, height: 24),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      "Study Streak: 8 Days 🔥",
                      style: TextStyle(
                        color: Colors.orange,
                        fontSize: 13,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      "Total study hours: 32.5h",
                      style: TextStyle(color: Colors.white70, fontSize: 13),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // 2. AI Learning Twin Proactive Suggestion
          const Text(
            "AI LEARNING TWIN PREDICTIONS",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(15),
              border: Border.all(color: Colors.blueAccent.withOpacity(0.2)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.psychology, color: Colors.blueAccent),
                    SizedBox(width: 8),
                    Text(
                      "Adaptive Suggestion",
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                const Text(
                  "\"Shash, your test performance suggests you are struggling with Computer Networks routing algorithms. Let's practice some network routing mock MCQs today, and focus on visual network animations!\"",
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 13,
                    height: 1.4,
                    fontStyle: FontStyle.italic,
                  ),
                ),
                const SizedBox(height: 12),
                Align(
                  alignment: Alignment.centerRight,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) =>
                              LearningTwinScreen(userId: widget.userId),
                        ),
                      );
                    },
                    icon: const Icon(Icons.forum, size: 16),
                    label: const Text("Chat with Twin"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.indigo,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 28),

          // 3. Cognitive Tools Matrix
          const Text(
            "COGNITIVE EDUCATION BRAIN TOOLS",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),
          LayoutBuilder(
            builder: (context, constraints) {
              int crossAxisCount = constraints.maxWidth > 600 ? 3 : 2;
              return GridView.count(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisCount: crossAxisCount,
                childAspectRatio: 1.2,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                children: [
                  _buildToolCard(
                    "AI Study Planner",
                    "Exam Strategy & Timetable",
                    Icons.calendar_month,
                    Colors.blueAccent,
                    () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) =>
                            StudyPlannerScreen(userId: widget.userId),
                      ),
                    ),
                  ),
                  _buildToolCard(
                    "AI Tutor & Notes",
                    "Lecture notes, citations, doubts",
                    Icons.menu_book,
                    Colors.purpleAccent,
                    () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) =>
                            NotesTutorScreen(userId: widget.userId),
                      ),
                    ),
                  ),
                  _buildToolCard(
                    "Quiz & Quests",
                    "Mock exams, diagnostic weak topics",
                    Icons.sports_esports,
                    Colors.tealAccent,
                    () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) =>
                            QuizGameScreen(userId: widget.userId),
                      ),
                    ),
                  ),
                  _buildToolCard(
                    "Study Circles",
                    "Collaborative team leaderboard",
                    Icons.groups,
                    Colors.amberAccent,
                    () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) =>
                            StudyCircleScreen(userId: widget.userId),
                      ),
                    ),
                  ),
                  _buildToolCard(
                    "Pomodoro Focus",
                    "Interval timer & ambient audio",
                    Icons.timer,
                    Colors.redAccent,
                    () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) =>
                            FocusModeScreen(userId: widget.userId),
                      ),
                    ),
                  ),
                  _buildToolCard(
                    "Learning Hub",
                    "Customized roadmap, books, videos",
                    Icons.school_outlined,
                    Colors.cyanAccent,
                    () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) =>
                            LearningHubScreen(userId: widget.userId),
                      ),
                    ),
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildProfileGenomeTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "STUDENT PROFILE GENOME",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _branchC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Course & Branch",
              labelStyle: TextStyle(color: Colors.white60),
            ),
          ),
          TextField(
            controller: _semC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Current Semester",
              labelStyle: TextStyle(color: Colors.white60),
            ),
          ),
          TextField(
            controller: _subjectsC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Subjects (comma separated)",
              labelStyle: TextStyle(color: Colors.white60),
            ),
          ),
          TextField(
            controller: _goalsC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Learning Goals (comma separated)",
              labelStyle: TextStyle(color: Colors.white60),
            ),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            value: _learningStyle,
            dropdownColor: const Color(0xFF1E293B),
            decoration: const InputDecoration(
              labelText: "Learning Style",
              labelStyle: TextStyle(color: Colors.white60),
            ),
            items: ["Visual", "Text", "Interactive"]
                .map(
                  (s) => DropdownMenuItem(
                    value: s,
                    child: Text(s, style: const TextStyle(color: Colors.white)),
                  ),
                )
                .toList(),
            onChanged: (val) => setState(() => _learningStyle = val!),
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _saveStudentProfile,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blueAccent,
              ),
              child: const Text(
                "Commit Profile Genome",
                style: TextStyle(color: Colors.white),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildToolCard(
    String title,
    String subtitle,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(15),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(15),
          border: Border.all(color: Colors.white.withOpacity(0.05)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: color, size: 20),
            ),
            const Spacer(),
            Text(
              title,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 13,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              subtitle,
              style: const TextStyle(color: Colors.white38, fontSize: 9),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}
