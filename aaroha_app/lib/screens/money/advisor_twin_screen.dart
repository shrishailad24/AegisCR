import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:aaroha_app/core/constants.dart';

class AdvisorTwinScreen extends StatefulWidget {
  final String userId;
  const AdvisorTwinScreen({super.key, required this.userId});

  @override
  State<AdvisorTwinScreen> createState() => _AdvisorTwinScreenState();
}

class _AdvisorTwinScreenState extends State<AdvisorTwinScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool _isLoading = false;

  final TextEditingController _advisorQC = TextEditingController(
    text: "How much should I save every month to buy a laptop?",
  );
  String _advisorResponse = "Enter a question above and ask the AI advisor.";

  final TextEditingController _msgC = TextEditingController();
  final List<Map<String, String>> _messages = [
    {
      "role": "assistant",
      "content":
          "Hello Shash! I've synced with your financial genome. You've spent 85% of your food budget this week, and you have subscriptions renewing soon. How can I help you optimize your savings today?",
    },
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _askAdvisor() async {
    final text = _advisorQC.text.trim();
    if (text.isEmpty) return;

    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/money/advisor'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "question": text,
          "transactions": [],
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _advisorResponse = data["answer"] ?? "";
        });
      }
    } catch (e) {
      debugPrint("Advisor failed: $e");
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _sendTwinMessage() async {
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
        Uri.parse('$baseUrl/money/money-twin'),
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
      }
    } catch (e) {
      debugPrint("Twin failed: $e");
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
        title: const Text(
          "AI Money Brain",
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.greenAccent,
          unselectedLabelColor: Colors.white60,
          indicatorColor: Colors.greenAccent,
          tabs: const [
            Tab(icon: Icon(Icons.psychology), text: "Twin Chat"),
            Tab(icon: Icon(Icons.forum), text: "Advisor"),
          ],
        ),
      ),
      body: Stack(
        children: [
          TabBarView(
            controller: _tabController,
            children: [_buildTwinChatTab(), _buildAdvisorQnATab()],
          ),
          if (_isLoading)
            const Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: LinearProgressIndicator(
                color: Colors.greenAccent,
                backgroundColor: Colors.transparent,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildTwinChatTab() {
    return Column(
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
                        ? const Color(0xFF10B981)
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
                          : Colors.greenAccent.withOpacity(0.15),
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
        _buildChatInput(),
      ],
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
                  hintText: "Ask Money Twin...",
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
                onSubmitted: (_) => _sendTwinMessage(),
              ),
            ),
            const SizedBox(width: 8),
            CircleAvatar(
              radius: 20,
              backgroundColor: Colors.greenAccent,
              child: IconButton(
                icon: const Icon(Icons.send, color: Colors.black, size: 18),
                onPressed: _sendTwinMessage,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAdvisorQnATab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "QUICK FINANCIAL ADVICE",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 11,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _advisorQC,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              labelText: "Your Question",
              labelStyle: const TextStyle(color: Colors.white60),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Colors.white24),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Colors.greenAccent),
              ),
              filled: true,
              fillColor: const Color(0xFF1E293B),
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              onPressed: _askAdvisor,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Text(
                "Query Advisor",
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.all(20),
            width: double.infinity,
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(15),
              border: Border.all(color: Colors.greenAccent.withOpacity(0.1)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "Advisor Response:",
                  style: TextStyle(
                    color: Colors.greenAccent,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  _advisorResponse,
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 13,
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
