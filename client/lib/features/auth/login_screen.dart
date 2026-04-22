import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../core/network/api_client.dart';

enum _RoleChoice { consumer, merchant }

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  _RoleChoice _selectedRole = _RoleChoice.consumer;
  bool _loading = false;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _showAuthDialog({
    required String title,
    required String message,
  }) {
    return showDialog<void>(
      context: context,
      builder: (context) => _AuthDialog(
        title: title,
        message: message,
      ),
    );
  }

  Future<void> _onLogin() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text;
    if (email.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('이메일과 비밀번호를 입력해주세요.')),
      );
      return;
    }

    setState(() => _loading = true);
    try {
      final session = await ApiClient.instance.login(
        email: email,
        password: password,
      );
      if (!mounted) return;
      final selectedRoleName = _selectedRole == _RoleChoice.merchant ? 'merchant' : 'consumer';
      if (session.user.role != selectedRoleName) {
        await _showAuthDialog(
          title: '회원 유형 불일치',
          message: '선택한 회원 유형과 계정 권한이 다릅니다.\n회원 유형을 확인한 뒤 다시 로그인해주세요.',
        );
        return;
      }
      if (session.user.role == 'merchant') {
        Navigator.pushReplacementNamed(context, AppRoutes.merchantDashboard);
      } else {
        Navigator.pushReplacementNamed(context, AppRoutes.consumerShell);
      }
    } catch (e) {
      if (!mounted) return;
      final raw = e.toString();
      final message = raw.replaceFirst('Exception: ', '');
      await _showAuthDialog(
        title: '로그인 실패',
        message: message == '아이디 또는 비밀번호를 확인해주세요.'
            ? '등록되지 않은 계정이거나 비밀번호가 일치하지 않습니다.\n아이디와 비밀번호를 다시 확인해주세요.'
            : message,
      );
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F7EC),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 14),
              Align(
                alignment: Alignment.centerLeft,
                child: Image.asset(
                  'assets/images/branding/icon_logo.png',
                  height: 44,
                  fit: BoxFit.contain,
                ),
              ),
              Align(
                alignment: Alignment.centerLeft,
                child: Image.asset(
                  'assets/images/branding/typo logo.png',
                  height: 34,
                  fit: BoxFit.contain,
                ),
              ),
              const SizedBox(height: 22),
              const Text(
                '전통시장의 생동감과 장보기의 똑똑함을 담은\n마켓인포에 오신 것을 환영합니다.',
                style: TextStyle(
                  fontSize: 14,
                  color: Color(0xFF5F6A58),
                  height: 1.4,
                ),
              ),
              const SizedBox(height: 24),
              _RoleCard(
                icon: Icons.shopping_bag_outlined,
                title: '소비자로 시작하기',
                subtitle: '신선한 재료와 일상의 즐거움을 찾아요',
                selected: _selectedRole == _RoleChoice.consumer,
                onTap: () => setState(() => _selectedRole = _RoleChoice.consumer),
              ),
              const SizedBox(height: 12),
              _RoleCard(
                icon: Icons.storefront_outlined,
                title: '상인으로 시작하기',
                subtitle: '귀하의 소중한 상품을 더 넓은 세상에 알려요',
                selected: _selectedRole == _RoleChoice.merchant,
                onTap: () => setState(() => _selectedRole = _RoleChoice.merchant),
              ),
              const SizedBox(height: 22),
              const Text(
                '이메일 로그인',
                style: TextStyle(
                  fontSize: 12,
                  color: Color(0xFF7A8472),
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(
                  hintText: '이메일을 입력하세요',
                  filled: true,
                  fillColor: Color(0xFFFDFBF5),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.all(Radius.circular(14)),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: _passwordController,
                obscureText: true,
                decoration: const InputDecoration(
                  hintText: '비밀번호를 입력하세요',
                  filled: true,
                  fillColor: Color(0xFFFDFBF5),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.all(Radius.circular(14)),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),
              const SizedBox(height: 14),
              SizedBox(
                width: double.infinity,
                child: FilledButton(
                  onPressed: _loading ? null : _onLogin,
                  style: FilledButton.styleFrom(
                    minimumSize: const Size.fromHeight(50),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  child: Text(_loading ? '로그인 중...' : '로그인하기'),
                ),
              ),
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton(
                  onPressed: _loading
                      ? null
                      : () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('회원가입은 서버/DB 연동 후 제공될 예정입니다.')),
                          );
                        },
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size.fromHeight(50),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  ),
                  child: const Text('회원가입'),
                ),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: _loading
                          ? null
                          : () {
                              setState(() => _selectedRole = _RoleChoice.consumer);
                              _emailController.text = 'consumer@example.com';
                              _passwordController.text = 'password123';
                              _onLogin();
                            },
                      child: const Text('데모 소비자'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: OutlinedButton(
                      onPressed: _loading
                          ? null
                          : () {
                              setState(() => _selectedRole = _RoleChoice.merchant);
                              _emailController.text = 'merchant@example.com';
                              _passwordController.text = 'password123';
                              _onLogin();
                            },
                      child: const Text('데모 상인'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              const Center(
                child: Text(
                  '서비스 이용약관  ·  개인정보 처리방침  ·  고객지원',
                  style: TextStyle(fontSize: 11, color: Color(0xFF98A18F)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _AuthDialog extends StatelessWidget {
  const _AuthDialog({
    required this.title,
    required this.message,
  });

  final String title;
  final String message;

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: const Color(0xFFFDFBF5),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(20, 18, 20, 16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 36,
                  height: 36,
                  decoration: const BoxDecoration(
                    color: Color(0xFFFBF0EA),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.error_outline, size: 20, color: Color(0xFFA34220)),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    title,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: const Color(0xFF1E1D18),
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              message,
              style: const TextStyle(
                fontSize: 14,
                height: 1.45,
                color: Color(0xFF3D3B34),
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: () => Navigator.pop(context),
                style: FilledButton.styleFrom(
                  minimumSize: const Size.fromHeight(44),
                ),
                child: const Text('확인'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RoleCard extends StatelessWidget {
  const _RoleCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.selected,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: selected ? const Color(0xFFFDFBF5) : const Color(0xFFF4F8EF),
      borderRadius: BorderRadius.circular(20),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: selected ? const Color(0xFF4A7D1A) : const Color(0xFFDCE6D2),
              width: selected ? 1.6 : 1.0,
            ),
          ),
          child: Row(
            children: [
              Icon(icon, color: const Color(0xFF4A7D1A), size: 24),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 28 / 1.75,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF2F5710),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: const TextStyle(
                        fontSize: 13,
                        color: Color(0xFF6C7763),
                      ),
                    ),
                  ],
                ),
              ),
              if (selected) const Icon(Icons.check_circle, color: Color(0xFF4A7D1A), size: 20),
            ],
          ),
        ),
      ),
    );
  }
}
