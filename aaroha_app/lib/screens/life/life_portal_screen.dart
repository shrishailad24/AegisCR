import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:aaroha_app/core/constants.dart';

class LifePortalScreen extends StatefulWidget {
  final String userId;
  const LifePortalScreen({super.key, required this.userId});

  @override
  State<LifePortalScreen> createState() => _LifePortalScreenState();
}

class _LifePortalScreenState extends State<LifePortalScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  // Personal Profile state
  final _nameC = TextEditingController(text: "Shash");
  final _prefC = TextEditingController(
    text: "Prefers remote work, High savings goal",
  );
  bool _isLoading = false;

  // Digital Locker documents mockup
  final List<Map<String, String>> _lockerDocs = [
    {"type": "Aadhaar Card", "number": "XXXX-XXXX-8912", "status": "Verified"},
    {"type": "PAN Card", "number": "ABCDE1234F", "status": "Verified"},
    {"type": "Passport", "number": "Z8912345", "status": "Expires 2032-12"},
    {
      "type": "Driving Licence",
      "number": "DL-1234567890",
      "status": "Expires 2029-05",
    },
  ];

  // Smart Planner checklist
  final List<Map<String, dynamic>> _tasks = [
    {"title": "Review career skill gap analysis", "completed": false},
    {"title": "Log dinner food transaction", "completed": false},
    {"title": "Do 15s visual breathing exercise", "completed": true},
    {"title": "Update PAN Card in Locker", "completed": false},
  ];

  // Government Scheme finder states
  final _ageC = TextEditingController(text: "24");
  final _stateC = TextEditingController(text: "Karnataka");
  final _incomeC = TextEditingController(text: "85000");
  List<dynamic> _govtSchemesList = [];

  // Travel Assistant states
  final _destC = TextEditingController(text: "Goa");
  final _daysC = TextEditingController(text: "3");
  List<dynamic> _packingChecklist = [];
  String _travelBudget = "";
  // List<dynamic> _itinerary = [];

  // Shopping Assistant states
  final List<String> _shoppingList = ["Fruit juices", "Gym resistance bands"];
  final _shopItemC = TextEditingController();

  // AI Daily Assistant states
  String _assistantBrief = "Generate today's morning briefing context.";
  List<dynamic> _briefTasks = [];
  int _prodScore = 75;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadLifeProfile();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  // Load Life Profile
  Future<void> _loadLifeProfile() async {
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/life/life-profile/${widget.userId}'),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data.containsKey("name")) {
          setState(() {
            _nameC.text = data["name"] ?? "";
            _prefC.text = (data["preferences"] as List).join(", ");
          });
        }
      }
    } catch (e) {
      debugPrint("Load life failed: $e");
    }
  }

  // Save Life Profile
  Future<void> _saveLifeProfile() async {
    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      List<String> splitList(String text) => text
          .split(',')
          .map((e) => e.trim())
          .where((e) => e.isNotEmpty)
          .toList();
      final response = await http.post(
        Uri.parse('$baseUrl/life/life-profile'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "name": _nameC.text,
          "emergency_contacts": [],
          "family_info": [],
          "preferences": splitList(_prefC.text),
        }),
      );
      if (response.statusCode == 200) {
        if (mounted) {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(const SnackBar(content: Text("Life Profile Saved!")));
        }
      }
    } catch (e) {
      debugPrint("Save life failed: $e");
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  // Call Daily Assistant
  Future<void> _fetchDailyBrief() async {
    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/life/daily-brief'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "question": "Fetch focus agenda.",
        }),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _assistantBrief = data["briefing"] ?? "";
          _briefTasks = data["tasks"] ?? [];
          _prodScore = data["productivity_score"] ?? 85;
        });
      }
    } catch (e) {
      debugPrint("Daily Assistant failed: $e");
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  // Call Govt Scheme Finder
  Future<void> _fetchGovtSchemes() async {
    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/life/govt-schemes'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "age": int.tryParse(_ageC.text) ?? 0,
          "state": _stateC.text,
          "income": int.tryParse(_incomeC.text) ?? 0,
        }),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _govtSchemesList = data["schemes"] ?? [];
        });
      }
    } catch (e) {
      debugPrint("Govt scheme failed: $e");
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  // Call Travel Planner
  Future<void> _planTravel() async {
    setState(() => _isLoading = true);
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/life/travel'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "destination": _destC.text.trim(),
          "duration_days": int.tryParse(_daysC.text) ?? 3,
        }),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _packingChecklist = data["packing_checklist"] ?? [];
          _travelBudget = data["budget_estimate"] ?? "";
          // _itinerary = data["itinerary_summary"] ?? [];
        });
      }
    } catch (e) {
      debugPrint("Travel planner failed: $e");
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _addShoppingItem(String item) {
    if (item.trim().isEmpty) return;
    setState(() {
      _shoppingList.add(item.trim());
      _shopItemC.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    int doneCount = _tasks.where((t) => t["completed"] == true).length;
    int calculatedScore = ((doneCount / _tasks.length) * 100).toInt();

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "Life Brain Portal",
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          labelColor: Colors.amberAccent,
          unselectedLabelColor: Colors.white60,
          indicatorColor: Colors.amberAccent,
          tabs: const [
            Tab(icon: Icon(Icons.dashboard_customize), text: "Daily Brief"),
            Tab(icon: Icon(Icons.calendar_today), text: "Planner & Profile"),
            Tab(icon: Icon(Icons.folder), text: "Locker & Govt"),
            Tab(icon: Icon(Icons.flight_takeoff), text: "Travel & Shopping"),
          ],
        ),
      ),
      body: SafeArea(
        child: Stack(
          children: [
            TabBarView(
              controller: _tabController,
              children: [
                _buildDailyBriefTab(calculatedScore),
                _buildPlannerTab(),
                _buildLockerGovtTab(),
                _buildTravelShoppingTab(),
              ],
            ),
            if (_isLoading)
              const Positioned(
                top: 0,
                left: 0,
                right: 0,
                child: LinearProgressIndicator(
                  color: Colors.amberAccent,
                  backgroundColor: Colors.transparent,
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildDailyBriefTab(int calcScore) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "DAILY PRODUCTIVITY MATRIX",
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
                colors: [Color(0xFF78350F), Color(0xFF0F172A)],
              ),
              borderRadius: BorderRadius.circular(15),
              border: Border.all(color: Colors.amberAccent.withOpacity(0.2)),
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
                            "Productivity Level",
                            style: TextStyle(
                              color: Colors.white70,
                              fontSize: 14,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            "$calcScore / 100",
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 24,
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
                        value: calcScore / 100.0,
                        backgroundColor: Colors.white10,
                        valueColor: const AlwaysStoppedAnimation<Color>(
                          Colors.amberAccent,
                        ),
                        strokeWidth: 6,
                      ),
                    ),
                  ],
                ),
                const Divider(color: Colors.white10, height: 24),
                Text(
                  "AI Productivity Score: $_prodScore 🔥",
                  style: const TextStyle(
                    color: Colors.amberAccent,
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Flexible(
                child: Text(
                  "AI DAILY BRIEFING",
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              ElevatedButton.icon(
                onPressed: _fetchDailyBrief,
                icon: const Icon(Icons.flash_on, size: 16),
                label: const Text("Brief", style: TextStyle(fontSize: 12)),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(15),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "Focus Agenda",
                  style: TextStyle(
                    color: Colors.amberAccent,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  _assistantBrief,
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 13,
                    height: 1.4,
                  ),
                ),
                if (_briefTasks.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  ..._briefTasks.map(
                    (t) => Padding(
                      padding: const EdgeInsets.only(bottom: 6.0),
                      child: Text(
                        "• $t",
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPlannerTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "1. PERSONAL IDENTITY",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _nameC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Full Name",
              labelStyle: TextStyle(color: Colors.white60),
            ),
          ),
          TextField(
            controller: _prefC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Preferences",
              labelStyle: TextStyle(color: Colors.white60),
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _saveLifeProfile,
              style: ElevatedButton.styleFrom(backgroundColor: Colors.amber),
              child: const Text(
                "Commit Profile",
                style: TextStyle(color: Colors.white),
              ),
            ),
          ),
          const Divider(height: 40, color: Colors.white10),

          const Text(
            "3. SMART PLANNER",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          ..._tasks.map(
            (task) => Card(
              color: const Color(0xFF1E293B),
              child: CheckboxListTile(
                title: Text(
                  task["title"],
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    decoration: task["completed"]
                        ? TextDecoration.lineThrough
                        : null,
                  ),
                ),
                value: task["completed"],
                activeColor: Colors.amber,
                onChanged: (val) {
                  setState(() => task["completed"] = val!);
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLockerGovtTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "2. DIGITAL VAULT",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          ..._lockerDocs.map(
            (doc) => Card(
              color: const Color(0xFF1E293B),
              child: ListTile(
                leading: const Icon(
                  Icons.file_present,
                  color: Colors.amberAccent,
                ),
                title: Text(
                  doc["type"]!,
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                subtitle: Text(
                  doc["number"]!,
                  style: const TextStyle(color: Colors.white60, fontSize: 11),
                ),
                trailing: Text(
                  doc["status"]!,
                  style: const TextStyle(
                    color: Colors.amberAccent,
                    fontSize: 10,
                  ),
                ),
              ),
            ),
          ),
          const Divider(height: 40, color: Colors.white10),

          const Text(
            "4. GOVT SCHEMES",
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
            controller: _stateC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "State",
              labelStyle: TextStyle(color: Colors.white60),
            ),
          ),
          TextField(
            controller: _incomeC,
            keyboardType: TextInputType.number,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Monthly Income",
              labelStyle: TextStyle(color: Colors.white60),
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _isLoading ? null : _fetchGovtSchemes,
              style: ElevatedButton.styleFrom(backgroundColor: Colors.amber),
              child: Text(
                _isLoading ? "Searching..." : "Search Schemes",
                style: const TextStyle(color: Colors.white),
              ),
            ),
          ),
          const SizedBox(height: 16),
          if (_govtSchemesList.isNotEmpty) ...[
            ..._govtSchemesList.map(
              (scheme) => Card(
                color: const Color(0xFF1E293B),
                child: ListTile(
                  title: Text(
                    scheme["name"],
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  subtitle: Text(
                    scheme["benefit"],
                    style: const TextStyle(color: Colors.white70, fontSize: 11),
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildTravelShoppingTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "5. TRAVEL ASSISTANT",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _destC,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Destination",
              labelStyle: TextStyle(color: Colors.white60),
            ),
          ),
          TextField(
            controller: _daysC,
            keyboardType: TextInputType.number,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "Duration (Days)",
              labelStyle: TextStyle(color: Colors.white60),
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _planTravel,
              style: ElevatedButton.styleFrom(backgroundColor: Colors.amber),
              child: const Text(
                "Plan Trip",
                style: TextStyle(color: Colors.white),
              ),
            ),
          ),
          const SizedBox(height: 16),
          if (_packingChecklist.isNotEmpty) ...[
            Text(
              "Budget: $_travelBudget",
              style: const TextStyle(
                color: Colors.amberAccent,
                fontWeight: FontWeight.bold,
                fontSize: 13,
              ),
            ),
            const SizedBox(height: 8),
            ..._packingChecklist
                .take(5)
                .map(
                  (item) => Text(
                    "• $item",
                    style: const TextStyle(color: Colors.white70, fontSize: 12),
                  ),
                ),
          ],
          const Divider(height: 40, color: Colors.white10),

          const Text(
            "6. SHOPPING MANAGER",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _shopItemC,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(
                    labelText: "Add item...",
                    labelStyle: TextStyle(color: Colors.white60),
                  ),
                  onSubmitted: _addShoppingItem,
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                onPressed: () => _addShoppingItem(_shopItemC.text),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                ),
                child: const Text("Add"),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ..._shoppingList.map(
            (item) => Card(
              color: const Color(0xFF1E293B),
              child: ListTile(
                leading: const Icon(
                  Icons.shopping_cart,
                  color: Colors.amberAccent,
                  size: 20,
                ),
                title: Text(
                  item,
                  style: const TextStyle(color: Colors.white, fontSize: 13),
                ),
                trailing: IconButton(
                  icon: const Icon(
                    Icons.delete,
                    color: Colors.redAccent,
                    size: 20,
                  ),
                  onPressed: () {
                    setState(() {
                      _shoppingList.remove(item);
                    });
                  },
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
