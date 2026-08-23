import 'package:aaroha_app/core/constants.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ScamProtectionScreen extends StatefulWidget {
  final String userId;
  const ScamProtectionScreen({super.key, required this.userId});

  @override
  State<ScamProtectionScreen> createState() => _ScamProtectionScreenState();
}

class _ScamProtectionScreenState extends State<ScamProtectionScreen> {
  final TextEditingController _msgC = TextEditingController();
  bool _isLoading = false;
  Map<String, dynamic>? _scanResult;

  // Hardcoded security alerts
  final List<Map<String, dynamic>> _securityAlerts = [
    {
      "title": "Fake Utility Bill APKs",
      "desc":
          "Malicious SMS claims your electricity will be disconnected. Do not install any APK files.",
      "severity": "High",
      "date": "Today",
    },
    {
      "title": "Part-time Job YouTube Likes Scam",
      "desc":
          "Scammers offer money for liking YouTube videos, then ask for deposits to unlock higher tasks.",
      "severity": "Medium",
      "date": "2 days ago",
    },
  ];

  Future<void> _scanMessage() async {
    final text = _msgC.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _isLoading = true;
      _scanResult = null;
    });

    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/money/scam-scanner'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"user_id": widget.userId, "message_text": text}),
      );

      if (!mounted) return;

      if (response.statusCode == 200) {
        setState(() {
          _scanResult = jsonDecode(response.body);
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Error scanning: Code ${response.statusCode}"),
          ),
        );
      }
    } catch (e) {
      debugPrint("Scam scanner failed: $e");
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Unable to connect to safety server.")),
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
          "Scam & Fraud Shield",
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
              _buildScannerInputCard(),
              const SizedBox(height: 20),
              if (_scanResult != null) ...[
                _buildScanResultCard(),
                const SizedBox(height: 20),
              ],
              _buildSafetyGuidelines(),
              const SizedBox(height: 20),
              _buildSecurityAlertsStream(),
            ],
          ),
          if (_isLoading)
            const Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: LinearProgressIndicator(
                color: Colors.redAccent,
                backgroundColor: Colors.transparent,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildScannerInputCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.redAccent.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              Icon(Icons.shield, color: Colors.redAccent, size: 22),
              SizedBox(width: 8),
              Text(
                "AAROHA SAFETY SCANNER",
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
            "Paste suspicious messages, SMS alerts, lottery claims, or payment links to scan for scams.",
            style: TextStyle(color: Colors.white60, fontSize: 12),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _msgC,
            maxLines: 4,
            style: const TextStyle(color: Colors.white, fontSize: 13),
            decoration: InputDecoration(
              hintText:
                  "Example: 'Dear Customer, your electricity bill is unpaid. Please download this app link immediately...'",
              hintStyle: const TextStyle(color: Colors.white24, fontSize: 12),
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
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: const BorderSide(color: Colors.redAccent),
              ),
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _isLoading ? null : _scanMessage,
              icon: const Icon(Icons.security, size: 18),
              label: const Text(
                "Scan for Threats",
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.redAccent,
                foregroundColor: Colors.white,
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

  Widget _buildScanResultCard() {
    final verdict = _scanResult!["verdict"] ?? "Suspicious";
    final threatScore = _scanResult!["threat_score"] ?? 50;
    final scamType = _scanResult!["scam_type"] ?? "Unknown";
    final explanation = _scanResult!["explanation"] ?? "";
    final safetyTips = _scanResult!["safety_tips"] as List<dynamic>? ?? [];

    Color verdictColor;
    IconData verdictIcon;
    if (verdict == "Dangerous") {
      verdictColor = Colors.redAccent;
      verdictIcon = Icons.dangerous;
    } else if (verdict == "Suspicious") {
      verdictColor = Colors.orangeAccent;
      verdictIcon = Icons.warning_amber_rounded;
    } else {
      verdictColor = Colors.greenAccent;
      verdictIcon = Icons.check_circle_outline;
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: verdictColor.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(verdictIcon, color: verdictColor, size: 24),
                  const SizedBox(width: 8),
                  Text(
                    "$verdict Threat Found!",
                    style: TextStyle(
                      color: verdictColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: verdictColor.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  "Score: $threatScore%",
                  style: TextStyle(
                    color: verdictColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
          const Divider(color: Colors.white10, height: 24),
          Text(
            "Scam Category: $scamType",
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 13,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            explanation,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 12,
              height: 1.4,
            ),
          ),
          if (safetyTips.isNotEmpty) ...[
            const SizedBox(height: 16),
            const Text(
              "AI Recommended Actions:",
              style: TextStyle(
                color: Colors.tealAccent,
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 8),
            ...safetyTips.map(
              (tip) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(
                      Icons.gpp_maybe,
                      color: Colors.tealAccent,
                      size: 16,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        tip.toString(),
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 11,
                          height: 1.3,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSafetyGuidelines() {
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
          const Text(
            "UPI & QR CODE SAFETY MANUAL",
            style: TextStyle(
              color: Colors.white70,
              fontWeight: FontWeight.bold,
              fontSize: 12,
              letterSpacing: 1.1,
            ),
          ),
          const SizedBox(height: 12),
          _buildGuidelineRow(
            Icons.pin_drop,
            "No PIN for Receiving Money",
            "Receiving money NEVER requires entering your UPI PIN. If someone asks you to enter your PIN or scan a QR code to receive cash, it is a scam.",
          ),
          const Divider(color: Colors.white10, height: 16),
          _buildGuidelineRow(
            Icons.qr_code_scanner,
            "Verify QR Details",
            "When scanning a QR code, always verify the merchant name displayed on the payment screen before hitting pay.",
          ),
          const Divider(color: Colors.white10, height: 16),
          _buildGuidelineRow(
            Icons.link_off,
            "Avoid Strange Links",
            "Do not download apps from unknown links sent on WhatsApp or SMS. Always use Google Play Store or Apple App Store.",
          ),
        ],
      ),
    );
  }

  Widget _buildGuidelineRow(IconData icon, String title, String desc) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        CircleAvatar(
          radius: 16,
          backgroundColor: Colors.teal.withValues(alpha: 0.15),
          child: Icon(icon, color: Colors.tealAccent, size: 16),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                desc,
                style: const TextStyle(
                  color: Colors.white60,
                  fontSize: 11,
                  height: 1.3,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildSecurityAlertsStream() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "LOCAL SAFETY ALERTS",
          style: TextStyle(
            color: Colors.white70,
            fontWeight: FontWeight.bold,
            fontSize: 12,
            letterSpacing: 1.1,
          ),
        ),
        const SizedBox(height: 10),
        ..._securityAlerts.map(
          (alert) => Card(
            color: const Color(0xFF1E293B),
            margin: const EdgeInsets.symmetric(vertical: 6),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
            child: ListTile(
              leading: Icon(
                Icons.report_problem,
                color: alert["severity"] == "High"
                    ? Colors.redAccent
                    : Colors.orangeAccent,
              ),
              title: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    alert["title"],
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                    ),
                  ),
                  Text(
                    alert["date"],
                    style: const TextStyle(color: Colors.white38, fontSize: 10),
                  ),
                ],
              ),
              subtitle: Padding(
                padding: const EdgeInsets.only(top: 6.0),
                child: Text(
                  alert["desc"],
                  style: const TextStyle(
                    color: Colors.white60,
                    fontSize: 11,
                    height: 1.3,
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
