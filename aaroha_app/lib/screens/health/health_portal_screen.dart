import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
import 'package:aaroha_app/core/constants.dart';

class HealthPortalScreen extends StatefulWidget {
  final String userId;
  const HealthPortalScreen({super.key, required this.userId});

  @override
  State<HealthPortalScreen> createState() => _HealthPortalScreenState();
}

class _HealthPortalScreenState extends State<HealthPortalScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  // Health Profile controllers
  final _ageC = TextEditingController(text: "24");
  final _heightC = TextEditingController(text: "175");
  final _weightC = TextEditingController(text: "70");
  final _goalsC = TextEditingController(text: "Weight loss, Consistent sleep");

  bool _isLoading = false;

  // Trackers counters
  int _steps = 6200;
  int _waterMl = 1250;
  double _sleepHours = 6.5;
  int _exerciseMins = 20;
  String _selectedMood = "😐"; // 😢 | 😐 | 🙂 | 😄

  // Breathing animation states
  String _breathingText = "Ready to start breathing exercise?";
  int _breathingSecs = 0;
  Timer? _breathingTimer;

  // SOS state
  bool _sosTriggered = false;

  // AI Wellness Coach states
  final _wellnessQC = TextEditingController(
    text: "How can I reduce stress during exam season?",
  );
  String _wellnessResponse = "Ask the AI wellness coach for lifestyle tips.";
  List<dynamic> _wellnessTips = [];

  // Reminders list
  final List<Map<String, dynamic>> _reminders = [
    {"name": "Vitamins (After Lunch)", "time": "14:00 PM", "done": false},
    {"name": "Water Alert (Hydrate)", "time": "Every 2 Hours", "done": true},
    {
      "name": "Cardiologist Appointment",
      "time": "July 20, 11:00 AM",
      "done": false,
    },
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadHealthProfile();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _breathingTimer?.cancel();
    super.dispose();
  }

  // Load Health Profile
  Future<void> _loadHealthProfile() async {
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health/health-profile/${widget.userId}'),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data.containsKey("age")) {
          setState(() {
            _ageC.text = data["age"].toString();
            _heightC.text = data["height"].toString();
            _weightC.text = data["weight"].toString();
            _goalsC.text = (data["goals"] as List).join(", ");
          });
        }
      }
    } catch (e) {
      debugPrint("Load health failed: $e");
    }
  }

  // Save Health Profile
  Future<void> _saveHealthProfile() async {
    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      List<String> splitList(String text) => text
          .split(',')
          .map((e) => e.trim())
          .where((e) => e.isNotEmpty)
          .toList();
      final response = await http.post(
        Uri.parse('$baseUrl/health/health-profile'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "age": int.tryParse(_ageC.text) ?? 0,
          "height": int.tryParse(_heightC.text) ?? 0,
          "weight": int.tryParse(_weightC.text) ?? 0,
          "allergies": [],
          "conditions": [],
          "goals": splitList(_goalsC.text),
        }),
      );
      if (response.statusCode == 200) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text("Health Profile Saved!")),
          );
        }
      }
    } catch (e) {
      debugPrint("Save health failed: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  // AI Wellness Coach Call
  Future<void> _queryWellnessCoach() async {
    if (_wellnessQC.text.trim().isEmpty) return;
    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/health/wellness'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "steps": _steps,
          "water_ml": _waterMl,
          "sleep_hours": _sleepHours,
          "exercise_mins": _exerciseMins,
          "mood": _selectedMood,
        }),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _wellnessResponse = "Evaluate Complete.";
          _wellnessTips = data["tips"] ?? [];
        });
      }
    } catch (e) {
      debugPrint("Wellness coach failed: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _startBreathingCycle() {
    _breathingTimer?.cancel();
    setState(() {
      _breathingSecs = 15;
    });

    _breathingTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_breathingSecs > 10) {
        setState(
          () =>
              _breathingText = "🌬️ Inhale deeply... (${_breathingSecs - 10}s)",
        );
      } else if (_breathingSecs > 5) {
        setState(
          () => _breathingText = "🧘 Hold breath... (${_breathingSecs - 5}s)",
        );
      } else if (_breathingSecs > 0) {
        setState(
          () => _breathingText = "💨 Exhale slowly... (${_breathingSecs}s)",
        );
      } else {
        setState(() {
          _breathingText = "Excellent work! Feel relaxed.";
          _breathingTimer?.cancel();
        });
      }
      setState(() {
        if (_breathingSecs > 0) _breathingSecs--;
      });
    });
  }

  void _triggerSOS() {
    setState(() {
      _sosTriggered = true;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
          "🚨 SOS CRITICAL ALERT SENT! Local Authorities & Family Notified.",
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        backgroundColor: Colors.redAccent,
        duration: Duration(seconds: 4),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    int score =
        ((_steps / 8000.0 * 30) +
                (_waterMl / 3000.0 * 30) +
                (_sleepHours / 8.0 * 40))
            .toInt()
            .clamp(0, 100);

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "Health Brain Portal",
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          labelColor: Colors.pinkAccent,
          unselectedLabelColor: Colors.white60,
          indicatorColor: Colors.pinkAccent,
          tabs: const [
            Tab(icon: Icon(Icons.favorite), text: "Wellness Score"),
            Tab(icon: Icon(Icons.directions_walk), text: "Trackers & Profile"),
            Tab(icon: Icon(Icons.notifications), text: "Reminders & Mind"),
            Tab(icon: Icon(Icons.health_and_safety), text: "Emergency Hub"),
          ],
        ),
      ),
      body: SafeArea(
        child: Stack(
          children: [
            TabBarView(
              controller: _tabController,
              children: [
                _buildWellnessScoreTab(score),
                _buildTrackersTab(),
                _buildRemindersMindTab(),
                _buildEmergencyTab(),
              ],
            ),
            if (_isLoading)
              const Positioned(
                top: 0,
                left: 0,
                right: 0,
                child: LinearProgressIndicator(
                  color: Colors.pinkAccent,
                  backgroundColor: Colors.transparent,
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildWellnessScoreTab(int score) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "OVERALL WELLNESS COGNITION",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF831843), Color(0xFF0F172A)],
              ),
              borderRadius: BorderRadius.circular(15),
              border: Border.all(color: Colors.pinkAccent.withOpacity(0.2)),
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            "Wellness score",
                            style: TextStyle(
                              color: Colors.white70,
                              fontSize: 14,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            "$score / 100",
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                    SizedBox(
                      height: 50,
                      width: 50,
                      child: CircularProgressIndicator(
                        value: score / 100.0,
                        backgroundColor: Colors.white10,
                        valueColor: const AlwaysStoppedAnimation<Color>(
                          Colors.pinkAccent,
                        ),
                        strokeWidth: 6,
                      ),
                    ),
                  ],
                ),
                const Divider(color: Colors.white10, height: 24),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Flexible(
                      child: Text(
                        "Streak: 4 Days 🏃",
                        style: TextStyle(
                          color: Colors.greenAccent,
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    Flexible(
                      child: Text(
                        "Mood: Excellent",
                        style: TextStyle(color: Colors.white70, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          const Text(
            "AI HEALTH TWIN AUDIT",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(15),
              border: Border.all(color: Colors.pinkAccent.withOpacity(0.2)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const [
                Row(
                  children: [
                    Icon(Icons.psychology, color: Colors.pinkAccent),
                    SizedBox(width: 8),
                    Text(
                      "AI Health Twin Advice",
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 12),
                Text(
                  "\"Shash, your sleep duration has fallen below target. Try reading a book instead of browsing files before bed!\"",
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 13,
                    height: 1.4,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTrackersTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "1. MEDICAL GENOME",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _ageC,
            keyboardType: TextInputType.number,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Age",
              labelStyle: TextStyle(color: Colors.white60),
            ),
          ),
          TextField(
            controller: _heightC,
            keyboardType: TextInputType.number,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Height (cm)",
              labelStyle: TextStyle(color: Colors.white60),
            ),
          ),
          TextField(
            controller: _weightC,
            keyboardType: TextInputType.number,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Weight (kg)",
              labelStyle: TextStyle(color: Colors.white60),
            ),
          ),
          TextField(
            controller: _goalsC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Health Goals",
              labelStyle: TextStyle(color: Colors.white60),
            ),
          ),
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _saveHealthProfile,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.pinkAccent,
              ),
              child: const Text(
                "Commit Health Profile",
                style: TextStyle(color: Colors.white),
              ),
            ),
          ),
          const Divider(height: 40, color: Colors.white10),

          const Text(
            "2. DAILY TRACKERS",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),

          _buildTrackerCounter(
            "Steps",
            "$_steps / 8000",
            Icons.directions_walk,
            Colors.greenAccent,
            () {
              setState(() => _steps += 1000);
            },
          ),
          const SizedBox(height: 10),
          _buildTrackerCounter(
            "Water",
            "$_waterMl / 3000 ml",
            Icons.local_drink,
            Colors.blueAccent,
            () {
              setState(() => _waterMl += 250);
            },
          ),
          const SizedBox(height: 10),
          _buildTrackerCounter(
            "Sleep",
            "$_sleepHours / 8 hrs",
            Icons.bedtime,
            Colors.amberAccent,
            () {
              setState(() => _sleepHours = (_sleepHours + 0.5).clamp(0, 24));
            },
          ),
          const SizedBox(height: 10),
          _buildTrackerCounter(
            "Exercise",
            "$_exerciseMins mins",
            Icons.fitness_center,
            Colors.pinkAccent,
            () {
              setState(() => _exerciseMins += 10);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildTrackerCounter(
    String name,
    String value,
    IconData icon,
    Color color,
    VoidCallback onAdd,
  ) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Row(
              children: [
                Icon(icon, color: color),
                const SizedBox(width: 12),
                Flexible(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        name,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        value,
                        style: const TextStyle(
                          color: Colors.white60,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          ElevatedButton(
            onPressed: onAdd,
            style: ElevatedButton.styleFrom(
              backgroundColor: color,
              foregroundColor: Colors.black,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              minimumSize: const Size(60, 36),
            ),
            child: const Text("Log +", style: TextStyle(fontSize: 12)),
          ),
        ],
      ),
    );
  }

  Widget _buildRemindersMindTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "3. SMART REMINDERS",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          ..._reminders.map(
            (rem) => Card(
              color: const Color(0xFF1E293B),
              child: CheckboxListTile(
                title: Text(
                  rem["name"],
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                    decoration: rem["done"] ? TextDecoration.lineThrough : null,
                  ),
                ),
                subtitle: Text(
                  "Time: ${rem["time"]}",
                  style: const TextStyle(color: Colors.white60, fontSize: 11),
                ),
                value: rem["done"],
                activeColor: Colors.pinkAccent,
                onChanged: (val) {
                  setState(() => rem["done"] = val!);
                },
              ),
            ),
          ),
          const Divider(height: 40, color: Colors.white10),

          const Text(
            "5. MENTAL WELLNESS",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: ["😢", "😐", "🙂", "😄"]
                .map(
                  (emoji) => InkWell(
                    onTap: () {
                      setState(() => _selectedMood = emoji);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text("Logged mood: $emoji")),
                      );
                    },
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: _selectedMood == emoji
                            ? Colors.pinkAccent.withOpacity(0.3)
                            : Colors.white10,
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: _selectedMood == emoji
                              ? Colors.pinkAccent
                              : Colors.transparent,
                        ),
                      ),
                      child: Text(emoji, style: const TextStyle(fontSize: 24)),
                    ),
                  ),
                )
                .toList(),
          ),
          const SizedBox(height: 24),

          const Text(
            "VISUAL BREATHING EXERCISE",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(15),
            ),
            child: Column(
              children: [
                Text(
                  _breathingText,
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: _startBreathingCycle,
                  child: const Text("Start 15s Cycle"),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmergencyTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_sosTriggered) ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              margin: const EdgeInsets.only(bottom: 20),
              decoration: BoxDecoration(
                color: Colors.red.withOpacity(0.2),
                borderRadius: BorderRadius.circular(15),
                border: Border.all(color: Colors.redAccent),
              ),
              child: Row(
                children: const [
                  Icon(Icons.warning, color: Colors.redAccent),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      "🚨 ACTIVE EMERGENCY ALERT: SOS broadcasted.",
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
          const Text(
            "7. EMERGENCY MEDICAL CARD",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: Colors.redAccent.withOpacity(0.3)),
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: const [
                    Flexible(
                      child: Text(
                        "Blood Group: O+",
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ),
                    Icon(Icons.bloodtype, color: Colors.redAccent, size: 28),
                  ],
                ),
                const Divider(color: Colors.white10),
                const ListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text(
                    "Allergies",
                    style: TextStyle(color: Colors.white60, fontSize: 12),
                  ),
                  subtitle: Text(
                    "Peanuts, Penicillin",
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ),
                const ListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text(
                    "Emergency Contacts",
                    style: TextStyle(color: Colors.white60, fontSize: 12),
                  ),
                  subtitle: Text(
                    "Dad: +91 98765 43210",
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton.icon(
                    onPressed: _triggerSOS,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.redAccent,
                      foregroundColor: Colors.white,
                    ),
                    icon: const Icon(Icons.emergency),
                    label: const Text(
                      "TRIGGER CRITICAL SOS",
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 40, color: Colors.white10),

          const Text(
            "4. AI WELLNESS COACH",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _wellnessQC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Ask wellness advisor...",
              labelStyle: TextStyle(color: Colors.pinkAccent),
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _queryWellnessCoach,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.pinkAccent,
              ),
              child: const Text(
                "Consult Wellness Coach",
                style: TextStyle(color: Colors.white),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            _wellnessResponse,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 13,
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(height: 8),
          if (_wellnessTips.isNotEmpty) ...[
            ..._wellnessTips.map(
              (tip) => Card(
                color: const Color(0xFF1E293B),
                child: ListTile(
                  leading: const Icon(
                    Icons.check,
                    color: Colors.pinkAccent,
                    size: 16,
                  ),
                  title: Text(
                    tip.toString(),
                    style: const TextStyle(color: Colors.white, fontSize: 12),
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
