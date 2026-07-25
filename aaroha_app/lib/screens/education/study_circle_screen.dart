import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class StudyCircleScreen extends StatefulWidget {
  final String userId;
  const StudyCircleScreen({super.key, required this.userId});

  @override
  State<StudyCircleScreen> createState() => _StudyCircleScreenState();
}

class _StudyCircleScreenState extends State<StudyCircleScreen> {
  bool _isLoading = false;
  Map<String, dynamic> _circles = {};
  String _selectedCircle = "";

  final TextEditingController _newCircleNameC = TextEditingController();
  final TextEditingController _postContentC = TextEditingController();

  // Team Leaderboard
  final List<Map<String, dynamic>> _leaderboard = [
    {
      "rank": "1",
      "name": "Rahul Sharma",
      "xp": "1250 XP",
      "badge": "Elite Scholar",
    },
    {
      "rank": "2",
      "name": "Shash (You)",
      "xp": "840 XP",
      "badge": "Quiz Warrior",
    },
    {
      "rank": "3",
      "name": "Aditya Verma",
      "xp": "790 XP",
      "badge": "Pomodoro King",
    },
  ];

  @override
  void initState() {
    super.initState();
    _fetchCircles("list");
  }

  // API Call: Study Circle Manager
  Future<void> _fetchCircles(
    String action, {
    String name = "",
    String content = "",
  }) async {
    setState(() => _isLoading = true);
    final String baseUrl = kIsWeb
        ? 'http://localhost:8002'
        : 'http://10.0.2.2:8002';
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/education/study-circle'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "action": action,
          "circle_name": name,
          "post_content": content,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _circles = data["circles"] ?? {};
          if (_selectedCircle.isEmpty && _circles.isNotEmpty) {
            _selectedCircle = _circles.keys.first;
          }
        });
      }
    } catch (e) {
      debugPrint("Study circles failed: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _createCircle() {
    final name = _newCircleNameC.text.trim();
    if (name.isEmpty) return;
    _fetchCircles("create", name: name);
    _newCircleNameC.clear();
    Navigator.pop(context); // Close dialog
  }

  void _postMessage() {
    final text = _postContentC.text.trim();
    if (text.isEmpty || _selectedCircle.isEmpty) return;
    _fetchCircles("post", name: _selectedCircle, content: text);
    _postContentC.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "Study Circles",
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(
              Icons.add_circle_outline,
              color: Colors.blueAccent,
            ),
            onPressed: _showCreateCircleDialog,
          ),
        ],
      ),
      body: Stack(
        children: [
          Column(
            children: [
              // Circle Selection Bar
              if (_circles.isNotEmpty) _buildCirclesSelectionBar(),

              Expanded(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Left Panel: Group Chat & Feed
                    Expanded(
                      flex: 3,
                      child: _selectedCircle.isNotEmpty
                          ? _buildCircleFeedPanel()
                          : const Center(
                              child: Text(
                                "No active Study Circle selected.",
                                style: TextStyle(color: Colors.white38),
                              ),
                            ),
                    ),

                    // Right Panel: Team Leaderboard
                    Expanded(
                      flex: 2,
                      child: Container(
                        decoration: const BoxDecoration(
                          border: Border(
                            left: BorderSide(color: Colors.white10),
                          ),
                          color: Color(0xFF131722),
                        ),
                        child: _buildTeamLeaderboard(),
                      ),
                    ),
                  ],
                ),
              ),
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

  Widget _buildCirclesSelectionBar() {
    return Container(
      height: 50,
      color: const Color(0xFF1E293B),
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        children: _circles.keys.map((cName) {
          final isSelected = _selectedCircle == cName;
          final isMember = (_circles[cName]["members"] as List).contains(
            widget.userId,
          );
          return Container(
            margin: const EdgeInsets.symmetric(horizontal: 6, vertical: 8),
            child: ChoiceChip(
              label: Text(cName, style: const TextStyle(fontSize: 12)),
              selected: isSelected,
              onSelected: (val) {
                if (val) {
                  setState(() => _selectedCircle = cName);
                  if (!isMember) {
                    _fetchCircles("join", name: cName);
                  }
                }
              },
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildCircleFeedPanel() {
    final circleData = _circles[_selectedCircle];
    final List posts = circleData != null ? circleData["posts"] ?? [] : [];

    return Column(
      children: [
        // Member count bar
        Container(
          padding: const EdgeInsets.all(12),
          color: const Color(0xFF1E293B).withValues(alpha: 0.5),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "$_selectedCircle Room",
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
              Text(
                "${circleData != null ? (circleData["members"] as List).length : 0} Active Members",
                style: const TextStyle(color: Colors.white54, fontSize: 11),
              ),
            ],
          ),
        ),

        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: posts.length,
            itemBuilder: (context, idx) {
              final post = posts[idx];
              final isMe = post["user"] == widget.userId;
              return Container(
                margin: const EdgeInsets.symmetric(vertical: 6),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: isMe
                      ? const Color(0xFF1E293B)
                      : const Color(0xFF0F172A),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: Colors.white.withValues(alpha: 0.05),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          isMe ? "You" : post["user"].toString(),
                          style: TextStyle(
                            color: isMe ? Colors.blueAccent : Colors.tealAccent,
                            fontWeight: FontWeight.bold,
                            fontSize: 11,
                          ),
                        ),
                        const Text(
                          "Recent",
                          style: TextStyle(color: Colors.white24, fontSize: 9),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      post["content"].toString(),
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 12,
                        height: 1.3,
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ),

        // Post Input Area
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          color: const Color(0xFF1E293B),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _postContentC,
                  style: const TextStyle(color: Colors.white, fontSize: 12),
                  decoration: const InputDecoration(
                    hintText: "Share a note or study room link...",
                    hintStyle: TextStyle(color: Colors.white24, fontSize: 12),
                    border: InputBorder.none,
                  ),
                ),
              ),
              IconButton(
                icon: const Icon(Icons.send, color: Colors.blueAccent),
                onPressed: _postMessage,
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTeamLeaderboard() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text(
          "TEAM LEADERBOARD",
          style: TextStyle(
            color: Colors.white70,
            fontSize: 11,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.2,
          ),
        ),
        const SizedBox(height: 12),
        ..._leaderboard.map(
          (lb) => Container(
            margin: const EdgeInsets.symmetric(vertical: 4),
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.white.withValues(alpha: 0.05)),
            ),
            child: Row(
              children: [
                Container(
                  width: 24,
                  alignment: Alignment.center,
                  child: Text(
                    lb["rank"],
                    style: const TextStyle(
                      color: Colors.amberAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        lb["name"],
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                      Text(
                        lb["badge"],
                        style: const TextStyle(
                          color: Colors.white38,
                          fontSize: 10,
                        ),
                      ),
                    ],
                  ),
                ),
                Text(
                  lb["xp"],
                  style: const TextStyle(
                    color: Colors.tealAccent,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  void _showCreateCircleDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "Create Study Circle",
          style: TextStyle(color: Colors.white),
        ),
        content: TextField(
          controller: _newCircleNameC,
          style: const TextStyle(color: Colors.white),
          decoration: const InputDecoration(
            hintText: "Enter Group Name (e.g. Physics Lab)",
            hintStyle: TextStyle(color: Colors.white24),
            enabledBorder: UnderlineInputBorder(
              borderSide: BorderSide(color: Colors.white24),
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Cancel"),
          ),
          ElevatedButton(onPressed: _createCircle, child: const Text("Create")),
        ],
      ),
    );
  }
}
