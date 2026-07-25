import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:aaroha_app/core/constants.dart';

class JobHubScreen extends StatefulWidget {
  final String userId;
  const JobHubScreen({super.key, required this.userId});

  @override
  State<JobHubScreen> createState() => _JobHubScreenState();
}

class _JobHubScreenState extends State<JobHubScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool _isLoadingMatches = false;
  List<dynamic> _matchedJobs = [];

  final List<Map<String, String>> _applications = [
    {
      "company": "Google",
      "role": "Data Analyst Intern",
      "status": "Interviewing",
      "deadline": "2026-08-01",
    },
    {
      "company": "Meta",
      "role": "Junior Data Scientist",
      "status": "Applied",
      "deadline": "2026-07-28",
    },
    {
      "company": "TCS",
      "role": "Software Developer",
      "status": "Offered",
      "deadline": "Completed",
    },
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _fetchJobMatches();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _fetchJobMatches() async {
    setState(() {
      _isLoadingMatches = true;
    });
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/career/jobs'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_id": widget.userId,
          "dream_job": "Data Science & Python developer",
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _matchedJobs = data['jobs'] ?? [];
        });
      }
    } catch (e) {
      debugPrint("Jobs failed: $e");
    } finally {
      if (mounted)
        setState(() {
          _isLoadingMatches = false;
        });
    }
  }

  void _addApplication(
    String company,
    String role,
    String status,
    String deadline,
  ) {
    setState(() {
      _applications.add({
        "company": company,
        "role": role,
        "status": status,
        "deadline": deadline,
      });
    });
  }

  void _moveStatus(int index, String newStatus) {
    setState(() {
      _applications[index]["status"] = newStatus;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "Job & Internship Hub",
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.purpleAccent,
          unselectedLabelColor: Colors.white60,
          indicatorColor: Colors.purpleAccent,
          tabs: const [
            Tab(icon: Icon(Icons.auto_awesome), text: "AI Recommendations"),
            Tab(icon: Icon(Icons.dashboard), text: "Kanban Board"),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [_buildRecommendationsTab(), _buildKanbanTab()],
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: Colors.purpleAccent,
        onPressed: _showAddAppDialog,
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }

  Widget _buildRecommendationsTab() {
    if (_isLoadingMatches) {
      return const Center(
        child: CircularProgressIndicator(color: Colors.purpleAccent),
      );
    }
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const Text(
          "Matched Jobs for your Profile",
          style: TextStyle(
            color: Colors.white70,
            fontSize: 13,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        if (_matchedJobs.isEmpty)
          const Card(
            color: Color(0xFF1E293B),
            child: Padding(
              padding: EdgeInsets.all(16.0),
              child: Text(
                "No jobs found matching your current profile credentials.",
                style: TextStyle(color: Colors.white70),
              ),
            ),
          )
        else
          ..._matchedJobs.map(
            (job) => Card(
              color: const Color(0xFF1E293B),
              margin: const EdgeInsets.only(bottom: 12),
              child: ListTile(
                leading: const Icon(Icons.business, color: Colors.purpleAccent),
                title: Text(
                  job['title'],
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                subtitle: Text(
                  "${job['company']} • Match: ${job['match_reason']}",
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                ),
                trailing: TextButton(
                  onPressed: () {
                    _addApplication(
                      job['company'],
                      job['title'],
                      "Applied",
                      job['deadline'] ?? "Immediate",
                    );
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text("Added to Kanban Board!")),
                    );
                  },
                  child: const Text(
                    "Track",
                    style: TextStyle(color: Colors.purpleAccent, fontSize: 12),
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildKanbanTab() {
    final statuses = ["Applied", "Interviewing", "Offered", "Declined"];
    return ListView(
      padding: const EdgeInsets.all(16),
      children: statuses.map((status) {
        final filteredApps = _applications
            .where((app) => app["status"] == status)
            .toList();
        return ExpansionTile(
          initiallyExpanded: true,
          iconColor: Colors.purpleAccent,
          collapsedIconColor: Colors.white70,
          textColor: Colors.purpleAccent,
          title: Text(
            "$status (${filteredApps.length})",
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 15,
            ),
          ),
          children: filteredApps.map((app) {
            final origIndex = _applications.indexOf(app);
            return Card(
              color: const Color(0xFF1E293B),
              margin: const EdgeInsets.symmetric(vertical: 6, horizontal: 16),
              child: ListTile(
                title: Text(
                  app["role"]!,
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                subtitle: Text(
                  "${app["company"]} • Deadline: ${app["deadline"]}",
                  style: const TextStyle(color: Colors.white70, fontSize: 11),
                ),
                trailing: PopupMenuButton<String>(
                  icon: const Icon(
                    Icons.more_vert,
                    color: Colors.white70,
                    size: 20,
                  ),
                  onSelected: (newVal) => _moveStatus(origIndex, newVal),
                  itemBuilder: (context) => statuses
                      .where((s) => s != status)
                      .map(
                        (s) => PopupMenuItem(
                          value: s,
                          child: Text(
                            "Move to $s",
                            style: const TextStyle(fontSize: 13),
                          ),
                        ),
                      )
                      .toList(),
                ),
              ),
            );
          }).toList(),
        );
      }).toList(),
    );
  }

  void _showAddAppDialog() {
    final companyC = TextEditingController();
    final roleC = TextEditingController();
    final deadlineC = TextEditingController();
    String selectedStatus = "Applied";

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          "Track Application",
          style: TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: companyC,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(
                  labelText: "Company",
                  labelStyle: TextStyle(color: Colors.white70),
                ),
              ),
              TextField(
                controller: roleC,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(
                  labelText: "Role Title",
                  labelStyle: TextStyle(color: Colors.white70),
                ),
              ),
              TextField(
                controller: deadlineC,
                style: const TextStyle(color: Colors.white),
                decoration: const InputDecoration(
                  labelText: "Deadline (YYYY-MM-DD)",
                  labelStyle: TextStyle(color: Colors.white70),
                ),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: selectedStatus,
                dropdownColor: const Color(0xFF1E293B),
                decoration: const InputDecoration(
                  labelText: "Status",
                  labelStyle: TextStyle(color: Colors.white70),
                ),
                items: ["Applied", "Interviewing", "Offered", "Declined"]
                    .map(
                      (s) => DropdownMenuItem(
                        value: s,
                        child: Text(
                          s,
                          style: const TextStyle(color: Colors.white),
                        ),
                      ),
                    )
                    .toList(),
                onChanged: (v) => selectedStatus = v!,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Cancel"),
          ),
          ElevatedButton(
            onPressed: () {
              if (companyC.text.isNotEmpty && roleC.text.isNotEmpty) {
                _addApplication(
                  companyC.text,
                  roleC.text,
                  selectedStatus,
                  deadlineC.text,
                );
                Navigator.pop(context);
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.purpleAccent,
            ),
            child: const Text("Add", style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }
}
