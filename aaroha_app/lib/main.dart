import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:aaroha_app/screens/auth/login_screen.dart';
import 'package:aaroha_app/screens/home/home_screen.dart';
import 'package:aaroha_app/services/auth_service.dart';

import 'package:flutter/foundation.dart' show kIsWeb;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    if (kIsWeb) {
      await Firebase.initializeApp(
        options: const FirebaseOptions(
          apiKey: "AIzaSyDU6Jt_23qht85yicJUxB-rlD1bUg4nCZE",
          appId: "1:185545417054:web:e712a20e2efc4d29b0f19e",
          messagingSenderId: "185545417054",
          projectId: "aaroha-cbd26",
          storageBucket: "aaroha-cbd26.firebasestorage.app",
        ),
      );
    } else {
      await Firebase.initializeApp(
        options: const FirebaseOptions(
          apiKey: "AIzaSyDU6Jt_23qht85yicJUxB-rlD1bUg4nCZE",
          appId: "1:185545417054:android:2a2d9ea66935fa51e3efcf",
          messagingSenderId: "185545417054",
          projectId: "aaroha-cbd26",
          storageBucket: "aaroha-cbd26.firebasestorage.app",
        ),
      );
    }
  } catch (e) {
    debugPrint("Firebase init note: $e");
    try {
      await Firebase.initializeApp();
    } catch (_) {}
  }
  runApp(const AAROHAApp());
}

class AAROHAApp extends StatelessWidget {
  const AAROHAApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'AAROHA Human OS',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const AuthCheckWrapper(),
    );
  }
}

class AuthCheckWrapper extends StatelessWidget {
  const AuthCheckWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<User?>(
      stream: AuthService.authStateChanges,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            backgroundColor: Color(0xFF0B0F19),
            body: Center(
              child: CircularProgressIndicator(color: Colors.purpleAccent),
            ),
          );
        }

        if (snapshot.hasData && snapshot.data != null) {
          return const HomeScreen();
        }

        return const LoginScreen();
      },
    );
  }
}
