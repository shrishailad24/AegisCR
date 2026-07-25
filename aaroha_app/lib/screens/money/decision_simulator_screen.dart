import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class DecisionSimulatorScreen extends StatefulWidget {
  final String userId;
  const DecisionSimulatorScreen({super.key, required this.userId});

  @override
  State<DecisionSimulatorScreen> createState() =>
      _DecisionSimulatorScreenState();
}

class _FocusMetric extends StatelessWidget {
  final String label;
  final String val;
  final IconData icon;
  final Color color;

  const _FocusMetric({
    required this.label,
    required this.val,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: color, size: 28),
        const SizedBox(height: 6),
        Text(
          val,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 15,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: const TextStyle(color: Colors.white38, fontSize: 10),
        ),
      ],
    );
  }
}

class _DecisionSimulatorScreenState extends State<DecisionSimulatorScreen> {
  final TextEditingController _itemC = TextEditingController(
    text: "MacBook Pro M4",
  );
  final TextEditingController _priceC = TextEditingController(text: "145000");
  String _category = "Electronics";

  bool _isLoading = false;
  Map<String, dynamic>? _simulationResult;

  Future<void> _runSimulation() async {
    final price = int.tryParse(_priceC.text) ?? 0;
    if (_itemC.text.trim().isEmpty || price <= 0) return;

    setState(() {
      _isLoading = true;
      _simulationResult = null;
    });

    final String baseUrl = kIsWeb
        ? 'http://localhost:8002'
        : 'http://10.0.2.2:8002';
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/money/decision-simulator'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "item_name": _itemC.text.trim(),
          "price": price,
          "category": _category,
        }),
      );

      if (!mounted) return;

      if (response.statusCode == 200) {
        setState(() {
          _simulationResult = jsonDecode(response.body);
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Simulation failed: Code ${response.statusCode}"),
          ),
        );
      }
    } catch (e) {
      debugPrint("Decision simulator failed: $e");
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("Unable to connect to Simulator server."),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
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
          "Decision Simulator",
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
              _buildInputCard(),
              const SizedBox(height: 24),
              if (_simulationResult != null) _buildSimulationDashboard(),
            ],
          ),
          if (_isLoading)
            const Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: LinearProgressIndicator(
                color: Colors.orangeAccent,
                backgroundColor: Colors.transparent,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildInputCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.orangeAccent.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              Icon(Icons.psychology, color: Colors.orangeAccent, size: 22),
              SizedBox(width: 8),
              Text(
                "WHAT HAPPENS IF I BUY THIS TODAY?",
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                  letterSpacing: 1.1,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            "Simulate the direct impact of major transactions on your active savings targets, emergency reserves, and delay times.",
            style: TextStyle(color: Colors.white60, fontSize: 12),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _itemC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Purchase Item (e.g. Laptop, Trip)",
              labelStyle: TextStyle(color: Colors.white60),
              enabledBorder: UnderlineInputBorder(
                borderSide: BorderSide(color: Colors.white12),
              ),
            ),
          ),
          TextField(
            controller: _priceC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Price Amount (₹)",
              labelStyle: TextStyle(color: Colors.white60),
              enabledBorder: UnderlineInputBorder(
                borderSide: BorderSide(color: Colors.white12),
              ),
            ),
            keyboardType: TextInputType.number,
          ),
          DropdownButtonFormField<String>(
            initialValue: _category,
            dropdownColor: const Color(0xFF1E293B),
            decoration: const InputDecoration(
              labelText: "Category",
              labelStyle: TextStyle(color: Colors.white60),
              enabledBorder: UnderlineInputBorder(
                borderSide: BorderSide(color: Colors.white12),
              ),
            ),
            items:
                [
                      "Electronics",
                      "Vacation",
                      "Vehicles",
                      "Luxury",
                      "Investment",
                      "Uncategorized",
                    ]
                    .map(
                      (cat) => DropdownMenuItem(
                        value: cat,
                        child: Text(
                          cat,
                          style: const TextStyle(color: Colors.white),
                        ),
                      ),
                    )
                    .toList(),
            onChanged: (val) => setState(() => _category = val!),
          ),
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _isLoading ? null : _runSimulation,
              icon: const Icon(Icons.flash_on, size: 18),
              label: const Text(
                "Simulate Financial Impact",
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.orangeAccent,
                foregroundColor: Colors.black,
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSimulationDashboard() {
    final res = _simulationResult!;
    final isSafe = res["emergency_fund"].toString().toLowerCase() == "safe";
    final savingsAfter = res["savings_after"] ?? 0;
    final recommendation = res["recommendation"] ?? "";

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1E293B), Color(0xFF0F172A)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.orangeAccent.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.bar_chart, color: Colors.orangeAccent),
              const SizedBox(width: 8),
              Text(
                "SIMULATION METRICS: ${res["item"]}",
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
            ],
          ),
          const Divider(color: Colors.white10, height: 24),

          // Key metrics row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _FocusMetric(
                label: "Est Savings Left",
                val: "₹$savingsAfter",
                icon: Icons.account_balance_wallet,
                color: Colors.blueAccent,
              ),
              _FocusMetric(
                label: "Emergency Fund",
                val: isSafe ? "Safe" : "Compromised",
                icon: isSafe ? Icons.gpp_good : Icons.gpp_maybe,
                color: isSafe ? Colors.greenAccent : Colors.redAccent,
              ),
            ],
          ),
          const Divider(color: Colors.white10, height: 24),

          // Goal impact list
          const Text(
            "🎯 GOAL IMPACT ANALYSIS:",
            style: TextStyle(
              color: Colors.orangeAccent,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          if (res["goal_impacts"] != null &&
              (res["goal_impacts"] as List).isNotEmpty)
            ...(res["goal_impacts"] as List).map(
              (gi) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4.0),
                child: Row(
                  children: [
                    const Icon(
                      Icons.arrow_right,
                      color: Colors.orangeAccent,
                      size: 16,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        gi.toString(),
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 12,
                          height: 1.3,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            )
          else
            const Text(
              "No goal impacts recorded.",
              style: TextStyle(color: Colors.white38, fontSize: 11),
            ),
          const SizedBox(height: 20),

          // Suggested Alternatives
          const Text(
            "💡 SUGGESTED ALTERNATIVES:",
            style: TextStyle(
              color: Colors.tealAccent,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          if (res["alternatives"] != null &&
              (res["alternatives"] as List).isNotEmpty)
            ...(res["alternatives"] as List).map(
              (alt) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4.0),
                child: Row(
                  children: [
                    const Icon(
                      Icons.lightbulb_outline,
                      color: Colors.tealAccent,
                      size: 16,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        alt.toString(),
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 12,
                          height: 1.3,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            )
          else
            const Text(
              "No alternatives suggested.",
              style: TextStyle(color: Colors.white38, fontSize: 11),
            ),
          const SizedBox(height: 20),

          // Final suggestion box
          Container(
            padding: const EdgeInsets.all(16),
            width: double.infinity,
            decoration: BoxDecoration(
              color: Colors.green.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: Colors.green.withValues(alpha: 0.2)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: const [
                    Icon(
                      Icons.assistant_navigation,
                      color: Colors.greenAccent,
                      size: 18,
                    ),
                    SizedBox(width: 6),
                    Text(
                      "AI Recommendation:",
                      style: TextStyle(
                        color: Colors.greenAccent,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  recommendation,
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 12,
                    height: 1.4,
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
