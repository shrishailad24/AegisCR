import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:aaroha_app/core/constants.dart';

class CareerProfileScreen extends StatefulWidget {
  final String userId;

  const CareerProfileScreen({super.key, required this.userId});

  @override
  State<CareerProfileScreen> createState() => _CareerProfileScreenState();
}

class _CareerProfileScreenState extends State<CareerProfileScreen> {
  final _educationController = TextEditingController();
  final _skillsController = TextEditingController();
  final _projectsController = TextEditingController();
  final _goalsController = TextEditingController();

  bool _isLoading = false;

  Future<void> _saveProfile() async {
    setState(() {
      _isLoading = true;
    });

    final String baseUrl = AppConstants.baseUrl;

    List<String> splitText(String text) {
      return text
          .split(',')
          .map((e) => e.trim())
          .where((e) => e.isNotEmpty)
          .toList();
    }

    final profileData = {
      "user_id": widget.userId,
      "education": splitText(_educationController.text),
      "skills": splitText(_skillsController.text),
      "certifications": [],
      "projects": splitText(_projectsController.text),
      "career_goals": splitText(_goalsController.text),
      "work_experience": [],
    };

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/update-profile'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode(profileData),
      );

      if (response.statusCode == 200) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Profile Saved to AI Twin!'),
              backgroundColor: Colors.green,
            ),
          );
        }
      } else {
        throw Exception('Server rejected the profile');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Connection Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: const Text(
          'My Career Profile',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF1E293B),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "Define Your AI Career Twin",
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              "This data acts as the memory for your AI advisor.",
              style: TextStyle(color: Colors.white60),
            ),
            const SizedBox(height: 24),

            _buildTextField(
              "Education (e.g., B.Tech AI & DS)",
              _educationController,
            ),
            _buildTextField("Skills (Separate with commas)", _skillsController),
            _buildTextField(
              "Projects (Separate with commas)",
              _projectsController,
            ),
            _buildTextField(
              "Career Goals (e.g., AI Engineer)",
              _goalsController,
            ),

            const SizedBox(height: 32),

            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.purpleAccent,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                onPressed: _isLoading ? null : _saveProfile,
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2,
                        ),
                      )
                    : const Text(
                        'Save Profile to Memory',
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTextField(String label, TextEditingController controller) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20.0),
      child: TextField(
        controller: controller,
        style: const TextStyle(color: Colors.white),
        decoration: InputDecoration(
          labelText: label,
          labelStyle: const TextStyle(color: Colors.white60),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: Colors.white24),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: Colors.purpleAccent),
          ),
          filled: true,
          fillColor: const Color(0xFF1E293B),
        ),
      ),
    );
  }
}
