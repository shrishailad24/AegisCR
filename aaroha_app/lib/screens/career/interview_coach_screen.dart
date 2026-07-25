import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:aaroha_app/core/constants.dart';

class InterviewCoachScreen extends StatefulWidget {
  final String userId;
  const InterviewCoachScreen({super.key, required this.userId});

  @override
  State<InterviewCoachScreen> createState() => _InterviewCoachScreenState();
}

class _InterviewCoachScreenState extends State<InterviewCoachScreen> {
  final TextEditingController _msgController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  bool _isSessionActive = false;
  String _selectedRole = "Technical"; // "Technical" | "HR"
  bool _isLoading = false;

  final List<Map<String, String>> _chatHistory = [];
  int _latestScore = 100;
  String _latestFeedback = "Select a mode and begin the interview.";

  Future<void> _startInterview() async {
    setState(() {
      _isSessionActive = true;
      _chatHistory.clear();
      _isLoading = true;
    });

    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/career/interview-chat'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "message": "Hello, I am ready to begin my $_selectedRole interview.",
          "role": _selectedRole,
          "history": [],
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _chatHistory.add({
            "role": "assistant",
            "content": data["next_question"] ?? "Could you introduce yourself?",
          });
          _latestFeedback = "Session Started.";
        });
      }
    } catch (e) {
      debugPrint("Failed starting interview: $e");
    } finally {
      if (mounted)
        setState(() {
          _isLoading = false;
        });
    }
  }

  Future<void> _sendResponse() async {
    final responseText = _msgController.text.trim();
    if (responseText.isEmpty) return;

    _msgController.clear();
    setState(() {
      _chatHistory.add({"role": "user", "content": responseText});
      _isLoading = true;
    });

    _scrollToBottom();

    final String baseUrl = AppConstants.baseUrl;
    try {
      final List<Map<String, String>> sendHistory = List.from(_chatHistory);
      sendHistory.removeLast();

      final response = await http.post(
        Uri.parse('$baseUrl/career/interview-chat'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "message": responseText,
          "role": _selectedRole,
          "history": sendHistory,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _latestScore = data["score"] ?? 100;
          _latestFeedback = data["feedback"] ?? "";
          _chatHistory.add({
            "role": "assistant",
            "content": data["next_question"] ?? "Thanks for your answer.",
          });
        });
      }
    } catch (e) {
      debugPrint("Coach answer submission failed: $e");
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        _scrollToBottom();
      }
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "AI Interview Coach",
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Column(
        children: [
          if (!_isSessionActive) _buildSetupView() else _buildActiveDashboard(),

          Expanded(
            child: _isSessionActive
                ? _buildChatList()
                : const Center(
                    child: Padding(
                      padding: EdgeInsets.all(40.0),
                      child: Text(
                        "Customize parameters above and click 'Start Session' to begin.",
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.white30, fontSize: 13),
                      ),
                    ),
                  ),
          ),

          if (_isSessionActive) _buildInputBar(),
        ],
      ),
    );
  }

  Widget _buildSetupView() {
    return Container(
      padding: const EdgeInsets.all(20),
      color: const Color(0xFF1E293B),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              ChoiceChip(
                label: const Text("Technical"),
                selected: _selectedRole == "Technical",
                onSelected: (selected) {
                  if (selected) setState(() => _selectedRole = "Technical");
                },
              ),
              ChoiceChip(
                label: const Text("HR & Behavioral"),
                selected: _selectedRole == "HR",
                onSelected: (selected) {
                  if (selected) setState(() => _selectedRole = "HR");
                },
              ),
            ],
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              onPressed: _startInterview,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.purpleAccent,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Text(
                "Start Session",
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActiveDashboard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: const BoxDecoration(
        color: Color(0xFF1E293B),
        border: Border(bottom: BorderSide(color: Colors.white10)),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "Role: $_selectedRole Session",
                  style: const TextStyle(
                    color: Colors.purpleAccent,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  "Feedback: $_latestFeedback",
                  style: const TextStyle(color: Colors.white70, fontSize: 11),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.white10,
              shape: BoxShape.circle,
              border: Border.all(
                color: _latestScore >= 75
                    ? Colors.greenAccent
                    : Colors.amberAccent,
                width: 2,
              ),
            ),
            child: Text(
              "$_latestScore",
              style: TextStyle(
                color: _latestScore >= 75
                    ? Colors.greenAccent
                    : Colors.amberAccent,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChatList() {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: _chatHistory.length,
      itemBuilder: (context, index) {
        final message = _chatHistory[index];
        final isUser = message["role"] == "user";
        return Align(
          alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
          child: Container(
            margin: const EdgeInsets.symmetric(vertical: 6),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: isUser ? Colors.purple : const Color(0xFF1E293B),
              borderRadius: BorderRadius.only(
                topLeft: const Radius.circular(15),
                topRight: const Radius.circular(15),
                bottomLeft: Radius.circular(isUser ? 15 : 0),
                bottomRight: Radius.circular(isUser ? 0 : 15),
              ),
              border: isUser ? null : Border.all(color: Colors.white10),
            ),
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.8,
            ),
            child: Text(
              message["content"]!,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
                height: 1.4,
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildInputBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: const Color(0xFF1E293B),
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _msgController,
                style: const TextStyle(color: Colors.white, fontSize: 14),
                decoration: InputDecoration(
                  hintText: "Type your answer...",
                  hintStyle: const TextStyle(
                    color: Colors.white38,
                    fontSize: 14,
                  ),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide.none,
                  ),
                  fillColor: const Color(0xFF0F172A),
                  filled: true,
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                ),
                onSubmitted: (_) => _sendResponse(),
              ),
            ),
            const SizedBox(width: 8),
            CircleAvatar(
              radius: 20,
              backgroundColor: Colors.purpleAccent,
              child: IconButton(
                icon: _isLoading
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2,
                        ),
                      )
                    : const Icon(Icons.send, color: Colors.white, size: 18),
                onPressed: _isLoading ? null : _sendResponse,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
