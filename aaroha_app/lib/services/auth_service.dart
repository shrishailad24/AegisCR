import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:flutter/foundation.dart';

class AuthService {
  static final FirebaseAuth _auth = FirebaseAuth.instance;
  static final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  static final GoogleSignIn _googleSignIn = GoogleSignIn();

  // Expose Auth State Changes Stream
  static Stream<User?> get authStateChanges => _auth.authStateChanges();

  // Expose current user
  static User? get currentUser => _auth.currentUser;

  // Sign In with Email & Password
  static Future<UserCredential> signInWithEmail(
    String email,
    String password,
  ) async {
    final credential = await _auth.signInWithEmailAndPassword(
      email: email,
      password: password,
    );

    // Update lastLogin timestamp in Firestore
    if (credential.user != null) {
      await _firestore
          .collection('users')
          .doc(credential.user!.uid)
          .update({'lastLogin': FieldValue.serverTimestamp()})
          .catchError((_) {}); // Ignore if document doesn't exist yet
    }

    return credential;
  }

  // Sign Up with Email, Name, and Phone
  static Future<UserCredential> signUpWithEmail({
    required String name,
    required String email,
    required String phone,
    required String password,
  }) async {
    final credential = await _auth.createUserWithEmailAndPassword(
      email: email,
      password: password,
    );

    if (credential.user != null) {
      final uid = credential.user!.uid;
      // Initialize firestore user profile document
      await _firestore.collection('users').doc(uid).set({
        'uid': uid,
        'name': name,
        'email': email,
        'phone': phone,
        'createdAt': FieldValue.serverTimestamp(),
        'lastLogin': FieldValue.serverTimestamp(),
        'profilePhoto': '',
        'careerBrain': {},
        'educationBrain': {},
        'moneyBrain': {},
        'healthBrain': {},
        'lifeBrain': {},
      });
    }

    return credential;
  }

  // Google Sign In
  static Future<UserCredential?> signInWithGoogle() async {
    try {
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
      if (googleUser == null) return null; // User canceled sign-in

      final GoogleSignInAuthentication googleAuth =
          await googleUser.authentication;
      final AuthCredential credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      final userCredential = await _auth.signInWithCredential(credential);

      if (userCredential.user != null) {
        final user = userCredential.user!;
        final doc = await _firestore.collection('users').doc(user.uid).get();

        if (!doc.exists) {
          // If first time sign-in, initialize user document in Firestore
          await _firestore.collection('users').doc(user.uid).set({
            'uid': user.uid,
            'name': user.displayName ?? 'Google User',
            'email': user.email ?? '',
            'phone': user.phoneNumber ?? '',
            'createdAt': FieldValue.serverTimestamp(),
            'lastLogin': FieldValue.serverTimestamp(),
            'profilePhoto': user.photoURL ?? '',
            'careerBrain': {},
            'educationBrain': {},
            'moneyBrain': {},
            'healthBrain': {},
            'lifeBrain': {},
          });
        } else {
          // Update lastLogin
          await _firestore.collection('users').doc(user.uid).update({
            'lastLogin': FieldValue.serverTimestamp(),
          });
        }
      }
      return userCredential;
    } catch (e) {
      debugPrint("Google Sign In Error: $e");
      rethrow;
    }
  }

  // Reset Password Request
  static Future<void> sendPasswordReset(String email) async {
    await _auth.sendPasswordResetEmail(email: email);
  }

  // Log Out
  static Future<void> signOut() async {
    await _googleSignIn.signOut().catchError((_) => null);
    await _auth.signOut();
  }
}
