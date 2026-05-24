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
    Future.delayed(const Duration(seconds: 4), () {
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
              "CODEMATE",
              style: TextStyle(fontSize: 16, color: Colors.blueAccent, letterSpacing: 2),
            ),
            SizedBox(height: 15),
            Text(
              "Welcome to the platform",
              style: TextStyle(
                color: Colors.white,
                fontSize: 22,
                fontWeight: FontWeight.w300,
              ),
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
  String statusMessage = "Please login or sign up to continue.";

  Future<void> handleAuth(String endpoint) async {
    if (emailController.text.isEmpty || passwordController.text.isEmpty) {
      setState(() => statusMessage = "Please enter both email and password.");
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
        setState(() => statusMessage = "Invalid credentials or user already exists.");
      }
    } catch (e) {
      setState(() => statusMessage = "Error connecting to the server.");
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
  String responseText = "Waiting for your prompt...";
  String selectedLanguage = "Python";
  String selectedMode = "Beginner Engine";

  Future<void> sendPrompt() async {
    if (promptController.text.isEmpty) return;
    setState(() => responseText = "Loading response from server...");
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
      setState(() => responseText = jsonDecode(response.body)['reply']);
    } catch (e) {
      setState(() => responseText = "Error: Could not connect to the backend.");
    }
  }

  void showInfoDialog(String title, String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF121216),
        title: Text(title, style: const TextStyle(color: Colors.blueAccent)),
        content: Text(message, style: const TextStyle(color: Colors.white70)),
        actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text("OK"))],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Dashboard - ${widget.userEmail}", style: const TextStyle(fontSize: 15)),
        backgroundColor: const Color(0xFF09090C),
        actions: [
          IconButton(icon: const Icon(Icons.history), onPressed: () => showInfoDialog("History", "Your history is saved in the database.")),
          IconButton(icon: const Icon(Icons.help_outline), onPressed: () => showInfoDialog("Help", "Select a mode and language, then type your prompt.")),
          IconButton(icon: const Icon(Icons.logout), onPressed: () {
            Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => const LoginPage()));
          }),
        ],
      ),
      body: Row(
        children: [
          Container(
            width: 75,
            color: const Color(0xFF09090C),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                IconButton(icon: const Icon(Icons.code, color: Colors.blueAccent), onPressed: () {}),
                const SizedBox(height: 30),
                IconButton(icon: const Icon(Icons.image, color: Colors.grey), onPressed: () => showInfoDialog("Feature Unavailable", "Image generation coming soon.")),
                const SizedBox(height: 30),
                IconButton(icon: const Icon(Icons.mic, color: Colors.grey), onPressed: () => showInfoDialog("Feature Unavailable", "Voice input coming soon.")),
              ],
            ),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                children: [
                  Row(
                    children: [
                      DropdownButton<String>(
                        value: selectedMode,
                        dropdownColor: const Color(0xFF121216),
                        items: ['Beginner Engine', 'Pro Debugger', 'Cinematic Generator'].map((String modeOption) {
                          return DropdownMenuItem<String>(value: modeOption, child: Text(modeOption));
                        }).toList(),
                        onChanged: (updatedMode) => setState(() => selectedMode = updatedMode!),
                      ),
                      const SizedBox(width: 25),
                      DropdownButton<String>(
                        value: selectedLanguage,
                        dropdownColor: const Color(0xFF121216),
                        items: ['Python', 'C', 'C++', 'Java', 'JavaScript'].map((String langOption) {
                          return DropdownMenuItem<String>(value: langOption, child: Text(langOption));
                        }).toList(),
                        onChanged: (updatedLang) => setState(() => selectedLanguage = updatedLang!),
                      ),
                      const Spacer(),
                      ElevatedButton(
                        onPressed: () {
                          promptController.text = "Write a calculator program for me.";
                        },
                        child: const Text("Example Prompt"),
                      )
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
                        child: Text(
                          responseText,
                          style: const TextStyle(fontFamily: 'Courier', color: Colors.greenAccent, fontSize: 14, height: 1.4),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: promptController,
                          decoration: const InputDecoration(
                            border: OutlineInputBorder(),
                            hintText: "Enter your prompt here...",
                          ),
                        ),
                      ),
                      const SizedBox(width: 15),
                      SizedBox(
                        height: 55,
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
          ),
        ],
      ),
    );
  }
}