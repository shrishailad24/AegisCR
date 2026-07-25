import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:aaroha_app/core/constants.dart';

class LearningTwinScreen extends StatefulWidget {
  final String userId;
  const LearningTwinScreen({super.key, required this.userId});

  @override
  State<LearningTwinScreen> createState() => _LearningTwinScreenState();
}

class _LearningTwinScreenState extends State<LearningTwinScreen> {
  final TextEditingController _msgC = TextEditingController();
  final List<Map<String, String>> _messages = [
    {
      "role": "assistant",
      "content":
          "Hey Shash! I've analyzed your computer science study logs. You are doing great on DSA, but we need to strengthen Network Routing and computer systems. How can I help you today?",
    },
  ];
  bool _isLoading = false;

  Future<void> _sendMessage() async {
    final text = _msgC.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add({"role": "user", "content": text});
      _msgC.clear();
      _isLoading = true;
    });

    final String baseUrl = AppConstants.baseUrl;
    try {
      final history = _messages.sublist(0, _messages.length - 1);
      final response = await http.post(
        Uri.parse('$baseUrl/education/learning-twin'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "message": text,
          "chat_history": history,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _messages.add({"role": "assistant", "content": data["answer"] ?? ""});
        });
      } else {
        setState(() {
          _messages.add({
            "role": "assistant",
            "content": "Oops, connection error: ${response.statusCode}.",
          });
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _messages.add({
            "role": "assistant",
            "content": "Failed to reach AI Learning Twin: $e",
          });
        });
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: Colors.indigoAccent.withOpacity(0.15),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.psychology,
                color: Colors.indigoAccent,
                size: 20,
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text(
                    "AI Learning Twin",
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 15,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    "Companion Synced",
                    style: TextStyle(color: Colors.indigoAccent, fontSize: 10),
                  ),
                ],
              ),
            ),
          ],
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                final isUser = msg["role"] == "user";
                return Align(
                  alignment: isUser
                      ? Alignment.centerRight
                      : Alignment.centerLeft,
                  child: Container(
                    constraints: BoxConstraints(
                      maxWidth: MediaQuery.of(context).size.width * 0.8,
                    ),
                    margin: const EdgeInsets.symmetric(vertical: 6),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 12,
                    ),
                    decoration: BoxDecoration(
                      color: isUser
                          ? const Color(0xFF3B82F6)
                          : const Color(0xFF1E293B),
                      borderRadius: BorderRadius.only(
                        topLeft: const Radius.circular(15),
                        topRight: const Radius.circular(15),
                        bottomLeft: isUser
                            ? const Radius.circular(15)
                            : const Radius.circular(0),
                        bottomRight: isUser
                            ? const Radius.circular(0)
                            : const Radius.circular(15),
                      ),
                      border: Border.all(
                        color: isUser
                            ? Colors.transparent
                            : Colors.indigoAccent.withOpacity(0.15),
                      ),
                    ),
                    child: Text(
                      msg["content"] ?? "",
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                        height: 1.3,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 8.0),
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  color: Colors.indigoAccent,
                  strokeWidth: 2,
                ),
              ),
            ),
          _buildChatInput(),
        ],
      ),
    );
  }

  Widget _buildChatInput() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      color: const Color(0xFF1E293B),
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _msgC,
                style: const TextStyle(color: Colors.white, fontSize: 14),
                decoration: InputDecoration(
                  hintText: "Ask your Twin...",
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
                onSubmitted: (_) => _sendMessage(),
              ),
            ),
            const SizedBox(width: 8),
            CircleAvatar(
              radius: 20,
              backgroundColor: Colors.indigoAccent,
              child: IconButton(
                icon: const Icon(Icons.send, color: Colors.white, size: 16),
                onPressed: _sendMessage,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
