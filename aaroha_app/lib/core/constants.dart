import 'package:flutter/foundation.dart';

class AppConstants {
  // Use 10.0.2.2 for Android Emulator, localhost for Web.
  // For physical devices, replace with your machine's IP address.
  static String get baseUrl {
    if (kIsWeb) {
      return 'http://localhost:8002';
    } else {
      // Default for Android Emulator
      return 'http://10.0.2.2:8002';
    }
  }

  static const String appName = 'AAROHA Human OS';
}
