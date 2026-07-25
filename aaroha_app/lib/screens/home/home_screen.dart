import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:aaroha_app/screens/career/career_portal_screen.dart';
import 'package:aaroha_app/screens/education/education_portal_screen.dart';
import 'package:aaroha_app/screens/money/money_portal_screen.dart';
import 'package:aaroha_app/screens/health/health_portal_screen.dart';
import 'package:aaroha_app/screens/life/life_portal_screen.dart';
import 'package:aaroha_app/services/auth_service.dart';
import 'package:aaroha_app/screens/auth/login_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String _userId = 'test_user';
  String _userName = 'Shash';

  @override
  void initState() {
    super.initState();
    _loadUserSession();
  }

  Future<void> _loadUserSession() async {
    final user = AuthService.currentUser;
    if (user != null) {
      setState(() {
        _userId = user.uid;
        _userName =
            user.displayName ??
            (user.email != null ? user.email!.split('@')[0] : 'Explorer');
      });

      // Fetch dynamic profile data from Firestore
      try {
        final doc = await FirebaseFirestore.instance
            .collection('users')
            .doc(user.uid)
            .get();
        if (doc.exists && doc.data() != null) {
          final data = doc.data()!;
          if (data['name'] != null && (data['name'] as String).isNotEmpty) {
            setState(() {
              _userName = data['name'];
            });
          }
        }
      } catch (e) {
        debugPrint("Failed to fetch Firestore user name: $e");
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B0F19),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Colors.purpleAccent, Colors.blueAccent],
                ),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(
                Icons.psychology,
                color: Colors.white,
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            const Text(
              "AAROHA OS",
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 18,
                letterSpacing: 1.2,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(
              Icons.notifications_active,
              color: Colors.purpleAccent,
              size: 20,
            ),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.redAccent, size: 20),
            tooltip: "Logout Session",
            onPressed: () async {
              await AuthService.signOut();
              if (mounted) {
                Navigator.pushAndRemoveUntil(
                  context,
                  MaterialPageRoute(builder: (context) => const LoginScreen()),
                  (route) => false,
                );
              }
            },
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildGreetingBanner(),
              const SizedBox(height: 24),

              const Text(
                "LIVE OS INSIGHTS",
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 12),
              _buildLiveInsightsGrid(),
              const SizedBox(height: 28),

              const Text(
                "INTELLIGENT LIFE BRAINS",
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 12),
              _buildBrainsGrid(context),
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildGreetingBanner() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1E1E38), Color(0xFF151528)],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withOpacity(0.05)),
        boxShadow: [
          BoxShadow(
            color: Colors.purpleAccent.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "Welcome back, $_userName",
            style: const TextStyle(
              color: Colors.white,
              fontSize: 22,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            "\"One AI. Every Life Decision.\" All your contextual brains are synced and active.",
            style: TextStyle(color: Colors.white70, fontSize: 13, height: 1.4),
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 12,
            runSpacing: 8,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: Colors.purple.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: const [
                    Icon(Icons.flash_on, color: Colors.amber, size: 14),
                    SizedBox(width: 4),
                    Text(
                      "Level 3: Explorer",
                      style: TextStyle(
                        color: Colors.amber,
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: Colors.teal.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Text(
                  "Productivity: 92%",
                  style: TextStyle(
                    color: Colors.tealAccent,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildLiveInsightsGrid() {
    return LayoutBuilder(
      builder: (context, constraints) {
        return Row(
          children: [
            Expanded(
              child: _buildSmallStatCard(
                "ATS Match",
                "85%",
                Icons.trending_up,
                Colors.greenAccent,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildSmallStatCard(
                "Budget",
                "₹45,000",
                Icons.account_balance_wallet,
                Colors.cyanAccent,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildSmallStatCard(
                "Water",
                "1.8 L",
                Icons.local_drink,
                Colors.blueAccent,
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildSmallStatCard(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF131722),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.white.withOpacity(0.04)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 18),
          const SizedBox(height: 10),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: const TextStyle(color: Colors.white38, fontSize: 10),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  Widget _buildBrainsGrid(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        int crossAxisCount = constraints.maxWidth > 600 ? 3 : 2;
        return GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: crossAxisCount,
          childAspectRatio: 0.85,
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
          children: [
            _buildBrainCard(
              context,
              "Career Brain",
              "Build and grow your career with smart planning.",
              Icons.work,
              [Colors.purpleAccent, Colors.purple],
              "10 Features Live",
              () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => CareerPortalScreen(userId: _userId),
                ),
              ),
            ),
            _buildBrainCard(
              context,
              "Education Brain",
              "Learn smarter, solve doubts, generate tests.",
              Icons.school,
              [Colors.blueAccent, Colors.indigo],
              "8 Features Live",
              () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => EducationPortalScreen(userId: _userId),
                ),
              ),
            ),
            _buildBrainCard(
              context,
              "Money Brain",
              "Manage budgets, expenses, and AI advisory.",
              Icons.currency_rupee,
              [Colors.green, Colors.teal],
              "8 Features Live",
              () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => MoneyPortalScreen(userId: _userId),
                ),
              ),
            ),
            _buildBrainCard(
              context,
              "Health Brain",
              "Track steps, water, sleep, emergency card.",
              Icons.favorite,
              [Colors.pinkAccent, Colors.redAccent],
              "8 Features Live",
              () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => HealthPortalScreen(userId: _userId),
                ),
              ),
            ),
            _buildBrainCard(
              context,
              "Life Brain",
              "Civic schemes, travel, locker, planner.",
              Icons.home,
              [Colors.amber, Colors.orange],
              "8 Features Live",
              () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => LifePortalScreen(userId: _userId),
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildBrainCard(
    BuildContext context,
    String title,
    String desc,
    IconData icon,
    List<Color> gradientColors,
    String tag,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF131722),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: Colors.white.withOpacity(0.05)),
          boxShadow: [
            BoxShadow(
              color: gradientColors[0].withOpacity(0.03),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                gradient: LinearGradient(colors: gradientColors),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: Colors.white, size: 20),
            ),
            const Spacer(),
            Text(
              title,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 15,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              desc,
              style: const TextStyle(
                color: Colors.white54,
                fontSize: 10,
                height: 1.2,
              ),
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 10),
            Text(
              tag,
              style: TextStyle(
                color: gradientColors[0],
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
