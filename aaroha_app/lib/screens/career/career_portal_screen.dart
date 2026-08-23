import 'package:flutter/material.dart';
import 'package:aaroha_app/screens/career/career_profile_screen.dart';
import 'package:aaroha_app/screens/career/document_hub_screen.dart';
import 'package:aaroha_app/screens/career/resume_builder_screen.dart';
import 'package:aaroha_app/screens/career/skill_gap_screen.dart';
import 'package:aaroha_app/screens/career/job_hub_screen.dart';
import 'package:aaroha_app/screens/career/interview_coach_screen.dart';
import 'package:aaroha_app/screens/career/portfolio_mentor_screen.dart';
import 'package:aaroha_app/screens/career/career_quest_screen.dart';

class CareerPortalScreen extends StatefulWidget {
  final String userId;
  const CareerPortalScreen({super.key, required this.userId});

  @override
  State<CareerPortalScreen> createState() => _CareerPortalScreenState();
}

class _CareerPortalScreenState extends State<CareerPortalScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A), // Slate 900
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B), // Slate 800
        title: const Text(
          "Career Brain Matrix",
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          labelColor: Colors.purpleAccent,
          unselectedLabelColor: Colors.white60,
          indicatorColor: Colors.purpleAccent,
          tabs: const [
            Tab(icon: Icon(Icons.dashboard), text: "Dashboard"),
            Tab(icon: Icon(Icons.folder_shared), text: "Vault & Profile"),
            Tab(icon: Icon(Icons.trending_up), text: "Skills & Resume"),
            Tab(icon: Icon(Icons.work), text: "Jobs & Coach"),
          ],
        ),
      ),
      body: SafeArea(
        child: TabBarView(
          controller: _tabController,
          children: [
            _buildDashboardTab(),
            _buildVaultProfileTab(),
            _buildSkillsResumeTab(),
            _buildJobsCoachTab(),
          ],
        ),
      ),
    );
  }

  Widget _buildDashboardTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "CAREER READINESS COGNITION",
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
                colors: [Color(0xFF3B0764), Color(0xFF1E1B4B)],
              ),
              borderRadius: BorderRadius.circular(15),
              border: Border.all(color: Colors.purpleAccent.withOpacity(0.2)),
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          "Readiness Score (Simulated Baseline)",
                          style: TextStyle(color: Colors.white70, fontSize: 12),
                        ),
                        SizedBox(height: 6),
                        Text(
                          "88 / 100",
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    SizedBox(
                      height: 50,
                      width: 50,
                      child: CircularProgressIndicator(
                        value: 0.88,
                        backgroundColor: Colors.white10,
                        valueColor: const AlwaysStoppedAnimation<Color>(
                          Colors.purpleAccent,
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
                        "Resume Score: 85%",
                        style: TextStyle(color: Colors.white70, fontSize: 13),
                      ),
                    ),
                    Flexible(
                      child: Text(
                        "Apps Tracked: 3",
                        style: TextStyle(color: Colors.white70, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "CAREER QUESTS",
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
              TextButton(
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) =>
                        CareerQuestScreen(userId: widget.userId),
                  ),
                ),
                child: const Text(
                  "Open Quests",
                  style: TextStyle(color: Colors.purpleAccent),
                ),
              ),
            ],
          ),
          _buildQuestProgressCard(),
          const SizedBox(height: 24),

          const Text(
            "AI TWIN PERSPECTIVE",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),
          _buildTwinNudgeCard(),
        ],
      ),
    );
  }

  Widget _buildQuestProgressCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
        children: [
          Row(
            children: [
              const Icon(Icons.military_tech, color: Colors.amber, size: 36),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "Current Level: 3",
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    LinearProgressIndicator(
                      value: 0.6,
                      color: Colors.amber,
                      backgroundColor: Colors.white12,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              const Text(
                "350/500 XP",
                style: TextStyle(
                  color: Colors.amber,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Row(
            children: [
              Icon(
                Icons.check_circle_outline,
                color: Colors.greenAccent,
                size: 18,
              ),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  "Daily Quest: Complete mock interview",
                  style: TextStyle(color: Colors.white70, fontSize: 12),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTwinNudgeCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1B4B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.indigoAccent.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.psychology, color: Colors.indigoAccent),
              SizedBox(width: 8),
              Text(
                "Proactive Suggestion",
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Text(
            "\"Shash, based on your target 'Senior Data Scientist' role, you have a 15% skill gap in Python Deep Learning libraries.\"",
            style: TextStyle(
              color: Colors.white70,
              fontSize: 13,
              height: 1.4,
              fontStyle: FontStyle.italic,
            ),
          ),
          const SizedBox(height: 12),
          Align(
            alignment: Alignment.centerRight,
            child: ElevatedButton(
              onPressed: () {
                _tabController.animateTo(2);
              },
              style: ElevatedButton.styleFrom(backgroundColor: Colors.indigo),
              child: const Text(
                "Bridge Gap",
                style: TextStyle(color: Colors.white),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVaultProfileTab() {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        _buildListTile(
          "1. AI Career Profile",
          "Education, Skills, Goals, and baseline resume records.",
          Icons.account_circle,
          Colors.purpleAccent,
          () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => CareerProfileScreen(userId: widget.userId),
            ),
          ),
        ),
        const SizedBox(height: 12),
        _buildListTile(
          "2. Smart Career Vault",
          "Resumes, Certificates, and Offer Letters organized by AI.",
          Icons.folder_shared,
          Colors.tealAccent,
          () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => DocumentHubScreen(userId: widget.userId),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSkillsResumeTab() {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        _buildListTile(
          "3. AI Resume Optimizer",
          "Optimize ATS score, draft customized cover letters.",
          Icons.description,
          Colors.indigoAccent,
          () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => ResumeBuilderScreen(userId: widget.userId),
            ),
          ),
        ),
        const SizedBox(height: 12),
        _buildListTile(
          "4. Skill Gap Analysis",
          "Compare your profile with a job and find suggested studies.",
          Icons.trending_up,
          Colors.amberAccent,
          () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => SkillGapScreen(userId: widget.userId),
            ),
          ),
        ),
        const SizedBox(height: 12),
        _buildListTile(
          "7. Project & Portfolio Mentor",
          "Get project ideas and portfolio checklist updates.",
          Icons.integration_instructions,
          Colors.lightBlueAccent,
          () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) =>
                  PortfolioMentorScreen(userId: widget.userId),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildJobsCoachTab() {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        _buildListTile(
          "5. Job & Internship Hub",
          "Track applications via Kanban, match roles.",
          Icons.work,
          Colors.greenAccent,
          () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => JobHubScreen(userId: widget.userId),
            ),
          ),
        ),
        const SizedBox(height: 12),
        _buildListTile(
          "6. AI Interview Coach",
          "Simulated technical/HR interview chat with feedback scores.",
          Icons.forum,
          Colors.pinkAccent,
          () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => InterviewCoachScreen(userId: widget.userId),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildListTile(
    String title,
    String desc,
    IconData icon,
    Color accentColor,
    VoidCallback onTap,
  ) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.white.withOpacity(0.05)),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: accentColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(icon, color: accentColor),
        ),
        title: Text(
          title,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 6.0),
          child: Text(
            desc,
            style: const TextStyle(color: Colors.white54, fontSize: 12),
          ),
        ),
        trailing: const Icon(
          Icons.arrow_forward_ios,
          color: Colors.white30,
          size: 16,
        ),
        onTap: onTap,
      ),
    );
  }
}
