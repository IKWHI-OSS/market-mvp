import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../core/network/api_client.dart';
import '../../shared/widgets/market_logo_title.dart';

class MerchantDashboardScreen extends StatefulWidget {
  const MerchantDashboardScreen({super.key});

  @override
  State<MerchantDashboardScreen> createState() => _MerchantDashboardScreenState();
}

class _MerchantDashboardScreenState extends State<MerchantDashboardScreen> {
  bool _loading = true;
  String _name = '';
  int _riskCount = 0;
  List<Map<String, dynamic>> _suggestions = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final user = await ApiClient.instance.getMyProfile();
      final store = await ApiClient.instance.getMyStore();
      final storeId = store['store_id'] as String;
      final products = await ApiClient.instance.getMerchantProducts(storeId);
      final risk = products.where((p) {
        final s = p['stock_status'] as String? ?? '';
        return s == 'low_stock' || s == 'out_of_stock';
      }).length;
      final suggestions = await ApiClient.instance.getPriceSuggestions();
      if (mounted) {
        setState(() {
          _name = user.name;
          _riskCount = risk;
          _suggestions = suggestions;
          _loading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _showPriceSuggestionsSheet() {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFFF2F7EC),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.6,
        maxChildSize: 0.9,
        builder: (_, controller) => _PriceSuggestionsSheet(
          suggestions: _suggestions,
          onApply: (productId, marketPrice) async {
            await ApiClient.instance.updateProduct(productId, price: marketPrice);
            if (mounted) {
              Navigator.pop(context);
              _load();
            }
          },
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        backgroundColor: Color(0xFFF2F7EC),
        body: Center(child: CircularProgressIndicator()),
      );
    }
    return Scaffold(
      backgroundColor: const Color(0xFFF2F7EC),
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded),
          onPressed: () => Navigator.pushNamedAndRemoveUntil(
            context,
            AppRoutes.login,
            (route) => false,
          ),
        ),
        title: const MarketLogoTitle(),
        actions: [
          IconButton(
            onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('알림 기능은 준비 중입니다.')),
            ),
            icon: const Icon(Icons.notifications_none),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 96),
        children: [
          const SizedBox(height: 14),
          Text(
            '반갑습니다, $_name님',
            style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                  fontSize: 36,
                  fontWeight: FontWeight.w800,
                  color: const Color(0xFF2F5710),
                ),
          ),
          const SizedBox(height: 6),
          const Text(
            '오늘의 시장 현황과 관리할 업무를 확인하세요.',
            style: TextStyle(fontSize: 13, color: Color(0xFF625E55)),
          ),
          const SizedBox(height: 14),
          if (_riskCount > 0) ...[
            _AlertCard(riskCount: _riskCount),
            const SizedBox(height: 10),
          ],
          const SizedBox(height: 8),
          Row(
            children: [
              Text(
                '오늘의 할 일',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      color: const Color(0xFF1E1D18),
                    ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: const Color(0xFFE8EDE3),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Text(
                  '3개의 할 일',
                  style: TextStyle(fontSize: 11, color: Color(0xFF625E55), fontWeight: FontWeight.w700),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          _TaskTile(
            icon: Icons.location_on_outlined,
            iconBg: const Color(0xFFDFF0CF),
            title: '신규 드랍 등록',
            subtitle: '설정 안 된 신선 산지 직송 예약',
            onTap: () => ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('드랍 등록 화면은 다음 단계에서 연결됩니다.')),
            ),
          ),
          const SizedBox(height: 8),
          _TaskTile(
            icon: Icons.sell_outlined,
            iconBg: const Color(0xFFF5CDB5),
            title: '가격 정보 갱신',
            subtitle: _suggestions.isEmpty
                ? '시세 기반 제안 없음'
                : '${_suggestions.length}개 상품 가격 제안 있음',
            onTap: _suggestions.isEmpty
                ? () => ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('현재 가격 제안이 없습니다.')),
                    )
                : _showPriceSuggestionsSheet,
          ),
          const SizedBox(height: 8),
          _TaskTile(
            icon: Icons.verified_outlined,
            iconBg: const Color(0xFFE8E5DE),
            title: '상인 스토리 생성',
            subtitle: '점포 소개문 자동 생성 후 검토',
            onTap: () => Navigator.pushNamed(context, AppRoutes.merchantStory),
          ),
          const SizedBox(height: 14),
          _PromoCard(
            onTap: () => Navigator.pushNamed(context, AppRoutes.merchantProductForm),
          ),
        ],
      ),
      floatingActionButton: Padding(
        padding: const EdgeInsets.only(bottom: 20),
        child: FloatingActionButton.extended(
          onPressed: () => Navigator.pushNamed(context, AppRoutes.merchantProductForm),
          backgroundColor: const Color(0xFF4A7D1A),
          foregroundColor: const Color(0xFFF2F7EC),
          icon: const Icon(Icons.add_circle_outline),
          label: const Text('상품 등록'),
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
    );
  }
}

class _AlertCard extends StatelessWidget {
  const _AlertCard({required this.riskCount});

  final int riskCount;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFF5CDB5),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        children: [
          const Icon(Icons.inventory_2_outlined, size: 18, color: Color(0xFFA34220)),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('재고 부족 상품', style: TextStyle(fontSize: 12, color: Color(0xFFA34220), fontWeight: FontWeight.w700)),
                const SizedBox(height: 2),
                Text('$riskCount', style: Theme.of(context).textTheme.headlineLarge?.copyWith(color: const Color(0xFF6E2B12))),
                const Text('품목 보충 필요', style: TextStyle(fontSize: 11, color: Color(0xFFA34220))),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _TaskTile extends StatelessWidget {
  const _TaskTile({
    required this.icon,
    required this.iconBg,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final Color iconBg;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: const Color(0xFFEBF3E3),
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(color: iconBg, shape: BoxShape.circle),
                child: Icon(icon, size: 18, color: const Color(0xFF2F5710)),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF1E1D18))),
                    const SizedBox(height: 2),
                    Text(subtitle, style: const TextStyle(fontSize: 11, color: Color(0xFF625E55))),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: Color(0xFF928E84)),
            ],
          ),
        ),
      ),
    );
  }
}

class _PromoCard extends StatelessWidget {
  const _PromoCard({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Ink(
          height: 118,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            image: const DecorationImage(
              image: NetworkImage('https://images.unsplash.com/photo-1488459716781-31db52582fe9?auto=format&fit=crop&w=1200&q=80'),
              fit: BoxFit.cover,
            ),
          ),
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              gradient: const LinearGradient(
                begin: Alignment.bottomCenter,
                end: Alignment.topCenter,
                colors: [Color(0x9A1E1D18), Color(0x331E1D18)],
              ),
            ),
            padding: const EdgeInsets.all(12),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                Text('드랍 아이템 등록', style: TextStyle(fontSize: 18, color: Color(0xFFF2F7EC), fontWeight: FontWeight.w800)),
                SizedBox(height: 2),
                Text('명산물 제휴에 대한 드랍 게시를 등록해 보세요.', style: TextStyle(fontSize: 11, color: Color(0xFFE8E5DE))),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _PriceSuggestionsSheet extends StatelessWidget {
  const _PriceSuggestionsSheet({required this.suggestions, required this.onApply});

  final List<Map<String, dynamic>> suggestions;
  final Future<void> Function(String productId, int marketPrice) onApply;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 36,
              height: 4,
              decoration: BoxDecoration(
                color: const Color(0xFFCCC9BF),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 16),
          const Text('가격 제안', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: Color(0xFF1E1D18))),
          const SizedBox(height: 12),
          Expanded(
            child: ListView.separated(
              itemCount: suggestions.length,
              separatorBuilder: (_, __) => const SizedBox(height: 8),
              itemBuilder: (_, i) {
                final s = suggestions[i];
                final productId = s['product_id'] as String;
                final productName = s['product_name'] as String? ?? '';
                final currentPrice = s['current_price'] as int? ?? 0;
                final marketPrice = s['market_price'] as int? ?? 0;
                final advice = s['advice'] as String? ?? '';
                return Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFFE8EDE3)),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(productName, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF1E1D18))),
                            const SizedBox(height: 2),
                            Text('현재 $currentPrice원 → 시세 $marketPrice원',
                                style: const TextStyle(fontSize: 11, color: Color(0xFF625E55))),
                            const SizedBox(height: 2),
                            Text(advice, style: const TextStyle(fontSize: 11, color: Color(0xFF928E84))),
                          ],
                        ),
                      ),
                      TextButton(
                        style: TextButton.styleFrom(
                          foregroundColor: const Color(0xFF2F5710),
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          minimumSize: Size.zero,
                          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ),
                        onPressed: () => onApply(productId, marketPrice),
                        child: const Text('적용', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
