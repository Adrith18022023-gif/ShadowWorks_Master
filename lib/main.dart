import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF070708),
      ),
      home: const SplashScreen(),
    );
  }
}

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    Future.delayed(const Duration(seconds: 3), () {
      Navigator.pushReplacement(
          context, MaterialPageRoute(builder: (context) => const LoginPage()));
    });
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              "CODEMATE AI",
              style: TextStyle(fontSize: 18, color: Colors.blueAccent, letterSpacing: 2),
            ),
            SizedBox(height: 15),
            Text(
              "Initializing Neural Engine...",
              style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w300),
            ),
          ],
        ),
      ),
    );
  }
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  String statusMessage = "Authenticate to access the core.";

  Future<void> handleAuth(String endpoint) async {
    if (emailController.text.isEmpty || passwordController.text.isEmpty) {
      setState(() => statusMessage = "Fields cannot be empty.");
      return;
    }
    try {
      final response = await http.post(
        Uri.parse('http://127.0.0.1:8000/$endpoint'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"email": emailController.text, "password": passwordController.text}),
      );
      final responseData = jsonDecode(response.body);
      
      if (responseData['status'] == 'success' || responseData['status'] == 'verified') {
        Navigator.pushReplacement(
            context, MaterialPageRoute(builder: (context) => Dashboard(userEmail: emailController.text)));
      } else {
        setState(() => statusMessage = "Access Denied.");
      }
    } catch (e) {
      setState(() => statusMessage = "Server offline.");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Container(
          width: 360,
          padding: const EdgeInsets.all(25),
          decoration: BoxDecoration(
            color: const Color(0xFF0F0F12),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.white10),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(statusMessage, style: const TextStyle(color: Colors.grey, fontSize: 13)),
              const SizedBox(height: 25),
              TextField(controller: emailController, decoration: const InputDecoration(labelText: "Email")),
              const SizedBox(height: 15),
              TextField(controller: passwordController, obscureText: true, decoration: const InputDecoration(labelText: "Password")),
              const SizedBox(height: 35),
              Row(
                children: [
                  Expanded(child: ElevatedButton(onPressed: () => handleAuth("login"), child: const Text("Log In"))),
                  const SizedBox(width: 10),
                  Expanded(child: OutlinedButton(onPressed: () => handleAuth("signup"), child: const Text("Sign Up"))),
                ],
              )
            ],
          ),
        ),
      ),
    );
  }
}

class Dashboard extends StatefulWidget {
  final String userEmail;
  const Dashboard({super.key, required this.userEmail});

  @override
  State<Dashboard> createState() => _DashboardState();
}

class _DashboardState extends State<Dashboard> {
  final TextEditingController promptController = TextEditingController();
  String responseText = "System ready.";
  String imageUrl = "";
  String selectedLanguage = "Python";
  String selectedMode = "Beginner Mode";

  Future<void> sendPrompt() async {
    if (promptController.text.isEmpty) return;
    setState(() {
      responseText = "Processing via AI Model...";
      imageUrl = "";
    });
    
    try {
      final response = await http.post(
        Uri.parse('http://127.0.0.1:8000/run_ai'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "email": widget.userEmail,
          "prompt": promptController.text,
          "language": selectedLanguage,
          "mode": selectedMode
        }),
      );
      final decoded = jsonDecode(response.body);
      setState(() {
        responseText = decoded['reply'];
        imageUrl = decoded['image'] ?? "";
      });
    } catch (e) {
      setState(() => responseText = "Connection to AI Engine lost.");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Codemate - ${widget.userEmail}", style: const TextStyle(fontSize: 15)),
        backgroundColor: const Color(0xFF09090C),
        actions: [
          IconButton(icon: const Icon(Icons.logout), onPressed: () {
            Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => const LoginPage()));
          }),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            Row(
              children: [
                DropdownButton<String>(
                  value: selectedMode,
                  dropdownColor: const Color(0xFF121216),
                  items: ['Beginner Mode', 'Pro Debugger', 'Cinematic Mode', 'AI Assistant'].map((String m) {
                    return DropdownMenuItem<String>(value: m, child: Text(m));
                  }).toList(),
                  onChanged: (val) => setState(() => selectedMode = val!),
                ),
                const SizedBox(width: 25),
                DropdownButton<String>(
                  value: selectedLanguage,
                  dropdownColor: const Color(0xFF121216),
                  items: ['Python', 'Java', 'JavaScript', 'C', 'C++', 'HTML'].map((String l) {
                    return DropdownMenuItem<String>(value: l, child: Text(l));
                  }).toList(),
                  onChanged: (val) => setState(() => selectedLanguage = val!),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Expanded(
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(15),
                decoration: BoxDecoration(
                  color: Colors.black,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.white12),
                ),
                child: SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (imageUrl.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 15.0),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: Image.network(imageUrl),
                          ),
                        ),
                      Text(
                        responseText,
                        style: const TextStyle(fontFamily: 'Courier', color: Colors.greenAccent, fontSize: 14, height: 1.4),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 20),
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Expanded(
                  child: TextField(
                    controller: promptController,
                    maxLines: null,
                    minLines: 3,
                    keyboardType: TextInputType.multiline,
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      hintText: "Type your code or prompt here. Press Enter for a new line...",
                    ),
                  ),
                ),
                const SizedBox(width: 15),
                SizedBox(
                  height: 60,
                  width: 60,
                  child: ElevatedButton(
                    onPressed: sendPrompt,
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
                    child: const Icon(Icons.send, color: Colors.white),
                  ),
                )
              ],
            )
          ],
        ),
      ),
    );
  }
}