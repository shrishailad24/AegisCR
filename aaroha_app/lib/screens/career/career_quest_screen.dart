import 'package:flutter/material.dart';

class CareerQuestScreen extends StatefulWidget {
  final String userId;
  const CareerQuestScreen({super.key, required this.userId});

  @override
  State<CareerQuestScreen> createState() => _CareerQuestScreenState();
}

class _CareerQuestScreenState extends State<CareerQuestScreen> {
  int _xp = 350;
  int _level = 3;
  final int _streak = 5;

  final List<Map<String, dynamic>> _quests = [
    {"title": "Draft a cover letter for Meta", "xp": 50, "completed": false},
    {
      "title": "Add Python Certification to Profile",
      "xp": 40,
      "completed": false,
    },
    {"title": "Take a 5-question technical quiz", "xp": 60, "completed": true},
    {
      "title": "Check ATS Match Score on a target job",
      "xp": 30,
      "completed": false,
    },
  ];

  final List<Map<String, String>> _badges = [
    {
      "name": "ATS Solver",
      "desc": "Checked first ATS Resume alignment.",
      "icon": "🎖️",
    },
    {
      "name": "Interview Pro",
      "desc": "Scored >80 in Mock interview.",
      "icon": "🛡️",
    },
    {"name": "Organized Mind", "desc": "Uploaded 3 vault files.", "icon": "📁"},
  ];

  void _completeQuest(int index) {
    if (_quests[index]["completed"]) return;
    setState(() {
      _quests[index]["completed"] = true;
      _xp += _quests[index]["xp"] as int;
      if (_xp >= 500) {
        _xp -= 500;
        _level += 1;
        _showLevelUpDialog();
      }
    });
  }

  void _showLevelUpDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1E1B4B),
        title: const Row(
          children: [
            Icon(Icons.military_tech, color: Colors.amber, size: 28),
            SizedBox(width: 8),
            Text(
              "LEVEL UP!",
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        content: Text(
          "Congratulations Shash! You have advanced to Career Level $_level!",
          style: const TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Awesome", style: TextStyle(color: Colors.amber)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "Career Quests Hub",
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
            // Level & XP Dashboard card
            _buildStatsHeader(),
            const SizedBox(height: 24),

            // Daily Quests
            const Text(
              "🚀 DAILY QUEST CHALLENGES",
              style: TextStyle(
                color: Colors.white70,
                fontSize: 12,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.2,
              ),
            ),
            const SizedBox(height: 12),
            ...List.generate(_quests.length, (index) {
              final quest = _quests[index];
              return Card(
                color: const Color(0xFF1E293B),
                margin: const EdgeInsets.only(bottom: 10),
                child: ListTile(
                  leading: Checkbox(
                    value: quest["completed"],
                    activeColor: Colors.purpleAccent,
                    onChanged: (val) {
                      if (val == true) _completeQuest(index);
                    },
                  ),
                  title: Text(
                    quest["title"],
                    style: TextStyle(
                      color: Colors.white,
                      decoration: quest["completed"]
                          ? TextDecoration.lineThrough
                          : null,
                    ),
                  ),
                  subtitle: Text(
                    "+${quest["xp"]} XP reward",
                    style: const TextStyle(color: Colors.amber, fontSize: 11),
                  ),
                ),
              );
            }),
            const SizedBox(height: 24),

            // Badges section
            const Text(
              "🏅 UNLOCKED RECOGNITION BADGES",
              style: TextStyle(
                color: Colors.white70,
                fontSize: 12,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.2,
              ),
            ),
            const SizedBox(height: 12),
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _badges.length,
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 3,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: 0.8,
              ),
              itemBuilder: (context, index) {
                final badge = _badges[index];
                return Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E293B),
                    borderRadius: BorderRadius.circular(15),
                    border: Border.all(
                      color: Colors.purpleAccent.withValues(alpha: 0.1),
                    ),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        badge["icon"]!,
                        style: const TextStyle(fontSize: 32),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        badge["name"]!,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        badge["desc"]!,
                        style: const TextStyle(
                          color: Colors.white38,
                          fontSize: 9,
                        ),
                        textAlign: TextAlign.center,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF3B0764), Color(0xFF1E1B4B)],
        ),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Current XP Level",
                    style: TextStyle(color: Colors.white60, fontSize: 12),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    "Level $_level",
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  const Text(
                    "Learning Streak",
                    style: TextStyle(color: Colors.white60, fontSize: 12),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      const Icon(
                        Icons.local_fire_department,
                        color: Colors.orange,
                        size: 24,
                      ),
                      Text(
                        "$_streak Days",
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          LinearProgressIndicator(
            value: _xp / 500.0,
            color: Colors.amber,
            backgroundColor: Colors.white12,
            minHeight: 10,
          ),
          const SizedBox(height: 8),
          Text(
            "$_xp / 500 XP to next level",
            style: const TextStyle(color: Colors.white70, fontSize: 12),
          ),
        ],
      ),
    );
  }
}
