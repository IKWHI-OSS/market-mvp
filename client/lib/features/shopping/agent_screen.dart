import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../core/network/api_client.dart';
import '../../shared/widgets/market_logo_title.dart';
import '../home/spotlight_screen.dart';

class AgentScreen extends StatefulWidget {
  const AgentScreen({super.key});

  @override
  State<AgentScreen> createState() => _AgentScreenState();
}

class _AgentScreenState extends State<AgentScreen> {
  final TextEditingController _queryController = TextEditingController();
  String _userQuery = '';
  bool _loading = false;
  ShoppingAgentData? _result;

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    _queryController.dispose();
    super.dispose();
  }

  Future<void> _submitQuery() async {
    final query = _queryController.text.trim();
    if (query.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('질문을 입력해 주세요.')),
      );
      return;
    }

    setState(() {
      _userQuery = query;
      _loading = true;
    });
    try {
      final data = await ApiClient.instance.requestShoppingAgent(
        query: query,
        people: 2,
        budget: 20000,
        saveAsList: true,
      );
      if (!mounted) return;
      setState(() => _result = data);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('추천 생성 실패: $e')),
      );
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _openStoreDetail(String? storeId) {
    if (storeId == null || storeId.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('점포 상세 정보가 없습니다.')),
      );
      return;
    }
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => SpotlightScreen(storeId: storeId)),
    );
  }

  void _openShoppingList() {
    Navigator.pushNamed(context, AppRoutes.shoppingList);
  }

  void _startRoute() {
    if ((_result?.shoppingListId ?? '').isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('리스트 생성 후 동선을 시작할 수 있어요.')),
      );
      return;
    }
    Navigator.pushNamed(context, AppRoutes.route);
  }

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final dateLabel = _koreanDate(now);
    final timeLabel = _koreanTime(now);
    final topMessage = _loading
        ? '장보기 추천을 생성하고 있어요...'
        : (_result?.clarificationNeeded ?? false)
            ? (_result?.clarificationQuestion ?? '원하시는 메뉴 유형을 조금 더 알려주세요.')
            : (_result?.menuReason ??
                '추천 메뉴, 재료 리스트, 매칭 점포를 한 번에 확인해보세요.');

    return Scaffold(
      backgroundColor: const Color(0xFFF2F7EC),
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(14, 8, 14, 10),
              child: Row(
                children: [
                  InkWell(
                    onTap: () {
                      if (Navigator.canPop(context)) {
                        Navigator.pop(context);
                        return;
                      }
                      Navigator.pushNamed(context, AppRoutes.home);
                    },
                    borderRadius: BorderRadius.circular(12),
                    child: const Icon(Icons.arrow_back, color: Color(0xFF3E7C18)),
                  ),
                  const SizedBox(width: 8),
                  const SizedBox(
                    height: 37,
                    child: Align(
                      alignment: Alignment.centerLeft,
                      child: MarketLogoTitle(),
                    ),
                  ),
                  const Spacer(),
                  InkWell(
                    onTap: () =>
                        Navigator.pushNamed(context, AppRoutes.notification),
                    borderRadius: BorderRadius.circular(12),
                    child: const Icon(Icons.notifications_none,
                        size: 20, color: Color(0xFF3E7C18)),
                  ),
                ],
              ),
            ),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(12, 8, 12, 16),
                children: [
                  Center(
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 14, vertical: 6),
                      decoration: BoxDecoration(
                        color: const Color(0xFFE2E9DD),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Text(
                        dateLabel,
                        style: const TextStyle(
                            fontSize: 13,
                            color: Color(0xFF61695C),
                            fontWeight: FontWeight.w700),
                      ),
                    ),
                  ),
                  const SizedBox(height: 14),
                  if (_userQuery.isNotEmpty) ...[
                    Align(
                      alignment: Alignment.centerRight,
                      child: Container(
                        constraints: const BoxConstraints(maxWidth: 270),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 12),
                        decoration: BoxDecoration(
                          color: const Color(0xFF3E7C18),
                          borderRadius: BorderRadius.circular(22),
                        ),
                        child: Text(
                          _userQuery,
                          style: const TextStyle(
                              fontSize: 17,
                              color: Colors.white,
                              fontWeight: FontWeight.w700),
                        ),
                      ),
                    ),
                    const SizedBox(height: 6),
                    Align(
                      alignment: Alignment.centerRight,
                      child: Text(timeLabel,
                          style: const TextStyle(
                              fontSize: 12, color: Color(0xFF7A8376))),
                    ),
                    const SizedBox(height: 10),
                  ],
                  const Row(
                    children: [
                      CircleAvatar(
                        radius: 16,
                        backgroundColor: Color(0xFF3E7C18),
                        child: Icon(Icons.auto_awesome,
                            size: 18, color: Colors.white),
                      ),
                      SizedBox(width: 10),
                      Text(
                        '장보기 에이전트',
                        style: TextStyle(
                            fontSize: 28,
                            color: Color(0xFF2E5F12),
                            fontWeight: FontWeight.w900),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFFE1E8DD),
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: Text(
                      topMessage,
                      style: const TextStyle(
                          fontSize: 17,
                          color: Color(0xFF3C4437),
                          height: 1.35),
                    ),
                  ),
                  const SizedBox(height: 14),
                  if (_loading)
                    const Center(child: CircularProgressIndicator())
                  else
                    _RecommendationCard(
                      result: _result,
                      onStoreTap: _openStoreDetail,
                      onStartRoute: _startRoute,
                      onOpenList: _openShoppingList,
                    ),
                  const SizedBox(height: 8),
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(timeLabel,
                        style: const TextStyle(
                            fontSize: 12, color: Color(0xFF7A8376))),
                  ),
                  const SizedBox(height: 10),
                  const Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      _QuickChip(icon: Icons.eco_outlined, label: '제철 반찬'),
                      _QuickChip(icon: Icons.savings_outlined, label: '1만원 이하'),
                      _QuickChip(icon: Icons.restaurant_menu, label: '2인 찌개 재료'),
                    ],
                  ),
                  const SizedBox(height: 12),
                ],
              ),
            ),
            Container(
              color: const Color(0xFFF2F7EC),
              padding: const EdgeInsets.fromLTRB(12, 0, 12, 8),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFFE7EDE0),
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.08),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    IconButton(
                      onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('첨부 기능은 준비 중입니다.')),
                      ),
                      icon: const Icon(Icons.add_circle_outline,
                          color: Color(0xFF6C7467)),
                    ),
                    Expanded(
                      child: TextField(
                        controller: _queryController,
                        decoration: const InputDecoration(
                          border: InputBorder.none,
                          isDense: true,
                          hintText: 'AI에게 물어보세요...',
                          hintStyle: TextStyle(color: Color(0xFF7B8377)),
                        ),
                        onSubmitted: (_) => _submitQuery(),
                      ),
                    ),
                    IconButton(
                      onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('음성 입력은 준비 중입니다.')),
                      ),
                      icon: const Icon(Icons.mic_none,
                          color: Color(0xFF6C7467)),
                    ),
                    SizedBox(
                      width: 42,
                      height: 42,
                      child: FilledButton(
                        onPressed: _submitQuery,
                        style: FilledButton.styleFrom(
                          padding: EdgeInsets.zero,
                          backgroundColor: const Color(0xFF3E7C18),
                          shape: const CircleBorder(),
                        ),
                        child: const Icon(Icons.send_rounded, size: 20),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: 2,
        onDestinationSelected: (value) {
          switch (value) {
            case 0:
              Navigator.pushNamedAndRemoveUntil(
                  context, AppRoutes.consumerShell, (route) => false);
              break;
            case 1:
              Navigator.pushNamed(context, AppRoutes.search);
              break;
            case 2:
              break;
            case 3:
              Navigator.pushNamed(context, AppRoutes.route);
              break;
            case 4:
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('마이페이지는 Phase 2에서 제공돼요.')),
              );
              break;
          }
        },
        destinations: const [
          NavigationDestination(
              icon: Icon(Icons.home_outlined),
              selectedIcon: Icon(Icons.home),
              label: '홈'),
          NavigationDestination(
              icon: Icon(Icons.search), label: '검색'),
          NavigationDestination(
              icon: Icon(Icons.shopping_bag_outlined),
              selectedIcon: Icon(Icons.shopping_bag),
              label: '장보기'),
          NavigationDestination(
              icon: Icon(Icons.map_outlined),
              selectedIcon: Icon(Icons.map),
              label: '지도'),
          NavigationDestination(
              icon: Icon(Icons.person_outline),
              selectedIcon: Icon(Icons.person),
              label: '마이'),
        ],
      ),
    );
  }

  String _koreanDate(DateTime dateTime) {
    const week = ['월', '화', '수', '목', '금', '토', '일'];
    return '${dateTime.year}년 ${dateTime.month}월 ${dateTime.day}일 ${week[dateTime.weekday - 1]}요일';
  }

  String _koreanTime(DateTime dateTime) {
    final isAm = dateTime.hour < 12;
    final hour12 = dateTime.hour % 12 == 0 ? 12 : dateTime.hour % 12;
    final minute = dateTime.minute.toString().padLeft(2, '0');
    return '${isAm ? '오전' : '오후'} $hour12:$minute';
  }
}

class _RecommendationCard extends StatelessWidget {
  const _RecommendationCard({
    required this.result,
    required this.onStoreTap,
    required this.onStartRoute,
    required this.onOpenList,
  });

  final ShoppingAgentData? result;
  final ValueChanged<String?> onStoreTap;
  final VoidCallback onStartRoute;
  final VoidCallback onOpenList;

  @override
  Widget build(BuildContext context) {
    final title = result?.menuTitle ?? '추천 메뉴 준비 중';
    final ingredients = result?.ingredients ?? const <ShoppingAgentIngredient>[];
    final stores = result?.storeMatches ?? const <ShoppingAgentStoreMatch>[];
    final showClarification = result?.clarificationNeeded ?? false;
    final total = ingredients.fold<int>(0, (s, i) => s + (i.price ?? 0));

    if (showClarification) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFFF6F7F4),
          borderRadius: BorderRadius.circular(24),
        ),
        child: const Text(
          '질문이 조금 모호해서 메뉴를 확정하지 못했어요. 하단 입력창에서 인원/예산/선호를 더 알려주세요.',
          style: TextStyle(fontSize: 16, color: Color(0xFF3C4437), height: 1.35),
        ),
      );
    }

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFFF6F7F4),
        borderRadius: BorderRadius.circular(28),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ClipRRect(
            borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
            child: Stack(
              children: [
                Image.network(
                  'https://images.unsplash.com/photo-1574484284002-952d92456975?auto=format&fit=crop&w=1200&q=80',
                  width: double.infinity,
                  height: 130,
                  fit: BoxFit.cover,
                ),
                Positioned.fill(
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Colors.black.withValues(alpha: 0.04),
                          Colors.black.withValues(alpha: 0.36),
                        ],
                      ),
                    ),
                  ),
                ),
                Positioned(
                  left: 12,
                  right: 12,
                  bottom: 12,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.45),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      title,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                          fontSize: 24,
                          color: Colors.white,
                          fontWeight: FontWeight.w900),
                    ),
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(14, 12, 14, 14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Expanded(
                        child: Text('품목 리스트',
                            style:
                                TextStyle(fontSize: 12, color: Color(0xFF7A8376)))),
                    Text('금액',
                        style: TextStyle(fontSize: 12, color: Color(0xFF7A8376))),
                  ],
                ),
                const SizedBox(height: 10),
                ...ingredients.take(3).map(
                      (i) => Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: _PriceRow(
                          name: i.name,
                          sub: '${i.qty}${i.unit} / ${i.matchStatus == 'matched' ? '매칭완료' : '미매칭'}',
                          price: i.price == null ? '-' : '₩${i.price}',
                        ),
                      ),
                    ),
                const SizedBox(height: 12),
                const Divider(height: 1, color: Color(0xFFD6DED0)),
                const SizedBox(height: 12),
                Row(
                  children: [
                    const Expanded(
                      child: Text('합계 예상',
                          style: TextStyle(
                              fontSize: 18,
                              color: Color(0xFF3E7C18),
                              fontWeight: FontWeight.w800)),
                    ),
                    Text(
                      total > 0 ? '₩$total' : '-',
                      style: const TextStyle(
                          fontSize: 30,
                          color: Color(0xFF3E7C18),
                          fontWeight: FontWeight.w900),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                const Text('추천 매칭 점포',
                    style: TextStyle(
                        fontSize: 13,
                        color: Color(0xFF798274),
                        fontWeight: FontWeight.w700)),
                const SizedBox(height: 8),
                if (stores.isEmpty)
                  const Text(
                    '매칭 점포를 찾지 못해 일반 장보기 리스트를 제공합니다.',
                    style: TextStyle(fontSize: 13, color: Color(0xFF7A8376)),
                  )
                else
                  ...stores.take(2).map(
                        (s) => Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: _StoreTile(
                            icon: Icons.storefront,
                            iconBg: s.stockPriority == 'low_stock'
                                ? const Color(0xFFE2865E)
                                : const Color(0xFF3E7C18),
                            title: '${s.storeName} (${s.zoneLabel})',
                            sub: '${s.distanceM}m  ·  ${s.matchedItems.join(", ")}',
                            onTap: () => onStoreTap(s.storeId),
                          ),
                        ),
                      ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Expanded(
                      child: FilledButton.tonal(
                        onPressed: onOpenList,
                        style: FilledButton.styleFrom(
                          backgroundColor: const Color(0xFFE4EBDD),
                          foregroundColor: const Color(0xFF3E7C18),
                        ),
                        child: const Text('리스트 보기'),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: FilledButton(
                        onPressed: onStartRoute,
                        style: FilledButton.styleFrom(
                          backgroundColor: const Color(0xFF3E7C18),
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(20)),
                        ),
                        child: const Text('이 구성으로 길찾기'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _PriceRow extends StatelessWidget {
  const _PriceRow({required this.name, required this.sub, required this.price});

  final String name;
  final String sub;
  final String price;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(name,
                  style: const TextStyle(
                      fontSize: 18,
                      color: Color(0xFF2A2E27),
                      fontWeight: FontWeight.w700)),
              const SizedBox(height: 2),
              Text(sub,
                  style: const TextStyle(fontSize: 12, color: Color(0xFF6F766D))),
            ],
          ),
        ),
        const SizedBox(width: 10),
        Padding(
          padding: const EdgeInsets.only(top: 2),
          child: Text(price,
              style: const TextStyle(
                  fontSize: 24,
                  color: Color(0xFF252A23),
                  fontWeight: FontWeight.w900)),
        ),
      ],
    );
  }
}

class _StoreTile extends StatelessWidget {
  const _StoreTile({
    required this.icon,
    required this.iconBg,
    required this.title,
    required this.sub,
    required this.onTap,
  });

  final IconData icon;
  final Color iconBg;
  final String title;
  final String sub;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: const Color(0xFFE6ECE0),
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(10, 10, 10, 10),
          child: Row(
            children: [
              CircleAvatar(
                radius: 16,
                backgroundColor: iconBg,
                child: Icon(icon, size: 16, color: Colors.white),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title,
                        style: const TextStyle(
                            fontSize: 14,
                            color: Color(0xFF2D332B),
                            fontWeight: FontWeight.w800)),
                    const SizedBox(height: 2),
                    Text(sub,
                        style: const TextStyle(
                            fontSize: 12, color: Color(0xFF727A6E))),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: Color(0xFF7E8679)),
            ],
          ),
        ),
      ),
    );
  }
}

class _QuickChip extends StatelessWidget {
  const _QuickChip({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFFE3E9DC),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: const Color(0xFF5A634F)),
          const SizedBox(width: 6),
          Text(label,
              style: const TextStyle(
                  fontSize: 13,
                  color: Color(0xFF5A634F),
                  fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}
