import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/auth/auth_provider.dart';
import '../../../app/routes.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _nameController = TextEditingController();
  bool _isLogin = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    final authProvider = context.read<AuthProvider>();
    bool success;

    if (_isLogin) {
      success = await authProvider.login(
        _emailController.text,
        _passwordController.text,
      );
    } else {
      success = await authProvider.register(
        _emailController.text,
        _passwordController.text,
        _nameController.text,
      );
    }

    if (success && mounted) {
      Navigator.pushReplacementNamed(context, AppRoutes.home);
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF0F172A), Color(0xFF0EA5E9)],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Logo
                  const Text(
                    'IGAMS',
                    style: TextStyle(
                      fontSize: 40,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Management Control System',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.white.withOpacity(0.7),
                    ),
                  ),
                  const SizedBox(height: 48),

                  // Form Card
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Form(
                        key: _formKey,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            // Toggle
                            Row(
                              children: [
                                Expanded(
                                  child: TextButton(
                                    onPressed: () =>
                                        setState(() => _isLogin = true),
                                    style: TextButton.styleFrom(
                                      backgroundColor: _isLogin
                                          ? Theme.of(
                                              context,
                                            ).colorScheme.primary
                                          : Colors.grey.shade200,
                                      foregroundColor: _isLogin
                                          ? Colors.white
                                          : Colors.grey.shade600,
                                    ),
                                    child: const Text('Login'),
                                  ),
                                ),
                                Expanded(
                                  child: TextButton(
                                    onPressed: () =>
                                        setState(() => _isLogin = false),
                                    style: TextButton.styleFrom(
                                      backgroundColor: !_isLogin
                                          ? Theme.of(
                                              context,
                                            ).colorScheme.primary
                                          : Colors.grey.shade200,
                                      foregroundColor: !_isLogin
                                          ? Colors.white
                                          : Colors.grey.shade600,
                                    ),
                                    child: const Text('Register'),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 24),

                            // Name field (register only)
                            if (!_isLogin) ...[
                              TextFormField(
                                controller: _nameController,
                                decoration: const InputDecoration(
                                  labelText: 'Full Name',
                                  prefixIcon: Icon(Icons.person),
                                ),
                                validator: (value) =>
                                    value?.isEmpty ?? true ? 'Required' : null,
                              ),
                              const SizedBox(height: 16),
                            ],

                            // Email
                            TextFormField(
                              controller: _emailController,
                              decoration: const InputDecoration(
                                labelText: 'Email',
                                prefixIcon: Icon(Icons.email),
                              ),
                              keyboardType: TextInputType.emailAddress,
                              validator: (value) =>
                                  value?.isEmpty ?? true ? 'Required' : null,
                            ),
                            const SizedBox(height: 16),

                            // Password
                            TextFormField(
                              controller: _passwordController,
                              decoration: const InputDecoration(
                                labelText: 'Password',
                                prefixIcon: Icon(Icons.lock),
                              ),
                              obscureText: true,
                              validator: (value) =>
                                  value?.isEmpty ?? true ? 'Required' : null,
                            ),
                            const SizedBox(height: 24),

                            // Error Message
                            if (authProvider.error != null)
                              Padding(
                                padding: const EdgeInsets.only(bottom: 16),
                                child: Text(
                                  authProvider.error!,
                                  style: const TextStyle(color: Colors.red),
                                  textAlign: TextAlign.center,
                                ),
                              ),

                            // Submit Button
                            ElevatedButton(
                              onPressed: authProvider.isLoading
                                  ? null
                                  : _submit,
                              child: authProvider.isLoading
                                  ? const SizedBox(
                                      height: 20,
                                      width: 20,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                      ),
                                    )
                                  : Text(_isLogin ? 'Login' : 'Register'),
                            ),
                            const SizedBox(height: 16),
                            TextButton(
                              onPressed: () {
                                context.read<AuthProvider>().loginAsGuest();
                                Navigator.pushReplacementNamed(
                                  context,
                                  AppRoutes.home,
                                );
                              },
                              child: const Text('Skip Login (Guest Mode)'),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
