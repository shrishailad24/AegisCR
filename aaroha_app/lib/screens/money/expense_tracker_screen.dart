import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:math' as math;
import 'package:aaroha_app/core/constants.dart';

class ExpenseTrackerScreen extends StatefulWidget {
  final String userId;
  const ExpenseTrackerScreen({super.key, required this.userId});

  @override
  State<ExpenseTrackerScreen> createState() => _ExpenseTrackerScreenState();
}

class _ExpenseTrackerScreenState extends State<ExpenseTrackerScreen> {
  bool _isLoading = false;

  final List<Map<String, dynamic>> _transactions = [
    {
      "desc": "Weekly Groceries",
      "amount": 2300,
      "category": "Food",
      "type": "Expense",
    },
    {
      "desc": "Appartment Rent",
      "amount": 15000,
      "category": "Rent",
      "type": "Expense",
    },
    {
      "desc": "Internet Broadband",
      "amount": 999,
      "category": "Bills",
      "type": "Expense",
    },
    {
      "desc": "Movie Night out",
      "amount": 1200,
      "category": "Entertainment",
      "type": "Expense",
    },
    {
      "desc": "Office Cab Booking",
      "amount": 450,
      "category": "Travel",
      "type": "Expense",
    },
    {
      "desc": "Consulting Freelance",
      "amount": 8000,
      "category": "Side Income",
      "type": "Income",
    },
  ];

  final TextEditingController _descC = TextEditingController();
  final TextEditingController _amountC = TextEditingController();
  String _category = "Food";

  String _monthlyReport = "";

  final Map<String, int> _categoryLimits = {
    "Food": 5000,
    "Rent": 20000,
    "Bills": 3000,
    "Travel": 4000,
    "Entertainment": 5000,
  };

  Future<void> _generateMonthlyReport() async {
    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/money/advisor'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "question":
              "Perform a comprehensive monthly expense categorization report on these transactions, flagging category spending trends and cost savings recommendation.",
          "transactions": _transactions,
        }),
      );

      if (!mounted) return;

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _monthlyReport = data["answer"] ?? "";
        });
      }
    } catch (e) {
      debugPrint("Monthly report failed: $e");
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  void _addTransaction() {
    final amt = int.tryParse(_amountC.text) ?? 0;
    if (_descC.text.trim().isEmpty || amt <= 0) return;

    setState(() {
      _transactions.add({
        "desc": _descC.text.trim(),
        "amount": amt,
        "category": _category,
        "type": "Expense",
      });
      _descC.clear();
      _amountC.clear();
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Transaction categorized & logged!")),
    );
  }

  @override
  Widget build(BuildContext context) {
    int totalExpense = _transactions
        .where((t) => t["type"] == "Expense")
        .fold(0, (sum, item) => sum + (item["amount"] as int));

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "Smart Expense Tracker",
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
      ),
      body: Stack(
        children: [
          ListView(
            padding: const EdgeInsets.all(20),
            children: [
              _buildAggregatesCard(totalExpense),
              const SizedBox(height: 20),
              _buildBudgetAlerts(),
              const SizedBox(height: 20),
              _buildSpendingTrendsCard(),
              const SizedBox(height: 20),
              _buildAddTransactionForm(),
              const SizedBox(height: 20),
              _buildTransactionsList(),
              const SizedBox(height: 20),
              _buildAIReportCard(),
            ],
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

  Widget _buildAggregatesCard(int total) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.cyanAccent.withOpacity(0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "TOTAL EXPENSES THIS MONTH",
            style: TextStyle(
              color: Colors.white38,
              fontSize: 10,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            "₹$total",
            style: const TextStyle(
              color: Colors.white,
              fontSize: 28,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            "Category Breakdown:",
            style: TextStyle(color: Colors.white70, fontSize: 12),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _buildCategoryPill("Food", Colors.amberAccent),
              _buildCategoryPill("Rent", Colors.blueAccent),
              _buildCategoryPill("Bills", Colors.redAccent),
              _buildCategoryPill("Travel", Colors.tealAccent),
              _buildCategoryPill("Entertainment", Colors.purpleAccent),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryPill(String name, Color color) {
    int totalCategory = _transactions
        .where((t) => t["category"] == name)
        .fold(0, (sum, item) => sum + (item["amount"] as int));
    if (totalCategory == 0) return const SizedBox.shrink();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Text(
        "$name: ₹$totalCategory",
        style: TextStyle(
          color: color,
          fontSize: 10,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildBudgetAlerts() {
    List<Widget> alerts = [];

    _categoryLimits.forEach((cat, limit) {
      int spent = _transactions
          .where((t) => t["category"] == cat && t["type"] == "Expense")
          .fold(0, (sum, item) => sum + (item["amount"] as int));

      if (spent >= limit) {
        alerts.add(
          Padding(
            padding: const EdgeInsets.only(top: 6.0),
            child: Text(
              "🚨 $cat Limit Exceeded! (₹$spent/₹$limit)",
              style: const TextStyle(
                color: Colors.redAccent,
                fontSize: 11,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        );
      } else if (spent >= limit * 0.8) {
        alerts.add(
          Padding(
            padding: const EdgeInsets.only(top: 6.0),
            child: Text(
              "⚠️ $cat near limit (₹$spent/₹$limit)",
              style: const TextStyle(
                color: Colors.orangeAccent,
                fontSize: 11,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        );
      }
    });

    if (alerts.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.withOpacity(0.08),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.redAccent.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "BUDGET HEALTH ALERTS",
            style: TextStyle(
              color: Colors.redAccent,
              fontSize: 11,
              fontWeight: FontWeight.bold,
            ),
          ),
          ...alerts,
        ],
      ),
    );
  }

  Widget _buildSpendingTrendsCard() {
    List<String> categories = ["Food", "Rent", "Bills", "Travel", "Ent"];
    List<double> values = categories.map((cat) {
      String catFull = cat == "Ent" ? "Entertainment" : cat;
      return _transactions
          .where((t) => t["category"] == catFull && t["type"] == "Expense")
          .fold(0.0, (sum, item) => sum + (item["amount"] as num).toDouble());
    }).toList();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.white.withOpacity(0.05)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "SPENDING TRENDS",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 11,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 20),
          SizedBox(
            height: 120,
            width: double.infinity,
            child: CustomPaint(
              painter: _CategoryTrendsPainter(categories, values),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAddTransactionForm() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "LOG TRANSACTION",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _descC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Description",
              labelStyle: TextStyle(color: Colors.white60),
            ),
          ),
          TextField(
            controller: _amountC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Amount (₹)",
              labelStyle: TextStyle(color: Colors.white60),
            ),
            keyboardType: TextInputType.number,
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            value: _category,
            dropdownColor: const Color(0xFF1E293B),
            decoration: const InputDecoration(
              labelText: "Category",
              labelStyle: TextStyle(color: Colors.white60),
            ),
            items:
                [
                      "Food",
                      "Rent",
                      "Bills",
                      "Entertainment",
                      "Travel",
                      "Miscellaneous",
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
            child: ElevatedButton(
              onPressed: _addTransaction,
              style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
              child: const Text(
                "Add & Categorize",
                style: TextStyle(color: Colors.white),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTransactionsList() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "TRANSACTION LOG",
          style: TextStyle(
            color: Colors.white70,
            fontSize: 12,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.2,
          ),
        ),
        const SizedBox(height: 12),
        ..._transactions.reversed.map(
          (t) => Card(
            color: const Color(0xFF1E293B),
            margin: const EdgeInsets.only(bottom: 8),
            child: ListTile(
              leading: Icon(
                t["type"] == "Income"
                    ? Icons.add_circle_outline
                    : Icons.remove_circle_outline,
                color: t["type"] == "Income"
                    ? Colors.greenAccent
                    : Colors.redAccent,
                size: 20,
              ),
              title: Text(
                t["desc"],
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              subtitle: Text(
                t["category"],
                style: const TextStyle(color: Colors.white60, fontSize: 11),
              ),
              trailing: Text(
                "₹${t["amount"]}",
                style: TextStyle(
                  color: t["type"] == "Income"
                      ? Colors.greenAccent
                      : Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildAIReportCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.green.withOpacity(0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Flexible(
                child: Text(
                  "AI MONTHLY REPORT",
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                  ),
                ),
              ),
              ElevatedButton(
                onPressed: _generateMonthlyReport,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.teal,
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                ),
                child: const Text(
                  "Generate",
                  style: TextStyle(fontSize: 11, color: Colors.white),
                ),
              ),
            ],
          ),
          if (_monthlyReport.isNotEmpty) ...[
            const Divider(color: Colors.white10, height: 24),
            Text(
              _monthlyReport,
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 12,
                height: 1.4,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _CategoryTrendsPainter extends CustomPainter {
  final List<String> categories;
  final List<double> values;

  _CategoryTrendsPainter(this.categories, this.values);

  @override
  void paint(Canvas canvas, Size size) {
    double maxVal = values.fold(0.0, (m, v) => math.max(m, v));
    if (maxVal == 0) maxVal = 1000;

    final double barWidth = size.width / (categories.length * 1.8);
    final double spacing =
        (size.width - (barWidth * categories.length)) / (categories.length + 1);

    for (int i = 0; i < categories.length; i++) {
      final double x = spacing + i * (barWidth + spacing);
      final double barHeight = (values[i] / maxVal) * (size.height - 30);
      final double y = size.height - 20 - barHeight;

      final rect = Rect.fromLTWH(x, y, barWidth, barHeight);
      final paint = Paint()
        ..shader = LinearGradient(
          colors: [Colors.cyanAccent, Colors.cyan.shade700],
          begin: Alignment.bottomCenter,
          end: Alignment.topCenter,
        ).createShader(rect)
        ..style = PaintingStyle.fill;

      canvas.drawRRect(
        RRect.fromRectAndRadius(rect, const Radius.circular(4)),
        paint,
      );

      final labelSpan = TextSpan(
        text: categories[i],
        style: const TextStyle(color: Colors.white38, fontSize: 8),
      );
      final labelPainter = TextPainter(
        text: labelSpan,
        textDirection: TextDirection.ltr,
      );
      labelPainter.layout();
      labelPainter.paint(
        canvas,
        Offset(x + (barWidth / 2) - (labelPainter.width / 2), size.height - 14),
      );
    }
  }

  @override
  bool shouldRepaint(covariant _CategoryTrendsPainter oldDelegate) {
    return oldDelegate.values != values || oldDelegate.categories != categories;
  }
}
