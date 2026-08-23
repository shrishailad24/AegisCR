import 'package:aaroha_app/core/constants.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class PortfolioMentorScreen extends StatefulWidget {
  final String userId;
  const PortfolioMentorScreen({super.key, required this.userId});

  @override
  State<PortfolioMentorScreen> createState() => _PortfolioMentorScreenState();
}

class _PortfolioMentorScreenState extends State<PortfolioMentorScreen> {
  final TextEditingController _stackController = TextEditingController(
    text: "Python, FastAPI, Flutter",
  );
  bool _isLoading = false;
  List<dynamic> _suggestedProjects = [];
  List<dynamic> _portfolioTips = [];
  bool _hasSearched = false;

  Future<void> _fetchPortfolioAdvice() async {
    if (_stackController.text.trim().isEmpty) return;
    setState(() {
      _isLoading = true;
    });

    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/career/portfolio-mentor'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "tech_stack": _stackController.text.trim(),
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _suggestedProjects = data['projects'] ?? [];
          _portfolioTips = data['portfolio_tips'] ?? [];
          _hasSearched = true;
        });
      }
    } catch (e) {
      debugPrint("Portfolio Mentor failed: $e");
    } finally {
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
          "Project & Portfolio Mentor",
          style: TextStyle(color: Colors.white),
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
            // Stack input
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(15),
              ),
              child: Column(
                children: [
                  TextField(
                    controller: _stackController,
                    style: const TextStyle(color: Colors.white),
                    decoration: const InputDecoration(
                      labelText: "Your Target Tech Stack",
                      labelStyle: TextStyle(color: Colors.purpleAccent),
                      hintText: "e.g., Python, SQL, React",
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
                      onPressed: _isLoading ? null : _fetchPortfolioAdvice,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.purpleAccent,
                      ),
                      icon: const Icon(Icons.auto_awesome, color: Colors.white),
                      label: Text(
                        _isLoading ? "Reviewing..." : "Get Mentor Suggestions",
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
              // Suggested projects
              const Text(
                "🛠️ SUGGESTED DEVELOPMENT PROJECTS",
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 8),
              if (_suggestedProjects.isEmpty)
                const Text(
                  "No project suggestions found.",
                  style: TextStyle(color: Colors.white70),
                )
              else
                ..._suggestedProjects.map(
                  (proj) => Card(
                    color: const Color(0xFF1E293B),
                    margin: const EdgeInsets.only(bottom: 12),
                    child: ListTile(
                      leading: const Icon(
                        Icons.code,
                        color: Colors.purpleAccent,
                      ),
                      title: Text(
                        proj['name'] ?? "Project Title",
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      subtitle: Text(
                        proj['description'] ?? "",
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ),
                ),
              const SizedBox(height: 24),

              // Portfolio Improvement Tips
              const Text(
                "💡 PORTFOLIO & GITHUB RECOMMENDATIONS",
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 8),
              ..._portfolioTips.map(
                (tip) => Card(
                  color: const Color(0xFF1E293B),
                  child: ListTile(
                    leading: const Icon(
                      Icons.check_circle_outline,
                      color: Colors.tealAccent,
                    ),
                    title: Text(
                      tip.toString(),
                      style: const TextStyle(color: Colors.white, fontSize: 13),
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
