import 'package:aaroha_app/core/constants.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class NotesTutorScreen extends StatefulWidget {
  final String userId;
  const NotesTutorScreen({super.key, required this.userId});

  @override
  State<NotesTutorScreen> createState() => _NotesTutorScreenState();
}

class _NotesTutorScreenState extends State<NotesTutorScreen>
    with SingleTickerProviderStateMixin {
  bool _isLoading = false;

  // AI Tutor & Doubt Solver
  final TextEditingController _doubtC = TextEditingController();
  String _solverExplanation = "Submit a concept to get details.";
  List<dynamic> _solverSteps = [];
  String _difficulty = "Medium";
  String _preferredLanguage = "English";

  // Flashcards & Smart Notes
  final TextEditingController _notesContentC = TextEditingController();
  List<dynamic> _flashcards = [];
  final Map<int, bool> _flippedCardIndices =
      {}; // Track flipped state for each index
  String _notesSummary = "";
  List<dynamic> _keyPoints = [];

  // Lecture Assistant
  bool _isRecording = false;
  double _waveformHeight = 10.0;
  final TextEditingController _transcriptC = TextEditingController();
  Map<String, dynamic>? _lectureOutput;

  // Research Assistant
  final TextEditingController _paperC = TextEditingController();
  String _citationStyle = "APA";
  Map<String, dynamic>? _researchOutput;

  @override
  void initState() {
    super.initState();
  }

  // API Call: AI Doubt Solver (with multilingual)
  Future<void> _solveDoubt() async {
    final text = _doubtC.text.trim();
    if (text.isEmpty) return;

    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      // Modify doubt query to enforce multilingual requirement
      final localizedQuery =
          "$text (Please provide explanation and steps in $_preferredLanguage language)";
      final response = await http.post(
        Uri.parse('$baseUrl/education/doubt-solver'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "doubt": localizedQuery,
          "difficulty": _difficulty,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _solverExplanation = data["explanation"] ?? "";
          _solverSteps = data["steps"] ?? [];
        });
      }
    } catch (e) {
      debugPrint("Doubt solver failed: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  // API Call: Mock notes analyzer/generator
  Future<void> _analyzeNotes() async {
    final content = _notesContentC.text.trim();
    if (content.isEmpty) return;

    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      // Generate summary and flashcards from direct input text or mock file
      final response = await http.post(
        Uri.parse(
          '$baseUrl/education/lecture-assistant',
        ), // Reuses lecture helper for notes text analysis
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"user_id": widget.userId, "lecture_text": content}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _notesSummary = data["summary"] ?? "";
          _keyPoints = data["notes"] ?? [];
          // Make dummy flashcards from key points
          _flashcards = (_keyPoints.length > 2)
              ? [
                  {
                    "question": "What is the core premise of the notes?",
                    "answer": _notesSummary,
                  },
                  {"question": "Recall Key Point 1:", "answer": _keyPoints[0]},
                  {"question": "Recall Key Point 2:", "answer": _keyPoints[1]},
                ]
              : [
                  {
                    "question": "Core Premise",
                    "answer":
                        "The text discusses general principles of learning and implementation.",
                  },
                  {
                    "question": "Flashcard 2",
                    "answer":
                        "Details are saved inside the study genome tracker.",
                  },
                ];
          _flippedCardIndices.clear();
        });
      }
    } catch (e) {
      debugPrint("Notes analysis failed: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  // API Call: Lecture Assistant
  Future<void> _processLecture() async {
    final text = _transcriptC.text.trim();
    if (text.isEmpty) return;

    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/education/lecture-assistant'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"user_id": widget.userId, "lecture_text": text}),
      );
      if (response.statusCode == 200) {
        setState(() {
          _lectureOutput = jsonDecode(response.body);
        });
      }
    } catch (e) {
      debugPrint("Lecture processing failed: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  // API Call: Research Assistant
  Future<void> _processResearch() async {
    final text = _paperC.text.trim();
    if (text.isEmpty) return;

    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/education/research-assistant'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "paper_text": text,
          "citation_format": _citationStyle,
        }),
      );
      if (response.statusCode == 200) {
        setState(() {
          _researchOutput = jsonDecode(response.body);
        });
      }
    } catch (e) {
      debugPrint("Research assistant failed: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _simulateRecording() async {
    if (_isRecording) {
      setState(() {
        _isRecording = false;
        _transcriptC.text =
            "This lecture discusses the time complexity of Sorting Algorithms. Quick Sort operates at average-case O(N log N) using a pivot element. Merge Sort is also O(N log N) but requires O(N) auxiliary space, making it stable but memory-expensive.";
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Recording complete. Transcript auto-populated!"),
        ),
      );
    } else {
      setState(() {
        _isRecording = true;
      });
      // Waveform animation simulation
      for (int i = 0; i < 10; i++) {
        await Future.delayed(const Duration(milliseconds: 300));
        if (!_isRecording) break;
        setState(() {
          _waveformHeight = (i % 2 == 0) ? 40.0 : 15.0;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "Notes, Tutor & Research",
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
              // 1. DUAL MODE TUTOR (Doubt Solver with Multilingual support)
              _buildSectionHeader("1. MULTILINGUAL AI TUTOR", Icons.translate),
              const SizedBox(height: 12),
              _buildTutorCard(),
              const SizedBox(height: 24),

              // 2. FLASHCARDS & SMART NOTES SUMMARY
              _buildSectionHeader(
                "2. SMART NOTES & INTERACTIVE FLASHCARDS",
                Icons.style,
              ),
              const SizedBox(height: 12),
              _buildFlashcardsCard(),
              const SizedBox(height: 24),

              // 3. AI LECTURE ASSISTANT
              _buildSectionHeader("3. AI LECTURE ASSISTANT", Icons.mic),
              const SizedBox(height: 12),
              _buildLectureAssistantCard(),
              const SizedBox(height: 24),

              // 4. AI RESEARCH ASSISTANT
              _buildSectionHeader(
                "4. AI RESEARCH ASSISTANT",
                Icons.travel_explore,
              ),
              const SizedBox(height: 12),
              _buildResearchCard(),
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
        Icon(icon, color: Colors.purpleAccent, size: 18),
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

  Widget _buildTutorCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.purpleAccent.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          TextField(
            controller: _doubtC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Ask a concept or question...",
              labelStyle: TextStyle(color: Colors.white60),
              enabledBorder: UnderlineInputBorder(
                borderSide: BorderSide(color: Colors.white24),
              ),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "Difficulty:",
                style: TextStyle(color: Colors.white70, fontSize: 12),
              ),
              Row(
                children: ["Easy", "Medium", "Hard"]
                    .map(
                      (lvl) => Padding(
                        padding: const EdgeInsets.only(left: 4.0),
                        child: ChoiceChip(
                          label: Text(
                            lvl,
                            style: const TextStyle(fontSize: 10),
                          ),
                          selected: _difficulty == lvl,
                          onSelected: (sel) {
                            if (sel) setState(() => _difficulty = lvl);
                          },
                        ),
                      ),
                    )
                    .toList(),
              ),
            ],
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "Language:",
                style: TextStyle(color: Colors.white70, fontSize: 12),
              ),
              DropdownButton<String>(
                value: _preferredLanguage,
                dropdownColor: const Color(0xFF1E293B),
                style: const TextStyle(color: Colors.white, fontSize: 12),
                items: ["English", "Hindi", "Spanish", "French", "German"]
                    .map((l) => DropdownMenuItem(value: l, child: Text(l)))
                    .toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _preferredLanguage = val);
                },
              ),
            ],
          ),
          const SizedBox(height: 10),
          ElevatedButton(
            onPressed: _solveDoubt,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.purpleAccent,
            ),
            child: const Text(
              "Explain Concept",
              style: TextStyle(color: Colors.white),
            ),
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF0F172A),
              borderRadius: BorderRadius.circular(10),
            ),
            width: double.infinity,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "Tutor Explanation:",
                  style: TextStyle(
                    color: Colors.purpleAccent,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  _solverExplanation,
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 12,
                    height: 1.4,
                  ),
                ),
                if (_solverSteps.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  ..._solverSteps.map(
                    (step) => Text(
                      "• $step",
                      style: const TextStyle(
                        color: Colors.amberAccent,
                        fontSize: 11,
                        height: 1.3,
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFlashcardsCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.purpleAccent.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          TextField(
            controller: _notesContentC,
            maxLines: 3,
            style: const TextStyle(color: Colors.white, fontSize: 12),
            decoration: const InputDecoration(
              labelText: "Paste study notes or transcript snippet...",
              labelStyle: TextStyle(color: Colors.white60),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          ElevatedButton.icon(
            onPressed: _analyzeNotes,
            icon: const Icon(Icons.auto_awesome, size: 16),
            label: const Text("Generate Summary & Flashcards"),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.teal),
          ),
          if (_notesSummary.isNotEmpty) ...[
            const SizedBox(height: 16),
            const Text(
              "Notes Summary:",
              style: TextStyle(
                color: Colors.tealAccent,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              _notesSummary,
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 12,
                height: 1.3,
              ),
            ),
          ],
          if (_flashcards.isNotEmpty) ...[
            const Divider(color: Colors.white10, height: 24),
            const Text(
              "Tap Flashcards to Flip:",
              style: TextStyle(
                color: Colors.amberAccent,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            SizedBox(
              height: 130,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: _flashcards.length,
                itemBuilder: (context, idx) {
                  final card = _flashcards[idx];
                  final isFlipped = _flippedCardIndices[idx] ?? false;
                  return InkWell(
                    onTap: () {
                      setState(() {
                        _flippedCardIndices[idx] = !isFlipped;
                      });
                    },
                    child: Container(
                      width: 200,
                      margin: const EdgeInsets.only(right: 12),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: isFlipped
                              ? [
                                  const Color(0xFF3B0764),
                                  const Color(0xFF1E1B4B),
                                ]
                              : [
                                  const Color(0xFF1E293B),
                                  const Color(0xFF334155),
                                ],
                        ),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(
                          color: Colors.amber.withValues(alpha: 0.2),
                        ),
                      ),
                      child: Center(
                        child: Text(
                          isFlipped ? card["answer"] : card["question"],
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: isFlipped
                                ? Colors.amberAccent
                                : Colors.white,
                            fontSize: 12,
                            fontWeight: isFlipped
                                ? FontWeight.normal
                                : FontWeight.bold,
                          ),
                          maxLines: 5,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildLectureAssistantCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.purpleAccent.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "AI Speech-to-Notes Live",
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
              IconButton(
                onPressed: _simulateRecording,
                icon: Icon(
                  _isRecording ? Icons.stop_circle : Icons.mic_none,
                  color: _isRecording ? Colors.red : Colors.blueAccent,
                  size: 28,
                ),
              ),
            ],
          ),
          if (_isRecording) ...[
            const SizedBox(height: 6),
            const Text(
              "Simulating Speech Recording (Say something...)",
              style: TextStyle(color: Colors.redAccent, fontSize: 10),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(
                8,
                (index) => Container(
                  margin: const EdgeInsets.symmetric(horizontal: 2),
                  width: 4,
                  height: _waveformHeight + (index * 2 % 10),
                  color: Colors.red,
                ),
              ),
            ),
          ],
          const SizedBox(height: 12),
          TextField(
            controller: _transcriptC,
            maxLines: 3,
            style: const TextStyle(color: Colors.white, fontSize: 12),
            decoration: const InputDecoration(
              hintText:
                  "Lecture transcript will auto-populate, or type here...",
              hintStyle: TextStyle(color: Colors.white24),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 10),
          ElevatedButton(
            onPressed: _processLecture,
            style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
            child: const Text(
              "Convert speech transcript to Notes",
              style: TextStyle(color: Colors.white),
            ),
          ),
          if (_lectureOutput != null) ...[
            const Divider(color: Colors.white10, height: 24),
            const Text(
              "Lecture Summary:",
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
            Text(
              _lectureOutput!["summary"] ?? "",
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 12,
                height: 1.3,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              "Key Concepts Extracted:",
              style: TextStyle(
                color: Colors.blueAccent,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            ...(_lectureOutput!["notes"] as List).map(
              (n) => Text(
                "• $n",
                style: const TextStyle(color: Colors.white70, fontSize: 11),
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              "Auto Revision Notes:",
              style: TextStyle(
                color: Colors.greenAccent,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            ...(_lectureOutput!["revision_notes"] as List).map(
              (rn) => Text(
                "• $rn",
                style: const TextStyle(color: Colors.white70, fontSize: 11),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildResearchCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.purpleAccent.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          TextField(
            controller: _paperC,
            maxLines: 3,
            style: const TextStyle(color: Colors.white, fontSize: 12),
            decoration: const InputDecoration(
              labelText: "Input research paper text snippet...",
              labelStyle: TextStyle(color: Colors.white60),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "Citation Format:",
                style: TextStyle(color: Colors.white70, fontSize: 12),
              ),
              Row(
                children: ["APA", "MLA", "Chicago"]
                    .map(
                      (style) => Padding(
                        padding: const EdgeInsets.only(left: 4.0),
                        child: ChoiceChip(
                          label: Text(
                            style,
                            style: const TextStyle(fontSize: 10),
                          ),
                          selected: _citationStyle == style,
                          onSelected: (sel) {
                            if (sel) setState(() => _citationStyle = style);
                          },
                        ),
                      ),
                    )
                    .toList(),
              ),
            ],
          ),
          ElevatedButton(
            onPressed: _processResearch,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.purpleAccent,
            ),
            child: const Text(
              "Analyze Research Paper",
              style: TextStyle(color: Colors.white),
            ),
          ),
          if (_researchOutput != null) ...[
            const Divider(color: Colors.white10, height: 24),
            const Text(
              "Abstract Summary:",
              style: TextStyle(
                color: Colors.amberAccent,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              _researchOutput!["summary"] ?? "",
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 11,
                height: 1.3,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              "Generated Citation:",
              style: TextStyle(
                color: Colors.greenAccent,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            SelectableText(
              _researchOutput!["citation"] ?? "",
              style: const TextStyle(
                color: Colors.greenAccent,
                fontSize: 11,
                fontStyle: FontStyle.italic,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              "Comparative Arguments:",
              style: TextStyle(
                color: Colors.blueAccent,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            ...(_researchOutput!["argument_comparison"] as List).map(
              (arg) => Text(
                "• $arg",
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 11,
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
