import 'package:aaroha_app/core/constants.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class VaultViewerScreen extends StatefulWidget {
  const VaultViewerScreen({super.key});

  @override
  State<VaultViewerScreen> createState() => _VaultViewerScreenState();
}

class _VaultViewerScreenState extends State<VaultViewerScreen> {
  List<String> _files = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchFiles();
  }

  Future<void> _fetchFiles() async {
    final String baseUrl = AppConstants.baseUrl;
    try {
      final response = await http.get(Uri.parse('$baseUrl/list-files'));
      if (!mounted) return;
      if (response.statusCode == 200) {
        setState(() {
          _files = List<String>.from(jsonDecode(response.body)['files']);
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("My Vault")),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: _files.length,
              itemBuilder: (context, index) => ListTile(
                leading: const Icon(Icons.description),
                title: Text(_files[index]),
              ),
            ),
    );
  }
}
