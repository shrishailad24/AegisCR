import 'package:aaroha_app/core/constants.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class QuizGameScreen extends StatefulWidget {
  final String userId;
  const QuizGameScreen({super.key, required this.userId});

  @override
  State<QuizGameScreen> createState() => _QuizGameScreenState();
}

class _QuizGameScreenState extends State<QuizGameScreen> {
  bool _isLoading = false;

  // Gamification Data
  int _xp = 120;
  int _level = 1;
  List<dynamic> _badges = [];
  List<dynamic> _missions = [];

  // Quiz / Mock Exam Data
  final TextEditingController _subjectC = TextEditingController(
    text: "Operating Systems",
  );
  List<dynamic> _quizQuestions = [];
  int _currentQuestionIdx = 0;
  int _score = 0;
  bool _quizCompleted = false;
  String _selectedOption = "";
  bool _showCorrectAnswer = false;

  // Performance Diagnostics
  final List<Map<String, dynamic>> _weakTopics = [
    {
      "topic": "Virtual Memory Page Replacement",
      "performance": "40% (Needs Focus)",
      "color": Colors.redAccent,
    },
    {
      "topic": "Process Synchronization Semaphores",
      "performance": "65% (Borderline)",
      "color": Colors.amberAccent,
    },
    {
      "topic": "CPU Scheduling",
      "performance": "90% (Proficient)",
      "color": Colors.greenAccent,
    },
  ];

  @override
  void initState() {
    super.initState();
    _fetchGamesData("get");
  }

  // API Call: Games Data (get/update XP & Missions)
  Future<void> _fetchGamesData(
    String action, {
    int xp = 0,
    String badge = "",
    String mission = "",
  }) async {
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/education/games-data'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "action": action,
          "xp_amount": xp,
          "badge_name": badge,
          "mission_name": mission,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _xp = data["xp"] ?? 120;
          _level = data["level"] ?? 1;
          _badges = data["badges"] ?? [];
          _missions = data["missions"] ?? [];
        });
      }
    } catch (e) {
      debugPrint("Games data failed: $e");
    }
  }

  // API Call: Quiz Generator
  Future<void> _generateQuiz() async {
    final text = _subjectC.text.trim();
    if (text.isEmpty) return;

    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/education/quiz-generator'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"user_id": widget.userId, "subject": text}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _quizQuestions = data["quiz"] ?? [];
          _currentQuestionIdx = 0;
          _score = 0;
          _quizCompleted = false;
          _selectedOption = "";
          _showCorrectAnswer = false;
        });
      }
    } catch (e) {
      debugPrint("Quiz generation failed: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _submitAnswer() {
    final currentQ = _quizQuestions[_currentQuestionIdx];
    final correctAns = currentQ["answer"].toString().trim();
    final selectedAns = _selectedOption.trim();

    if (selectedAns == correctAns) {
      _score += 1;
      _fetchGamesData("add_xp", xp: 30); // Award 30 XP on correct answer
    }

    setState(() {
      _showCorrectAnswer = true;
    });

    Future.delayed(const Duration(seconds: 2), () {
      if (!mounted) return;
      setState(() {
        if (_currentQuestionIdx < _quizQuestions.length - 1) {
          _currentQuestionIdx += 1;
          _selectedOption = "";
          _showCorrectAnswer = false;
        } else {
          _quizCompleted = true;
          // Completed quiz mission update
          _fetchGamesData("complete_mission", mission: "daily_quiz");
          if (_score == _quizQuestions.length) {
            _fetchGamesData("unlock_badge", badge: "Perfect Score");
          }
        }
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "Quiz, Mock Tests & Games",
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
              // GAMIFICATION DASHBOARD (XP / LEVEL / BADGES)
              _buildSectionHeader(
                "AAROHA GAMIFIED PROFILE",
                Icons.military_tech,
              ),
              const SizedBox(height: 12),
              _buildGamifiedPanel(),
              const SizedBox(height: 24),

              // AI MOCK TEST ENGINE
              _buildSectionHeader("AI SUBJECT QUIZ & MOCK EXAMS", Icons.quiz),
              const SizedBox(height: 12),
              _buildQuizCard(),
              const SizedBox(height: 24),

              // DIAGNOSTIC RADAR (WEAK TOPICS)
              _buildSectionHeader(
                "WEAK-TOPIC DETECTION & PERFORMANCE",
                Icons.analytics,
              ),
              const SizedBox(height: 12),
              _buildDiagnosticsCard(),
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
        Icon(icon, color: Colors.tealAccent, size: 18),
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

  Widget _buildGamifiedPanel() {
    final nextLevelXp = 300;
    final xpProgress = (_xp % nextLevelXp) / nextLevelXp;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF0D1B2A), Color(0xFF1B263B)],
        ),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.tealAccent.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    "Student Level $_level",
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    "Total XP: $_xp XP",
                    style: const TextStyle(
                      color: Colors.tealAccent,
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
              const Icon(Icons.stars, color: Colors.amber, size: 36),
            ],
          ),
          const SizedBox(height: 10),
          LinearProgressIndicator(
            value: xpProgress,
            color: Colors.tealAccent,
            backgroundColor: Colors.white10,
            minHeight: 8,
          ),
          const SizedBox(height: 16),
          const Text(
            "Achievements & Badges:",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: _badges
                .map(
                  (b) => Chip(
                    backgroundColor: Colors.teal.withValues(alpha: 0.2),
                    avatar: const Icon(
                      Icons.workspace_premium,
                      color: Colors.amber,
                      size: 16,
                    ),
                    label: Text(
                      b.toString(),
                      style: const TextStyle(color: Colors.white, fontSize: 10),
                    ),
                  ),
                )
                .toList(),
          ),
          const Divider(color: Colors.white10, height: 24),
          const Text(
            "Daily Learning Missions:",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          ..._missions.map(
            (mission) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 4.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Icon(
                        mission["completed"]
                            ? Icons.check_circle
                            : Icons.circle_outlined,
                        color: mission["completed"]
                            ? Colors.tealAccent
                            : Colors.white24,
                        size: 16,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        mission["title"],
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                  Text(
                    "+${mission["xp"]} XP",
                    style: const TextStyle(
                      color: Colors.amber,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuizCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.tealAccent.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_quizQuestions.isEmpty) ...[
            TextField(
              controller: _subjectC,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(
                labelText: "Focus Subject / Topic",
                labelStyle: TextStyle(color: Colors.white60),
                enabledBorder: UnderlineInputBorder(
                  borderSide: BorderSide(color: Colors.white24),
                ),
              ),
            ),
            const SizedBox(height: 12),
            ElevatedButton.icon(
              onPressed: _generateQuiz,
              icon: const Icon(Icons.gamepad, size: 16),
              label: const Text("Generate Mock Test"),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.teal,
                foregroundColor: Colors.white,
              ),
            ),
          ] else if (_quizCompleted) ...[
            Center(
              child: Column(
                children: [
                  const Icon(Icons.emoji_events, color: Colors.amber, size: 48),
                  const SizedBox(height: 10),
                  const Text(
                    "Mock Test Finished!",
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    "Score: $_score / ${_quizQuestions.length}",
                    style: const TextStyle(
                      color: Colors.amberAccent,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton(
                    onPressed: () => setState(() => _quizQuestions.clear()),
                    child: const Text("Create Another Test"),
                  ),
                ],
              ),
            ),
          ] else ...[
            _buildActiveQuizWidget(),
          ],
        ],
      ),
    );
  }

  Widget _buildActiveQuizWidget() {
    final currentQ = _quizQuestions[_currentQuestionIdx];
    final options = currentQ["options"] as List;
    final correctAns = currentQ["answer"].toString().trim();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          "Question ${_currentQuestionIdx + 1} of ${_quizQuestions.length}",
          style: const TextStyle(color: Colors.tealAccent, fontSize: 12),
        ),
        const SizedBox(height: 8),
        Text(
          currentQ["question"],
          style: const TextStyle(
            color: Colors.white,
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        ...options.map((opt) {
          final optStr = opt.toString();
          final isSelected = _selectedOption == optStr;
          Color optionColor = const Color(0xFF0F172A);
          if (_showCorrectAnswer) {
            if (optStr.trim() == correctAns) {
              optionColor = Colors.green.withValues(alpha: 0.3);
            } else if (isSelected) {
              optionColor = Colors.red.withValues(alpha: 0.3);
            }
          } else if (isSelected) {
            optionColor = Colors.teal.withValues(alpha: 0.3);
          }

          return InkWell(
            onTap: _showCorrectAnswer
                ? null
                : () {
                    setState(() {
                      _selectedOption = optStr;
                    });
                  },
            child: Container(
              margin: const EdgeInsets.symmetric(vertical: 4),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: optionColor,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: isSelected ? Colors.tealAccent : Colors.white12,
                ),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      optStr,
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 13,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        }),
        const SizedBox(height: 12),
        if (!_showCorrectAnswer)
          Align(
            alignment: Alignment.centerRight,
            child: ElevatedButton(
              onPressed: _selectedOption.isEmpty ? null : _submitAnswer,
              style: ElevatedButton.styleFrom(backgroundColor: Colors.teal),
              child: const Text(
                "Submit Answer",
                style: TextStyle(color: Colors.white),
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildDiagnosticsCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.tealAccent.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "AI Diagnostic Analysis:",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 10),
          ..._weakTopics.map(
            (wt) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 6.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      wt["topic"],
                      style: const TextStyle(color: Colors.white, fontSize: 12),
                    ),
                  ),
                  Text(
                    wt["performance"],
                    style: TextStyle(
                      color: wt["color"],
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
