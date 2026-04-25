import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../core/network/api_client.dart';
import '../../shared/widgets/error_state.dart';
import '../../shared/widgets/market_logo_title.dart';
import '../search/product_detail_screen.dart';

class DropListScreen extends StatefulWidget {
  const DropListScreen({super.key});

  @override
  State<DropListScreen> createState() => _DropListScreenState();
}

class _DropListScreenState extends State<DropListScreen> {
  late Future<List<DropData>> _future;
  int _tabIndex = 0;

  @override
  void initState() {
    super.initState();
    _future = ApiClient.instance.getDrops();
  }

  Future<void> _reload() async {
    setState(() {
      _future = ApiClient.instance.getDrops();
    });
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'scheduled':
        return '예정';
      case 'arrived':
        return '판매중';
      case 'sold_out':
        return '마감';
      default:
        return '확인중';
    }
  }

  String _statusKicker(String status) {
    switch (status) {
      case 'scheduled':
        return '입고 예정';
      case 'arrived':
        return '판매중';
      case 'sold_out':
        return '마감 임박';
      default:
        return '업데이트';
    }
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'scheduled':
        return const Color(0xFF3B7A1E);
      case 'arrived':
        return const Color(0xFF3A7E1F);
      case 'sold_out':
        return const Color(0xFFB35B3E);
      default:
        return const Color(0xFF697167);
    }
  }

  List<DropData> _applyFilter(List<DropData> all) {
    switch (_tabIndex) {
      case 1:
        return all.where((e) => e.status == 'scheduled').toList(growable: false);
      case 2:
        return all.where((e) => e.status == 'arrived').toList(growable: false);
      default:
        return all;
    }
  }

  Future<void> _toggleSubscription(DropData drop) async {
    await ApiClient.instance.setDropSubscription(dropId: drop.dropId, subscribe: !drop.isSubscribed);
    if (!mounted) {
      return;
    }
    await _reload();
    if (!mounted) {
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(drop.isSubscribed ? '알림 구독을 해제했어요.' : '알림 구독 완료')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5EB),
      body: SafeArea(
        child: FutureBuilder<List<DropData>>(
          future: _future,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return ErrorStateWidget(
                title: '드랍 정보를 불러오지 못했어요',
                description: '잠시 후 다시 시도해주세요.',
                onRetry: _reload,
                onSecondary: () => Navigator.pushNamed(context, AppRoutes.notification),
                secondaryLabel: '알림함 이동',
              );
            }

            final all = snapshot.data ?? const <DropData>[];
            final items = _applyFilter(all);
            if (items.isEmpty) {
              return ListView(
                padding: const EdgeInsets.fromLTRB(14, 10, 14, 20),
                children: [
                  _Header(onNotification: () => Navigator.pushNamed(context, AppRoutes.notification)),
                  const SizedBox(height: 10),
                  Text(
                    '금주의 드랍',
                    style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                          color: const Color(0xFF457A27),
                          height: 1.02,
                        ),
                  ),
                  const SizedBox(height: 6),
                  const Text('현재 예정된 드랍 이벤트가 없어요.', style: TextStyle(fontSize: 14, color: Color(0xFF6F766D))),
                  const SizedBox(height: 18),
                  _FilterTabs(current: _tabIndex, onChange: (idx) => setState(() => _tabIndex = idx)),
                  const SizedBox(height: 18),
                  Container(
                    padding: const EdgeInsets.all(18),
                    decoration: BoxDecoration(
                      color: const Color(0xFFE8EDE3),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Column(
                      children: [
                        const Icon(Icons.inventory_2_outlined, size: 30, color: Color(0xFF8F968D)),
                        const SizedBox(height: 8),
                        const Text('현재 예정된 드랍이 없습니다', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF5C6359))),
                        const SizedBox(height: 6),
                        const Text('실시간 신규 입고를 설정하면\n가장 먼저 알려드릴게요.', textAlign: TextAlign.center, style: TextStyle(fontSize: 12, color: Color(0xFF80877D))),
                        const SizedBox(height: 10),
                        FilledButton.tonal(
                          onPressed: () => Navigator.pushNamed(context, AppRoutes.search),
                          style: FilledButton.styleFrom(
                            backgroundColor: const Color(0xFFDCE8CF),
                            foregroundColor: const Color(0xFF3F6E23),
                          ),
                          child: const Text('대체 인기 상품 확인'),
                        ),
                      ],
                    ),
                  ),
                ],
              );
            }

            return ListView(
              padding: const EdgeInsets.fromLTRB(14, 10, 14, 20),
              children: [
                _Header(onNotification: () => Navigator.pushNamed(context, AppRoutes.notification)),
                const SizedBox(height: 10),
                Text(
                  '금주의 드랍',
                  style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                        color: const Color(0xFF457A27),
                        height: 1.02,
                      ),
                ),
                const SizedBox(height: 6),
                Container(
                  width: 132,
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(color: const Color(0xFFE2E8DA), borderRadius: BorderRadius.circular(13)),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.access_time, size: 12, color: Color(0xFF697167)),
                      SizedBox(width: 4),
                      Text('실시간 업데이트 중', style: TextStyle(fontSize: 11, color: Color(0xFF697167), fontWeight: FontWeight.w700)),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                _FilterTabs(current: _tabIndex, onChange: (idx) => setState(() => _tabIndex = idx)),
                const SizedBox(height: 10),
                ...items.map(
                  (drop) => _DropCard(
                    drop: drop,
                    statusLabel: _statusLabel(drop.status),
                    statusKicker: _statusKicker(drop.status),
                    statusColor: _statusColor(drop.status),
                    onTap: () => Navigator.pushNamed(
                      context,
                      AppRoutes.productDetail,
                      arguments: ProductDetailArgs(productId: drop.productId),
                    ),
                    onSubscribeTap: () => _toggleSubscription(drop),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}

class _Header extends StatelessWidget {
  const _Header({required this.onNotification});

  final VoidCallback onNotification;

  @override
  Widget build(BuildContext context) {
    return Row(
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
          child: const Icon(Icons.arrow_back, color: Color(0xFF457A27)),
        ),
        const SizedBox(width: 6),
        const SizedBox(
          height: 37,
          child: Align(
            alignment: Alignment.centerLeft,
            child: MarketLogoTitle(),
          ),
        ),
        const Spacer(),
        InkWell(
          onTap: onNotification,
          borderRadius: BorderRadius.circular(12),
          child: const Icon(Icons.notifications_none, size: 18, color: Color(0xFF457A27)),
        ),
      ],
    );
  }
}

class _FilterTabs extends StatelessWidget {
  const _FilterTabs({required this.current, required this.onChange});

  final int current;
  final ValueChanged<int> onChange;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        _tabButton(label: '전체', idx: 0),
        const SizedBox(width: 8),
        _tabButton(label: '예정', idx: 1),
        const SizedBox(width: 8),
        _tabButton(label: '판매중', idx: 2),
      ],
    );
  }

  Widget _tabButton({required String label, required int idx}) {
    final selected = current == idx;
    return GestureDetector(
      onTap: () => onChange(idx),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
        decoration: BoxDecoration(
          color: selected ? const Color(0xFF4A7C2C) : const Color(0xFFE4E9DE),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w700,
            color: selected ? Colors.white : const Color(0xFF6E7769),
          ),
        ),
      ),
    );
  }
}

class _DropCard extends StatelessWidget {
  const _DropCard({
    required this.drop,
    required this.statusLabel,
    required this.statusKicker,
    required this.statusColor,
    required this.onTap,
    required this.onSubscribeTap,
  });

  final DropData drop;
  final String statusLabel;
  final String statusKicker;
  final Color statusColor;
  final VoidCallback onTap;
  final VoidCallback onSubscribeTap;

  String _displayDateTime(String raw) {
    final tryParse = DateTime.tryParse(raw);
    if (tryParse == null) {
      return raw.replaceFirst('T', ' ').split('.').first;
    }
    final d = tryParse.toLocal();
    final month = d.month.toString().padLeft(2, '0');
    final day = d.day.toString().padLeft(2, '0');
    final hour = d.hour.toString().padLeft(2, '0');
    final minute = d.minute.toString().padLeft(2, '0');
    return '${d.year}-$month-$day $hour:$minute';
  }

  String _imageUrl(String productId) {
    switch (productId) {
      case 'product_002':
        return 'https://images.unsplash.com/photo-1607305387299-a3d9611cd469?auto=format&fit=crop&w=1200&q=80';
      case 'product_003':
        return 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1200&q=80';
      default:
        return 'https://images.unsplash.com/photo-1601004890684-d8cbf643f5f2?auto=format&fit=crop&w=1200&q=80';
    }
  }

  @override
  Widget build(BuildContext context) {
    final subscribed = drop.isSubscribed;
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ClipRRect(
              borderRadius: const BorderRadius.vertical(top: Radius.circular(14)),
              child: Stack(
                children: [
                  Image.network(
                    _imageUrl(drop.productId),
                    width: double.infinity,
                    height: 165,
                    fit: BoxFit.cover,
                  ),
                  Positioned(
                    left: 8,
                    top: 8,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: statusColor,
                        borderRadius: BorderRadius.circular(11),
                      ),
                      child: Text(
                        '$statusKicker · ${_displayDateTime(drop.expectedAt)}',
                        style: const TextStyle(fontSize: 10, color: Colors.white, fontWeight: FontWeight.w700),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          drop.productName,
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF2D332B)),
                        ),
                      ),
                      Text(statusLabel, style: TextStyle(fontSize: 12, color: statusColor, fontWeight: FontWeight.w700)),
                    ],
                  ),
                  const SizedBox(height: 3),
                  Text(
                    '${drop.storeName}에서 입고 예정. 예상가 ₩${drop.estimatedPrice}',
                    style: const TextStyle(fontSize: 12, color: Color(0xFF7D8577)),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(subscribed ? Icons.notifications_active : Icons.notifications_none, size: 16, color: const Color(0xFF6A7465)),
                      const SizedBox(width: 4),
                      Text(subscribed ? '알림 설정됨' : '알림 설정', style: const TextStyle(fontSize: 11, color: Color(0xFF6A7465))),
                      const Spacer(),
                      FilledButton.tonal(
                        onPressed: onSubscribeTap,
                        style: FilledButton.styleFrom(
                          backgroundColor: subscribed ? const Color(0xFFF7D6C5) : const Color(0xFFDCE9D1),
                          foregroundColor: subscribed ? const Color(0xFF9A4D32) : const Color(0xFF376D1A),
                          minimumSize: const Size(118, 30),
                          padding: const EdgeInsets.symmetric(horizontal: 12),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                        ),
                        child: Text(subscribed ? '알림 해제' : '알림 받기'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
