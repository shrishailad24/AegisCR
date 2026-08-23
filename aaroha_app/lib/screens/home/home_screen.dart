import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'dart:io';
import 'dart:convert';
import 'dart:math' as math;
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
  String _userId = AuthService.currentUser?.uid ?? 'guest_user';
  String _userName = AuthService.currentUser?.displayName ?? 'Explorer';
  String _weatherCondition = 'Sunny';
  double _temperature = 27.0;
  bool _isWeatherLoading = false;

  @override
  void initState() {
    super.initState();
    _loadUserSession();
    _fetchWeather();
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

  Future<void> _fetchWeather() async {
    setState(() => _isWeatherLoading = true);
    try {
      final client = HttpClient();
      final request = await client.getUrl(Uri.parse(
        'https://api.open-meteo.com/v1/forecast?latitude=12.9716&longitude=77.5946&current_weather=true'
      ));
      final response = await request.close();
      if (response.statusCode == 200) {
        final jsonString = await response.transform(utf8.decoder).join();
        final data = json.decode(jsonString);
        final currentWeather = data['current_weather'];
        final temp = (currentWeather['temperature'] as num).toDouble();
        final code = currentWeather['weathercode'] as int;

        String condition = 'Sunny';
        if (code == 0) {
          condition = 'Sunny';
        } else if (code >= 1 && code <= 3) {
          condition = 'Cloudy';
        } else if (code >= 51 && code <= 67 || code >= 80 && code <= 82) {
          condition = 'Rainy';
        } else if (code >= 71 && code <= 77) {
          condition = 'Snowy';
        } else if (code >= 95 && code <= 99) {
          condition = 'Stormy';
        } else {
          condition = 'Cloudy';
        }

        setState(() {
          _temperature = temp;
          _weatherCondition = condition;
          _isWeatherLoading = false;
        });
      } else {
        setState(() => _isWeatherLoading = false);
      }
    } catch (e) {
      debugPrint("Failed to fetch weather: $e");
      setState(() => _isWeatherLoading = false);
    }
  }

  List<Color> _getWeatherGradientColors() {
    switch (_weatherCondition) {
      case 'Sunny':
        return const [Color(0xFF2C241E), Color(0xFF0B0F19)];
      case 'Cloudy':
        return const [Color(0xFF1C2230), Color(0xFF0B0F19)];
      case 'Rainy':
      case 'Stormy':
        return const [Color(0xFF141A28), Color(0xFF0B0F19)];
      case 'Snowy':
        return const [Color(0xFF1E2838), Color(0xFF0B0F19)];
      default:
        return const [Color(0xFF0B0F19), Color(0xFF05070B)];
    }
  }

  IconData _getWeatherIcon() {
    switch (_weatherCondition) {
      case 'Sunny':
        return Icons.wb_sunny;
      case 'Cloudy':
        return Icons.wb_cloudy;
      case 'Rainy':
        return Icons.umbrella;
      case 'Stormy':
        return Icons.thunderstorm;
      case 'Snowy':
        return Icons.ac_unit;
      default:
        return Icons.cloud;
    }
  }

  Color _getWeatherColor() {
    switch (_weatherCondition) {
      case 'Sunny':
        return Colors.orangeAccent;
      case 'Cloudy':
        return Colors.blueGrey;
      case 'Rainy':
        return Colors.blueAccent;
      case 'Stormy':
        return Colors.purpleAccent;
      case 'Snowy':
        return Colors.cyanAccent;
      default:
        return Colors.white70;
    }
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
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
        child: Stack(
          children: [
            // Dynamic Background based on Weather
            Positioned.fill(
              child: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: _getWeatherGradientColors(),
                  ),
                ),
              ),
            ),
            // Animated Overlays (Particles, Flares, Clouds)
            Positioned.fill(
              child: WeatherAnimationOverlay(condition: _weatherCondition),
            ),
            SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildGreetingBanner(),
                  const SizedBox(height: 24),

                  const Text(
                    "LIVE OS INSIGHTS (SIMULATED)",
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
          ],
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
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: Colors.white.withOpacity(0.05),
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      _getWeatherIcon(),
                      color: _getWeatherColor(),
                      size: 14,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      "$_weatherCondition • ${_temperature.toStringAsFixed(1)}°C",
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
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

// --- Weather Animation Overlay Widget ---
class WeatherAnimationOverlay extends StatefulWidget {
  final String condition;
  const WeatherAnimationOverlay({super.key, required this.condition});

  @override
  State<WeatherAnimationOverlay> createState() => _WeatherAnimationOverlayState();
}

class _WeatherAnimationOverlayState extends State<WeatherAnimationOverlay>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 10),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        if (widget.condition == 'Rainy' || widget.condition == 'Stormy') {
          return CustomPaint(
            painter: RainPainter(_controller.value),
            child: Container(),
          );
        } else if (widget.condition == 'Sunny') {
          return CustomPaint(
            painter: SunnyPainter(_controller.value),
            child: Container(),
          );
        } else if (widget.condition == 'Cloudy') {
          return CustomPaint(
            painter: CloudyPainter(_controller.value),
            child: Container(),
          );
        }
        return Container();
      },
    );
  }
}

// --- Rain Drops Custom Painter ---
class RainPainter extends CustomPainter {
  final double progress;
  RainPainter(this.progress);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.lightBlueAccent.withOpacity(0.3)
      ..strokeWidth = 1.5
      ..strokeCap = StrokeCap.round;

    for (int i = 0; i < 40; i++) {
      double x = (i * 37) % size.width;
      double speed = 1.0 + (i % 3) * 0.5;
      double startY = ((progress * size.height * speed) + (i * 47)) % size.height;
      canvas.drawLine(
        Offset(x, startY),
        Offset(x, startY + 15),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

// --- Sunny Breathing Flares Custom Painter ---
class SunnyPainter extends CustomPainter {
  final double progress;
  SunnyPainter(this.progress);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.amber.withOpacity(0.06)
      ..style = PaintingStyle.fill;

    double centerX = size.width * 0.8;
    double centerY = size.height * 0.1;
    double baseRadius = 80.0;
    double scale = 1.0 + 0.15 * math.sin(progress * 2.0 * math.pi);

    canvas.drawCircle(Offset(centerX, centerY), baseRadius * scale, paint);
    canvas.drawCircle(
      Offset(centerX, centerY),
      (baseRadius + 50.0) * scale,
      Paint()..color = Colors.amber.withOpacity(0.03),
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

// --- Cloudy Moving Mists Custom Painter ---
class CloudyPainter extends CustomPainter {
  final double progress;
  CloudyPainter(this.progress);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.02)
      ..style = PaintingStyle.fill;

    for (int i = 0; i < 4; i++) {
      double speed = 0.3 + (i * 0.15);
      double x = ((progress * size.width * speed) + (i * size.width * 0.3)) % (size.width + 200.0) - 100.0;
      double y = (size.height * 0.05) + (i * 40.0);
      double radius = 40.0 + (i * 10.0);
      canvas.drawCircle(Offset(x, y), radius, paint);
      canvas.drawCircle(Offset(x + 30, y - 10), radius * 0.8, paint);
      canvas.drawCircle(Offset(x - 30, y - 5), radius * 0.8, paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
