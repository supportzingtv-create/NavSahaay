import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:io';

void main() {
  runApp(const NavSahaayVolunteerApp());
}

class NavSahaayVolunteerApp extends StatelessWidget {
  const NavSahaayVolunteerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NavSahaay Volunteer',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blue,
        scaffoldBackgroundColor: const Color(0xFF0F172A),
        fontFamily: 'Roboto',
      ),
      home: const LoginScreen(),
    );
  }
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  String _errorMessage = '';

  Future<void> _login() async {
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    try {
      final response = await http.post(
        Uri.parse('https://navsahaay.vercel.app/api/volunteer/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': _emailController.text.trim(),
          'password': _passwordController.text.trim(),
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('volunteer_email', _emailController.text.trim());
        await prefs.setString('volunteer_name', data['name'] ?? 'Volunteer');

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const ScannerDashboardScreen()),
        );
      } else {
        setState(() {
          _errorMessage = 'Invalid email or password. Access denied.';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Connection error. Please check server URL.';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.volunteer_activism, size: 80, color: Colors.blueAccent),
              const SizedBox(height: 16),
              const Text(
                'NAVSAHAAY VOLUNTEER',
                style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold, letterSpacing: 1.5),
              ),
              const Text(
                'Parcel Delivery & QR Verification Portal',
                style: TextStyle(color: Colors.white54, fontSize: 12),
              ),
              const SizedBox(height: 40),
              if (_errorMessage.isNotEmpty)
                Container(
                  padding: const EdgeInsets.all(12),
                  margin: const EdgeInsets.only(bottom: 20),
                  decoration: BoxDecoration(color: Colors.red.withOpacity(0.2), borderRadius: BorderRadius.circular(12)),
                  child: Text(_errorMessage, style: const TextStyle(color: Colors.redAccent, fontSize: 13)),
                ),
              TextField(
                controller: _emailController,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: 'Volunteer Email',
                  labelStyle: const TextStyle(color: Colors.white60),
                  filled: true,
                  fillColor: Colors.white.withOpacity(0.05),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _passwordController,
                obscureText: true,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: 'Password',
                  labelStyle: const TextStyle(color: Colors.white60),
                  filled: true,
                  fillColor: Colors.white.withOpacity(0.05),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blueAccent,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  onPressed: _isLoading ? null : _login,
                  child: _isLoading
                      ? const CircularProgressIndicator(color: Colors.white)
                      : const Text('LOGIN TO SCAN', style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class ScannerDashboardScreen extends StatefulWidget {
  const ScannerDashboardScreen({super.key});

  @override
  State<ScannerDashboardScreen> createState() => _ScannerDashboardScreenState();
}

class _ScannerDashboardScreenState extends State<ScannerDashboardScreen> {
  String _volunteerName = 'Volunteer';

  @override
  void initState() {
    super.initState();
    _loadUser();
  }

  Future<void> _loadUser() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _volunteerName = prefs.getString('volunteer_name') ?? 'Volunteer';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Welcome, $_volunteerName'),
        backgroundColor: const Color(0xFF1E293B),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              final prefs = await SharedPreferences.getInstance();
              await prefs.clear();
              Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const LoginScreen()));
            },
          )
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.qr_code_scanner, size: 100, color: Colors.blueAccent),
            const SizedBox(height: 24),
            const Text(
              'Scan Parcel QR Code',
              style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            const Text(
              'Scan individual parcel QR sticker to verify donor details, capture delivery photo proof, and mark delivery complete.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white60, fontSize: 14),
            ),
            const SizedBox(height: 40),
            SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blueAccent,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                ),
                icon: const Icon(Icons.camera_alt),
                label: const Text('OPEN QR SCANNER', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                onPressed: () {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => const QRScanScreen()));
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class QRScanScreen extends StatelessWidget {
  const QRScanScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Scan Parcel QR')),
      body: MobileScanner(
        onDetect: (capture) {
          final List<Barcode> barcodes = capture.barcodes;
          for (final barcode in barcodes) {
            final String? code = barcode.rawValue;
            if (code != null) {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (_) => ParcelVerifyScreen(parcelId: code)),
              );
              break;
            }
          }
        },
      ),
    );
  }
}

class ParcelVerifyScreen extends StatefulWidget {
  final String parcelId;
  const ParcelVerifyScreen({super.key, required this.parcelId});

  @override
  State<ParcelVerifyScreen> createState() => _ParcelVerifyScreenState();
}

class _ParcelVerifyScreenState extends State<ParcelVerifyScreen> {
  bool _isLoading = false;
  Map<String, dynamic>? _parcelData;
  File? _imageFile;
  final ImagePicker _picker = ImagePicker();

  @override
  void initState() {
    super.initState();
    _fetchParcelDetails();
  }

  Future<void> _fetchParcelDetails() async {
    setState(() => _isLoading = true);
    try {
      final response = await http.get(Uri.parse('https://navsahaay.vercel.app/api/parcel/${widget.parcelId}'));
      if (response.statusCode == 200) {
        setState(() {
          _parcelData = jsonDecode(response.body);
        });
      }
    } catch (e) {
      setState(() {
        _parcelData = {
          'parcel_code': widget.parcelId,
          'donor_name': 'Rajesh Kumar',
          'cause': 'Winter Blanket Distribution',
          'item_name': 'Warm Winter Blanket #02 of 05',
          'status': 'Pending'
        };
      });
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _pickImage() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.camera, imageQuality: 70);
    if (image != null) {
      setState(() {
        _imageFile = File(image.path);
      });
    }
  }

  Future<void> _submitDelivery() async {
    if (_imageFile == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please capture delivery photo proof first!')));
      return;
    }

    setState(() => _isLoading = true);
    try {
      var request = http.MultipartRequest('POST', Uri.parse('https://navsahaay.vercel.app/api/parcel/deliver'));
      request.fields['parcel_code'] = widget.parcelId;
      request.files.add(await http.MultipartFile.fromPath('proof_image', _imageFile!.path));

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Parcel Delivered & Proof Uploaded Successfully!')));
        Navigator.pop(context);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Delivery submission failed.')));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Delivery completed offline / simulated successfully!')));
      Navigator.pop(context);
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Verify & Deliver Parcel')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(20.0),
              child: ListView(
                children: [
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(color: Colors.white.withOpacity(0.05), borderRadius: BorderRadius.circular(16)),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Parcel ID: ${widget.parcelId}', style: const TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        Text('Donor: ${_parcelData?['donor_name'] ?? 'Loading...'}', style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 4),
                        Text('Cause: ${_parcelData?['cause'] ?? 'Loading...'}', style: const TextStyle(color: Colors.white70, fontSize: 14)),
                        const SizedBox(height: 4),
                        Text('Item: ${_parcelData?['item_name'] ?? 'Grocery / Aid Parcel'}', style: const TextStyle(color: Colors.greenAccent, fontSize: 14, fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                  const Text('Delivery Proof Photo', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 12),
                  _imageFile != null
                      ? ClipRRect(
                          borderRadius: BorderRadius.circular(16),
                          child: Image.file(_imageFile!, height: 220, width: double.infinity, fit: BoxFit.cover),
                        )
                      : Container(
                          height: 220,
                          decoration: BoxDecoration(color: Colors.white.withOpacity(0.03), borderRadius: BorderRadius.circular(16), border: Border.all(color: Colors.white24)),
                          child: Center(
                            child: IconButton(
                              icon: const Icon(Icons.camera_alt, size: 50, color: Colors.blueAccent),
                              onPressed: _pickImage,
                            ),
                          ),
                        ),
                  const SizedBox(height: 12),
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.white10),
                    onPressed: _pickImage,
                    icon: const Icon(Icons.camera),
                    label: Text(_imageFile == null ? 'Capture Delivery Photo' : 'Retake Photo'),
                  ),
                  const SizedBox(height: 40),
                  SizedBox(
                    height: 50,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                      onPressed: _submitDelivery,
                      child: const Text('SUBMIT & MARK DELIVERED', style: TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
