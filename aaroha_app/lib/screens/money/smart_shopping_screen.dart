import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class SmartShoppingScreen extends StatefulWidget {
  final String userId;
  const SmartShoppingScreen({super.key, required this.userId});

  @override
  State<SmartShoppingScreen> createState() => _SmartShoppingScreenState();
}

class _SmartShoppingScreenState extends State<SmartShoppingScreen> {
  final TextEditingController _productC = TextEditingController(
    text: "MacBook Pro M4",
  );
  bool _isLoading = false;
  Map<String, dynamic>? _shopResult;

  // Local Wishlist data for tracking
  final List<Map<String, dynamic>> _wishlist = [
    {
      "name": "Sony WH-1000XM5",
      "targetPrice": 22000,
      "currentPrice": 24999,
      "status": "Wait",
    },
    {
      "name": "iPhone 15 Pro",
      "targetPrice": 110000,
      "currentPrice": 112000,
      "status": "Buy",
    },
  ];

  // Savings Calculator state
  double _savingsSliderVal = 10; // 10% discount expectation
  double _originalPrice = 145000;

  Future<void> _analyzeProduct() async {
    final name = _productC.text.trim();
    if (name.isEmpty) return;

    setState(() {
      _isLoading = true;
      _shopResult = null;
    });

    final String baseUrl = kIsWeb
        ? 'http://localhost:8002'
        : 'http://10.0.2.2:8002';
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/money/smart-shopping'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"user_id": widget.userId, "product_name": name}),
      );

      if (!mounted) return;

      if (response.statusCode == 200) {
        setState(() {
          _shopResult = jsonDecode(response.body);
          if (_shopResult != null && _shopResult!["current_average"] != null) {
            _originalPrice = (_shopResult!["current_average"] as num)
                .toDouble();
          }
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              "Error fetching price details: Code ${response.statusCode}",
            ),
          ),
        );
      }
    } catch (e) {
      debugPrint("Smart shopping price analysis failed: $e");
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("Unable to connect to Smart Shopping backend."),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  void _addToWishlist() {
    if (_productC.text.trim().isEmpty) return;
    setState(() {
      final curPrice =
          _shopResult != null && _shopResult!["current_average"] != null
          ? _shopResult!["current_average"] as int
          : 12000;
      _wishlist.add({
        "name": _productC.text.trim(),
        "targetPrice": (curPrice * 0.9).toInt(),
        "currentPrice": curPrice,
        "status": _shopResult?["buy_or_wait"] ?? "Wait",
      });
    });
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text("Added to Wishlist Tracker!")));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "AI Smart Shopping",
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
              const SizedBox(height: 20),
              if (_shopResult != null) ...[
                _buildAnalysisResultCard(),
                const SizedBox(height: 20),
                _buildSavingsCalculator(),
                const SizedBox(height: 20),
              ],
              _buildWishlistTracker(),
            ],
          ),
          if (_isLoading)
            const Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: LinearProgressIndicator(
                color: Colors.tealAccent,
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
        border: Border.all(color: Colors.tealAccent.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              Icon(Icons.shopping_bag, color: Colors.tealAccent, size: 22),
              SizedBox(width: 8),
              Text(
                "PRICE TRACKER & SHOPPING AI",
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
            "Enter product name to track multi-store pricing, historical charts, festival sale predictions, and cashback tips.",
            style: TextStyle(color: Colors.white60, fontSize: 12),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _productC,
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                  decoration: InputDecoration(
                    hintText: "Product Name (e.g. iPad Air)",
                    hintStyle: const TextStyle(color: Colors.white24),
                    filled: true,
                    fillColor: const Color(0xFF0F172A),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                      borderSide: BorderSide(
                        color: Colors.white.withValues(alpha: 0.1),
                      ),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                      borderSide: BorderSide(
                        color: Colors.white.withValues(alpha: 0.1),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _isLoading ? null : _analyzeProduct,
                  icon: const Icon(Icons.troubleshoot, size: 18),
                  label: const Text(
                    "Analyze Prices",
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.teal,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              IconButton(
                onPressed: _addToWishlist,
                icon: const Icon(Icons.bookmark_add, color: Colors.tealAccent),
                style: IconButton.styleFrom(
                  backgroundColor: const Color(0xFF0F172A),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                    side: BorderSide(
                      color: Colors.tealAccent.withValues(alpha: 0.3),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAnalysisResultCard() {
    final product = _shopResult!["product"] ?? "";
    final currentAvg = _shopResult!["current_average"] ?? 0;
    final prediction = _shopResult!["prediction"] ?? "";
    final buyOrWait = _shopResult!["buy_or_wait"] ?? "Wait";
    final stores = _shopResult!["stores"] as List<dynamic>? ?? [];
    final priceHistory = _shopResult!["price_history"] as List<dynamic>? ?? [];

    final isBuy = buyOrWait.toString().toLowerCase() == "buy";

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.white.withValues(alpha: 0.05)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  product,
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: isBuy
                      ? Colors.green.withValues(alpha: 0.15)
                      : Colors.amber.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    Icon(
                      isBuy ? Icons.check_circle : Icons.hourglass_empty,
                      color: isBuy ? Colors.greenAccent : Colors.amberAccent,
                      size: 14,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      isBuy ? "Buy Now" : "Wait",
                      style: TextStyle(
                        color: isBuy ? Colors.greenAccent : Colors.amberAccent,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            "Current Average: ₹$currentAvg",
            style: const TextStyle(
              color: Colors.tealAccent,
              fontWeight: FontWeight.bold,
              fontSize: 14,
            ),
          ),
          const Divider(color: Colors.white10, height: 24),

          // Price drop alert
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.teal.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.teal.withValues(alpha: 0.2)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.campaign, color: Colors.tealAccent, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "Festival Sale Prediction",
                        style: TextStyle(
                          color: Colors.tealAccent,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        prediction,
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 11,
                          height: 1.4,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Custom Painter for Price History Chart
          const Text(
            "PRICE TREND HISTORY",
            style: TextStyle(
              color: Colors.white54,
              fontSize: 11,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Container(
            height: 100,
            width: double.infinity,
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: const Color(0xFF0F172A),
              borderRadius: BorderRadius.circular(10),
            ),
            child: CustomPaint(
              painter: _PriceHistoryPainter(
                priceHistory.map((e) => (e as num).toDouble()).toList(),
              ),
            ),
          ),
          const SizedBox(height: 20),

          // Multi-store Comparison
          const Text(
            "MULTI-STORE COMPARISON",
            style: TextStyle(
              color: Colors.white54,
              fontSize: 11,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          ...stores.map((store) {
            final storeName = store["name"] ?? "";
            final price = store["price"] ?? 0;
            final coupon = store["coupon"] ?? "";

            return Card(
              color: const Color(0xFF0F172A),
              margin: const EdgeInsets.symmetric(vertical: 4),
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: Colors.white.withValues(alpha: 0.05),
                  child: Text(
                    storeName.substring(0, 1),
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                title: Text(
                  storeName,
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                  ),
                ),
                subtitle: coupon.toString().isNotEmpty
                    ? Container(
                        margin: const EdgeInsets.only(top: 4),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.green.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          "Coupon: $coupon",
                          style: const TextStyle(
                            color: Colors.greenAccent,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      )
                    : null,
                trailing: Text(
                  "₹$price",
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                  ),
                ),
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildSavingsCalculator() {
    final expectedPrice = _originalPrice * (1 - (_savingsSliderVal / 100));
    final savings = _originalPrice - expectedPrice;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.tealAccent.withValues(alpha: 0.1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "SAVINGS CALCULATOR",
            style: TextStyle(
              color: Colors.white70,
              fontWeight: FontWeight.bold,
              fontSize: 12,
              letterSpacing: 1.1,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            "Adjust slider to simulate a festival discount (e.g. 5% to 20% savings)",
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.5),
              fontSize: 11,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "Target Discount: ${_savingsSliderVal.toInt()}%",
                style: const TextStyle(
                  color: Colors.tealAccent,
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
              Text(
                "Estimated Savings: ₹${savings.toInt()}",
                style: const TextStyle(
                  color: Colors.greenAccent,
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
            ],
          ),
          Slider(
            value: _savingsSliderVal,
            min: 5,
            max: 30,
            divisions: 5,
            activeColor: Colors.tealAccent,
            inactiveColor: Colors.white10,
            onChanged: (val) {
              setState(() {
                _savingsSliderVal = val;
              });
            },
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "Original Price: ₹${_originalPrice.toInt()}",
                style: const TextStyle(color: Colors.white54, fontSize: 11),
              ),
              Text(
                "New Price: ₹${expectedPrice.toInt()}",
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildWishlistTracker() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "WISHLIST PRICE TRACKER",
          style: TextStyle(
            color: Colors.white70,
            fontWeight: FontWeight.bold,
            fontSize: 12,
            letterSpacing: 1.1,
          ),
        ),
        const SizedBox(height: 10),
        ..._wishlist.map((item) {
          final isBuy = item["status"].toString().toLowerCase() == "buy";
          return Card(
            color: const Color(0xFF1E293B),
            margin: const EdgeInsets.symmetric(vertical: 6),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
            child: ListTile(
              leading: Icon(
                Icons.bookmark,
                color: isBuy ? Colors.greenAccent : Colors.amberAccent,
              ),
              title: Text(
                item["name"],
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
              subtitle: Text(
                "Target: ₹${item["targetPrice"]} • Current: ₹${item["currentPrice"]}",
                style: const TextStyle(color: Colors.white60, fontSize: 11),
              ),
              trailing: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: isBuy
                      ? Colors.green.withValues(alpha: 0.15)
                      : Colors.amber.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  isBuy ? "Affordable" : "Waiting for drop",
                  style: TextStyle(
                    color: isBuy ? Colors.greenAccent : Colors.amberAccent,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          );
        }),
      ],
    );
  }
}

// Custom Painter to draw Price History Graph
class _PriceHistoryPainter extends CustomPainter {
  final List<double> prices;
  _PriceHistoryPainter(this.prices);

  @override
  void paint(Canvas canvas, Size size) {
    if (prices.length < 2) return;

    final paint = Paint()
      ..color = Colors.tealAccent
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    final fillPaint = Paint()
      ..color = Colors.tealAccent.withValues(alpha: 0.1)
      ..style = PaintingStyle.fill;

    double maxVal = prices[0];
    double minVal = prices[0];
    for (var p in prices) {
      if (p > maxVal) maxVal = p;
      if (p < minVal) minVal = p;
    }

    if (maxVal == minVal) {
      maxVal += 1000;
      minVal -= 1000;
    }

    final double heightPad = size.height * 0.15;
    final double graphHeight = size.height - (heightPad * 2);
    final double stepWidth = size.width / (prices.length - 1);

    final path = Path();
    final fillPath = Path();

    // Map first point
    double getX(int idx) => idx * stepWidth;
    double getY(double val) =>
        size.height -
        heightPad -
        ((val - minVal) / (maxVal - minVal) * graphHeight);

    path.moveTo(getX(0), getY(prices[0]));
    fillPath.moveTo(getX(0), size.height);
    fillPath.lineTo(getX(0), getY(prices[0]));

    for (int i = 1; i < prices.length; i++) {
      path.lineTo(getX(i), getY(prices[i]));
      fillPath.lineTo(getX(i), getY(prices[i]));
    }

    fillPath.lineTo(getX(prices.length - 1), size.height);
    fillPath.close();

    canvas.drawPath(fillPath, fillPaint);
    canvas.drawPath(path, paint);

    // Draw circles and text labels
    for (int i = 0; i < prices.length; i++) {
      canvas.drawCircle(
        Offset(getX(i), getY(prices[i])),
        4,
        Paint()..color = Colors.tealAccent,
      );
      canvas.drawCircle(
        Offset(getX(i), getY(prices[i])),
        2,
        Paint()..color = const Color(0xFF0F172A),
      );

      // Draw price text above or below
      final textSpan = TextSpan(
        text: "₹${prices[i].toInt()}",
        style: const TextStyle(color: Colors.white38, fontSize: 8),
      );
      final textPainter = TextPainter(
        text: textSpan,
        textDirection: TextDirection.ltr,
      );
      textPainter.layout();
      textPainter.paint(
        canvas,
        Offset(getX(i) - (textPainter.width / 2), getY(prices[i]) - 14),
      );
    }
  }

  @override
  bool shouldRepaint(covariant _PriceHistoryPainter oldDelegate) {
    return oldDelegate.prices != prices;
  }
}
