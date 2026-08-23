import 'package:aaroha_app/core/constants.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class LearningHubScreen extends StatefulWidget {
  final String userId;
  const LearningHubScreen({super.key, required this.userId});

  @override
  State<LearningHubScreen> createState() => _LearningHubScreenState();
}

class _LearningHubScreenState extends State<LearningHubScreen> {
  bool _isLoading = false;
  List<dynamic> _courses = [];
  List<dynamic> _books = [];
  List<dynamic> _videos = [];
  List<dynamic> _roadmap = [];

  @override
  void initState() {
    super.initState();
    _fetchLearningHub();
  }

  // API Call: Learning Hub Resource Recommendations
  Future<void> _fetchLearningHub() async {
    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/education/learning-hub/${widget.userId}'),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _courses = data["courses"] ?? [];
          _books = data["books"] ?? [];
          _videos = data["videos"] ?? [];
          _roadmap = data["roadmap"] ?? [];
        });
      }
    } catch (e) {
      debugPrint("Learning Hub failed: $e");
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
          "Learning Hub Resources",
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.tealAccent),
            onPressed: _fetchLearningHub,
          ),
        ],
      ),
      body: Stack(
        children: [
          ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // Roadmap items
              _buildSectionHeader("PERSONALIZED ROADMAP", Icons.route_outlined),
              const SizedBox(height: 8),
              if (_roadmap.isNotEmpty)
                ..._roadmap.map(
                  (rm) => _buildResourceTile(
                    rm.toString(),
                    Icons.check_circle_outline,
                    Colors.orangeAccent,
                  ),
                )
              else
                const Text(
                  "No active roadmap milestones.",
                  style: TextStyle(color: Colors.white38, fontSize: 12),
                ),
              const SizedBox(height: 24),

              // Courses recommendations
              _buildSectionHeader("ONLINE COURSES", Icons.school_outlined),
              const SizedBox(height: 8),
              if (_courses.isNotEmpty)
                ..._courses.map(
                  (course) => _buildResourceTile(
                    course.toString(),
                    Icons.laptop_chromebook,
                    Colors.tealAccent,
                  ),
                )
              else
                const Text(
                  "No course recommendations loaded.",
                  style: TextStyle(color: Colors.white38, fontSize: 12),
                ),
              const SizedBox(height: 24),

              // Books recommendations
              _buildSectionHeader(
                "RECOMMENDED BOOKS",
                Icons.menu_book_outlined,
              ),
              const SizedBox(height: 8),
              if (_books.isNotEmpty)
                ..._books.map(
                  (book) => _buildResourceTile(
                    book.toString(),
                    Icons.book,
                    Colors.blueAccent,
                  ),
                )
              else
                const Text(
                  "No book recommendations loaded.",
                  style: TextStyle(color: Colors.white38, fontSize: 12),
                ),
              const SizedBox(height: 24),

              // Video recommendations
              _buildSectionHeader(
                "RECOMMENDED VIDEOS",
                Icons.video_library_outlined,
              ),
              const SizedBox(height: 8),
              if (_videos.isNotEmpty)
                ..._videos.map(
                  (vid) => _buildResourceTile(
                    vid.toString(),
                    Icons.video_collection,
                    Colors.redAccent,
                  ),
                )
              else
                const Text(
                  "No video recommendations loaded.",
                  style: TextStyle(color: Colors.white38, fontSize: 12),
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

  Widget _buildResourceTile(String text, IconData icon, Color color) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(10),
      ),
      child: ListTile(
        leading: Icon(icon, color: color),
        title: Text(
          text,
          style: const TextStyle(color: Colors.white, fontSize: 13),
        ),
      ),
    );
  }
}
