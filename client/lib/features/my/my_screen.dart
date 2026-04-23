import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../core/network/api_client.dart';

class MyScreen extends StatefulWidget {
  const MyScreen({super.key});

  @override
  State<MyScreen> createState() => _MyScreenState();
}

class _MyScreenState extends State<MyScreen> {
  bool _loading = true;
  String? _error;
  AuthUser? _user;
  List<Map<String, dynamic>> _preorders = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final user = await ApiClient.instance.getMyProfile();
      List<Map<String, dynamic>> preorders = [];
      if (user.role == 'consumer') {
        preorders = await ApiClient.instance.getMyPreorders();
      }
      if (mounted) {
        setState(() {
          _user = user;
          _preorders = preorders;
          _loading = false;
          _error = null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  Future<void> _cancel(String preorderId) async {
    try {
      await ApiClient.instance.cancelPreorder(preorderId);
      _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    }
  }

  void _logout() {
    ApiClient.instance.clearSession();
    Navigator.pushNamedAndRemoveUntil(context, AppRoutes.login, (r) => false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F7EC),
      appBar: AppBar(
        backgroundColor: const Color(0xFFF2F7EC),
        title: const Text('마이페이지', style: TextStyle(fontWeight: FontWeight.w700)),
        actions: [
          TextButton(
            onPressed: _logout,
            child: const Text('로그아웃', style: TextStyle(color: Color(0xFF928E84))),
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? _ErrorBody(error: _error!, onRetry: _load)
              : _Body(
                  user: _user!,
                  preorders: _preorders,
                  onCancel: _cancel,
                ),
    );
  }
}

class _ErrorBody extends StatelessWidget {
  const _ErrorBody({required this.error, required this.onRetry});

  final String error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, size: 48, color: Color(0xFFA34220)),
            const SizedBox(height: 12),
            Text(error, textAlign: TextAlign.center, style: const TextStyle(color: Color(0xFF625E55))),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: onRetry, child: const Text('다시 시도')),
          ],
        ),
      ),
    );
  }
}

class _Body extends StatelessWidget {
  const _Body({
    required this.user,
    required this.preorders,
    required this.onCancel,
  });

  final AuthUser user;
  final List<Map<String, dynamic>> preorders;
  final Future<void> Function(String preorderId) onCancel;

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: () async {},
      child: ListView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 96),
        children: [
          // ── 프로필 카드
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFFE8EDE3),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 28,
                  backgroundColor: const Color(0xFF4A7D1A),
                  child: Text(
                    user.name.isNotEmpty ? user.name[0] : '?',
                    style: const TextStyle(fontSize: 22, color: Colors.white, fontWeight: FontWeight.w700),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(user.name, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: Color(0xFF1E1D18))),
                      const SizedBox(height: 2),
                      Text(user.email, style: const TextStyle(fontSize: 12, color: Color(0xFF625E55))),
                      const SizedBox(height: 4),
                      _RoleBadge(role: user.role),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // ── 사전 주문 섹션 (consumer only)
          if (user.role == 'consumer') ...[
            const SizedBox(height: 22),
            Text(
              '내 사전 주문',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                    color: const Color(0xFF1E1D18),
                  ),
            ),
            const SizedBox(height: 10),
            if (preorders.isEmpty)
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: const Color(0xFFEBF3E3),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: const Center(
                  child: Text('사전 주문 내역이 없습니다.', style: TextStyle(color: Color(0xFF928E84))),
                ),
              )
            else
              ...preorders.map((p) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: _PreorderCard(preorder: p, onCancel: onCancel),
                  )),
          ],
        ],
      ),
    );
  }
}

class _RoleBadge extends StatelessWidget {
  const _RoleBadge({required this.role});
  final String role;

  @override
  Widget build(BuildContext context) {
    final label = switch (role) {
      'consumer' => '소비자',
      'merchant' => '상인',
      'operator' => '운영자',
      _ => role,
    };
    final color = switch (role) {
      'merchant' => const Color(0xFF2F5710),
      'operator' => const Color(0xFF1A3A6B),
      _ => const Color(0xFF4A7D1A),
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha:0.12),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(label, style: TextStyle(fontSize: 11, color: color, fontWeight: FontWeight.w700)),
    );
  }
}

class _PreorderCard extends StatelessWidget {
  const _PreorderCard({required this.preorder, required this.onCancel});

  final Map<String, dynamic> preorder;
  final Future<void> Function(String) onCancel;

  @override
  Widget build(BuildContext context) {
    final status = preorder['status'] as String? ?? '';
    final isRequested = status == 'requested';

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE8EDE3)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        preorder['product_name'] as String? ?? '',
                        style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF1E1D18)),
                      ),
                    ),
                    _StatusBadge(status: status),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  '${preorder['store_name'] ?? ''} · ${preorder['qty']}개',
                  style: const TextStyle(fontSize: 12, color: Color(0xFF625E55)),
                ),
              ],
            ),
          ),
          if (isRequested) ...[
            const SizedBox(width: 8),
            TextButton(
              style: TextButton.styleFrom(
                foregroundColor: const Color(0xFFA34220),
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                minimumSize: Size.zero,
                tapTargetSize: MaterialTapTargetSize.shrinkWrap,
              ),
              onPressed: () => onCancel(preorder['preorder_id'] as String),
              child: const Text('취소', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
            ),
          ],
        ],
      ),
    );
  }
}

class _StatusBadge extends StatelessWidget {
  const _StatusBadge({required this.status});
  final String status;

  @override
  Widget build(BuildContext context) {
    final (label, color) = switch (status) {
      'requested' => ('대기중', const Color(0xFF625E55)),
      'confirmed' => ('확인됨', const Color(0xFF2F5710)),
      'ready'     => ('준비완료', const Color(0xFF1A6B3A)),
      'cancelled' => ('취소', const Color(0xFF928E84)),
      _ => (status, const Color(0xFF928E84)),
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha:0.10),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(label, style: TextStyle(fontSize: 11, color: color, fontWeight: FontWeight.w700)),
    );
  }
}
