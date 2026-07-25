import 'dart:async';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class FocusModeScreen extends StatefulWidget {
  final String userId;
  const FocusModeScreen({super.key, required this.userId});

  @override
  State<FocusModeScreen> createState() => _FocusModeScreenState();
}

class _FocusModeScreenState extends State<FocusModeScreen> {
  // Timer States
  Timer? _timer;
  int _totalSeconds = 25 * 60; // Default 25 minutes
  int _secondsRemaining = 25 * 60;
  bool _isRunning = false;
  bool _isBreakTime = false;

  // Configuration
  int _focusDurationMins = 25;
  int _breakDurationMins = 5;
  String _selectedSound = "Lofi Beats";

  // Ambient sound list
  final List<String> _ambientSounds = [
    "Lofi Beats",
    "Rain Sounds",
    "White Noise",
    "Forest Ambience",
  ];

  // Focus history from API
  int _averageFocusScore = 0;
  int _totalFocusTimeMins = 0;

  @override
  void initState() {
    super.initState();
    _saveFocusSession(
      0,
      0,
    ); // Trigger fetch of history on startup (0 time/score)
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  // API Call: Save Focus Session & Fetch stats
  Future<void> _saveFocusSession(int duration, int score) async {
    final String baseUrl = kIsWeb
        ? 'http://localhost:8002'
        : 'http://10.0.2.2:8002';
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/education/focus-session'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "duration_mins": duration,
          "focus_score": score,
          "ambient_sound": _selectedSound,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _averageFocusScore = data["total_focus_score"] ?? 0;
          _totalFocusTimeMins = data["total_focus_time_mins"] ?? 0;
        });
      }
    } catch (e) {
      debugPrint("Focus session save failed: $e");
    }
  }

  void _toggleTimer() {
    if (_isRunning) {
      _timer?.cancel();
      setState(() => _isRunning = false);
    } else {
      setState(() => _isRunning = true);
      _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
        if (_secondsRemaining > 0) {
          setState(() {
            _secondsRemaining--;
          });
        } else {
          _timer?.cancel();
          _onTimerComplete();
        }
      });
    }
  }

  void _resetTimer() {
    _timer?.cancel();
    setState(() {
      _isRunning = false;
      _secondsRemaining =
          (_isBreakTime ? _breakDurationMins : _focusDurationMins) * 60;
    });
  }

  void _onTimerComplete() {
    if (!_isBreakTime) {
      // Completed Focus Session!
      _saveFocusSession(_focusDurationMins, 95); // Log session with 95 score
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            "Focus session complete! Logged 95 productivity score. Time for a break!",
          ),
        ),
      );
      setState(() {
        _isBreakTime = true;
        _secondsRemaining = _breakDurationMins * 60;
        _totalSeconds = _breakDurationMins * 60;
        _isRunning = false;
      });
    } else {
      // Completed Break Time
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Break time complete! Let's get back to focusing."),
        ),
      );
      setState(() {
        _isBreakTime = false;
        _secondsRemaining = _focusDurationMins * 60;
        _totalSeconds = _focusDurationMins * 60;
        _isRunning = false;
      });
    }
  }

  void _applyConfig() {
    _timer?.cancel();
    setState(() {
      _isRunning = false;
      _isBreakTime = false;
      _totalSeconds = _focusDurationMins * 60;
      _secondsRemaining = _focusDurationMins * 60;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Pomodoro configured successfully.")),
    );
  }

  String _formatTime(int totalSecs) {
    final mins = totalSecs ~/ 60;
    final secs = totalSecs % 60;
    return "${mins.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}";
  }

  @override
  Widget build(BuildContext context) {
    final double progress = _secondsRemaining / _totalSeconds;

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "Focus Mode & Pomodoro",
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // 1. DYNAMIC POMODORO VISUALIZER
          _buildTimerVisualizer(progress),
          const SizedBox(height: 24),

          // 2. FOCUS METRICS CARD
          _buildFocusMetricsCard(),
          const SizedBox(height: 24),

          // 3. SETTINGS & CONFIGURE
          _buildSettingsCard(),
        ],
      ),
    );
  }

  Widget _buildTimerVisualizer(double progress) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 36),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.purpleAccent.withValues(alpha: 0.1)),
      ),
      child: Column(
        children: [
          Text(
            _isBreakTime ? "BREAK TIME" : "FOCUSING MODE",
            style: TextStyle(
              color: _isBreakTime ? Colors.tealAccent : Colors.redAccent,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.5,
              fontSize: 13,
            ),
          ),
          const SizedBox(height: 24),
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 180,
                height: 180,
                child: CircularProgressIndicator(
                  value: progress,
                  strokeWidth: 10,
                  backgroundColor: Colors.white10,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    _isBreakTime ? Colors.tealAccent : Colors.redAccent,
                  ),
                ),
              ),
              Column(
                children: [
                  Text(
                    _formatTime(_secondsRemaining),
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 36,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.music_note, color: Colors.white30, size: 12),
                      const SizedBox(width: 4),
                      Text(
                        _selectedSound,
                        style: const TextStyle(
                          color: Colors.white30,
                          fontSize: 10,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              IconButton(
                icon: Icon(
                  _isRunning ? Icons.pause_circle : Icons.play_circle,
                  color: Colors.white,
                  size: 48,
                ),
                onPressed: _toggleTimer,
              ),
              const SizedBox(width: 20),
              IconButton(
                icon: const Icon(
                  Icons.replay_circle_filled,
                  color: Colors.white60,
                  size: 36,
                ),
                onPressed: _resetTimer,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildFocusMetricsCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          Column(
            children: [
              const Icon(Icons.timer, color: Colors.blueAccent),
              const SizedBox(height: 8),
              Text(
                "$_totalFocusTimeMins min",
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              const Text(
                "Total Study Time",
                style: TextStyle(color: Colors.white38, fontSize: 11),
              ),
            ],
          ),
          Column(
            children: [
              const Icon(Icons.favorite, color: Colors.redAccent),
              const SizedBox(height: 8),
              Text(
                "$_averageFocusScore/100",
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              const Text(
                "Avg Focus Score",
                style: TextStyle(color: Colors.white38, fontSize: 11),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSettingsCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "CONFIGURE MODE",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "Focus Duration:",
                style: TextStyle(color: Colors.white70),
              ),
              DropdownButton<int>(
                value: _focusDurationMins,
                dropdownColor: const Color(0xFF1E293B),
                style: const TextStyle(color: Colors.white),
                items: [15, 25, 45, 60]
                    .map(
                      (v) => DropdownMenuItem(value: v, child: Text("$v Mins")),
                    )
                    .toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _focusDurationMins = val);
                },
              ),
            ],
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "Break Duration:",
                style: TextStyle(color: Colors.white70),
              ),
              DropdownButton<int>(
                value: _breakDurationMins,
                dropdownColor: const Color(0xFF1E293B),
                style: const TextStyle(color: Colors.white),
                items: [3, 5, 10, 15]
                    .map(
                      (v) => DropdownMenuItem(value: v, child: Text("$v Mins")),
                    )
                    .toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _breakDurationMins = val);
                },
              ),
            ],
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "Ambient Sound:",
                style: TextStyle(color: Colors.white70),
              ),
              DropdownButton<String>(
                value: _selectedSound,
                dropdownColor: const Color(0xFF1E293B),
                style: const TextStyle(color: Colors.white),
                items: _ambientSounds
                    .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                    .toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _selectedSound = val);
                },
              ),
            ],
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _applyConfig,
            style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
            child: const Text(
              "Save Configuration",
              style: TextStyle(color: Colors.white),
            ),
          ),
        ],
      ),
    );
  }
}
