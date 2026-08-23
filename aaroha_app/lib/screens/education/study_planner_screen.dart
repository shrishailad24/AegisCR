import 'package:aaroha_app/core/constants.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class StudyPlannerScreen extends StatefulWidget {
  final String userId;
  const StudyPlannerScreen({super.key, required this.userId});

  @override
  State<StudyPlannerScreen> createState() => _StudyPlannerScreenState();
}

class _StudyPlannerScreenState extends State<StudyPlannerScreen> {
  bool _isLoading = false;

  // Study Planner
  List<dynamic> _studySchedule = [];
  String _examCountdown = "30 Days";
  List<dynamic> _studyTips = [];
  int _plannerDays = 15;

  // Exam Strategy
  final TextEditingController _strategySubjectC = TextEditingController(
    text: "Computer Networks",
  );
  double _daysToExam = 7.0;
  Map<String, dynamic>? _examStrategy;

  // Smart Revision Mode
  final TextEditingController _revisionSubjectC = TextEditingController(
    text: "Database Systems",
  );
  Map<String, dynamic>? _revisionPlan;

  // API Call: AI Study Planner
  Future<void> _generateStudyPlan() async {
    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/education/study-planner'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "exam_countdown_days": _plannerDays,
        }),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _studySchedule = data["schedule"] ?? [];
          _examCountdown = data["countdown"] ?? "$_plannerDays Days";
          _studyTips = data["revision_plan"] ?? [];
        });
      }
    } catch (e) {
      debugPrint("Study planner failed: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  // API Call: Exam Strategy Generator
  Future<void> _generateExamStrategy() async {
    if (_strategySubjectC.text.trim().isEmpty) return;
    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/education/exam-strategy'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "subject": _strategySubjectC.text.trim(),
          "days_to_exam": _daysToExam.toInt(),
        }),
      );
      if (response.statusCode == 200) {
        setState(() {
          _examStrategy = jsonDecode(response.body);
        });
      }
    } catch (e) {
      debugPrint("Exam Strategy failed: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  // API Call: Smart Spaced Revision Planner
  Future<void> _generateSmartRevision() async {
    if (_revisionSubjectC.text.trim().isEmpty) return;
    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/education/smart-revision'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "subject": _revisionSubjectC.text.trim(),
        }),
      );
      if (response.statusCode == 200) {
        setState(() {
          _revisionPlan = jsonDecode(response.body);
        });
      }
    } catch (e) {
      debugPrint("Smart revision failed: $e");
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
          "Study Planner & Strategy",
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Stack(
        children: [
          ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // 1. AI TIMETABLE SECTION
              _buildSectionHeader(
                "1. AI DAILY STUDY TIMETABLE",
                Icons.calendar_month,
              ),
              const SizedBox(height: 12),
              _buildTimetableCard(),
              const SizedBox(height: 24),

              // 2. EXAM STRATEGY GENERATOR
              _buildSectionHeader(
                "2. EXAM STRATEGY ENGINE",
                Icons.rocket_launch,
              ),
              const SizedBox(height: 12),
              _buildStrategyGeneratorCard(),
              const SizedBox(height: 24),

              // 3. SMART REVISION MODE
              _buildSectionHeader("3. SMART SPACED REVISION", Icons.sync),
              const SizedBox(height: 12),
              _buildRevisionPlannerCard(),
            ],
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
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, color: Colors.blueAccent, size: 18),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 13,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.2,
          ),
        ),
      ],
    );
  }

  Widget _buildTimetableCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "Set Prep Duration:",
                style: TextStyle(color: Colors.white70, fontSize: 13),
              ),
              DropdownButton<int>(
                value: _plannerDays,
                dropdownColor: const Color(0xFF1E293B),
                style: const TextStyle(color: Colors.white),
                items: [7, 15, 30, 60]
                    .map(
                      (d) => DropdownMenuItem(value: d, child: Text("$d Days")),
                    )
                    .toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _plannerDays = val);
                },
              ),
            ],
          ),
          const SizedBox(height: 10),
          ElevatedButton.icon(
            onPressed: _generateStudyPlan,
            icon: const Icon(Icons.auto_awesome, size: 16),
            label: const Text("Generate Timetable"),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blueAccent,
              foregroundColor: Colors.white,
            ),
          ),
          if (_studySchedule.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text(
              "Active Prep Countdown: $_examCountdown",
              style: const TextStyle(
                color: Colors.amberAccent,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            ..._studySchedule.map(
              (item) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4.0),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: Colors.blueAccent.withValues(alpha: 0.1),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.check,
                        color: Colors.blueAccent,
                        size: 14,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "${item["day"]}: ${item["topic"]}",
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            "Allocate: ${item["hours"]} Hours",
                            style: const TextStyle(
                              color: Colors.white54,
                              fontSize: 11,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            if (_studyTips.isNotEmpty) ...[
              const Divider(color: Colors.white10, height: 24),
              const Text(
                "Proactive Study Tips",
                style: TextStyle(
                  color: Colors.amberAccent,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 6),
              ..._studyTips.map(
                (tip) => Text(
                  "• $tip",
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 12,
                    height: 1.4,
                  ),
                ),
              ),
            ],
          ],
        ],
      ),
    );
  }

  Widget _buildStrategyGeneratorCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          TextField(
            controller: _strategySubjectC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Target Subject Name",
              labelStyle: TextStyle(color: Colors.white60),
              enabledBorder: UnderlineInputBorder(
                borderSide: BorderSide(color: Colors.white24),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "Days to Exam: ${_daysToExam.toInt()}",
                style: const TextStyle(color: Colors.white70),
              ),
              Expanded(
                child: Slider(
                  value: _daysToExam,
                  min: 2,
                  max: 30,
                  divisions: 28,
                  label: _daysToExam.toInt().toString(),
                  onChanged: (val) => setState(() => _daysToExam = val),
                ),
              ),
            ],
          ),
          ElevatedButton.icon(
            onPressed: _generateExamStrategy,
            icon: const Icon(Icons.psychology, size: 16),
            label: const Text("Create Strategy Checklist"),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blueAccent,
              foregroundColor: Colors.white,
            ),
          ),
          if (_examStrategy != null) ...[
            const Divider(color: Colors.white10, height: 24),
            Text(
              "Strategy roadmap: ${_examStrategy!["subject"]}",
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              "Expected Weightage Focus:",
              style: TextStyle(
                color: Colors.amberAccent,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            ...(_examStrategy!["high_weightage_topics"] as List).map(
              (topic) => Text(
                "• $topic",
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                  height: 1.3,
                ),
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              "Prioritized Study Order:",
              style: TextStyle(
                color: Colors.blueAccent,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            ...(_examStrategy!["study_order"] as List).map(
              (topic) => Text(
                "• $topic",
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                  height: 1.3,
                ),
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              "Last-Day Checklist:",
              style: TextStyle(
                color: Colors.greenAccent,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            ...(_examStrategy!["last_day_checklist"] as List).map(
              (chk) => Text(
                "• $chk",
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                  height: 1.3,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildRevisionPlannerCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          TextField(
            controller: _revisionSubjectC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Focus Subject",
              labelStyle: TextStyle(color: Colors.white60),
              enabledBorder: UnderlineInputBorder(
                borderSide: BorderSide(color: Colors.white24),
              ),
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _generateSmartRevision,
            icon: const Icon(Icons.track_changes, size: 16),
            label: const Text("Launch Spaced Revision Mode"),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.teal,
              foregroundColor: Colors.white,
            ),
          ),
          if (_revisionPlan != null) ...[
            const Divider(color: Colors.white10, height: 24),
            Row(
              children: [
                const Icon(Icons.flash_on, color: Colors.orange, size: 18),
                const SizedBox(width: 8),
                Text(
                  "Suggested Revise Time: ${_revisionPlan!["best_time_to_revise"]}",
                  style: const TextStyle(
                    color: Colors.orange,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Text(
              "Flagged Weak Topics:",
              style: TextStyle(
                color: Colors.redAccent,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            ...(_revisionPlan!["weak_topics"] as List).map(
              (topic) => Text(
                "• $topic",
                style: const TextStyle(color: Colors.white70, fontSize: 12),
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              "Frequently Forgotten Concepts:",
              style: TextStyle(
                color: Colors.amberAccent,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            ...(_revisionPlan!["forgotten_concepts"] as List).map(
              (c) => Text(
                "• $c",
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                  height: 1.3,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
