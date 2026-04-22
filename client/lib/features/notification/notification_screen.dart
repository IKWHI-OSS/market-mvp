import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../core/network/api_client.dart';
import '../../shared/widgets/error_state.dart';
import '../home/event_screen.dart';
import '../home/spotlight_screen.dart';
import '../search/product_detail_screen.dart';

class NotificationScreen extends StatefulWidget {
  const NotificationScreen({super.key});

  @override
  State<NotificationScreen> createState() => _NotificationScreenState();
}

class _NotificationScreenState extends State<NotificationScreen> {
  late Future<List<NotificationData>> _future;
  int _tabIndex = 0;

  @override
  void initState() {
    super.initState();
    _future = ApiClient.instance.getNotifications();
  }

  Future<void> _refresh() async {
    setState(() {
      _future = ApiClient.instance.getNotifications();
    });
  }

  Future<void> _markAllRead(List<NotificationData> items) async {
    for (final item in items.where((e) => !e.isRead)) {
      await ApiClient.instance.markNotificationRead(item.notificationId);
    }
    if (!mounted) {
      return;
    }
    await _refresh();
  }

  List<NotificationData> _applyTab(List<NotificationData> all) {
    switch (_tabIndex) {
      case 1:
        return all.where((e) => e.targetType == 'drop').toList(growable: false);
      case 2:
        return all.where((e) => e.targetType == 'preorder').toList(growable: false);
      case 3:
        return all.where((e) => e.targetType != 'drop' && e.targetType != 'preorder').toList(growable: false);
      default:
        return all;
    }
  }

  Future<void> _openNotification(NotificationData item) async {
    await ApiClient.instance.markNotificationRead(item.notificationId);
    if (!mounted) {
      return;
    }
    await _refresh();
    if (!mounted) {
      return;
    }
    switch (item.targetType) {
      case 'product':
        Navigator.pushNamed(
          context,
          AppRoutes.productDetail,
          arguments: ProductDetailArgs(productId: item.targetId),
        );
        break;
      case 'drop':
        Navigator.pushNamed(context, AppRoutes.drop);
        break;
      case 'event':
        Navigator.push(context, MaterialPageRoute(builder: (_) => EventScreen(eventId: item.targetId)));
        break;
      case 'store':
        Navigator.push(context, MaterialPageRoute(builder: (_) => SpotlightScreen(storeId: item.targetId)));
        break;
      default:
        Navigator.pushNamed(context, AppRoutes.home);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5EB),
      body: SafeArea(
        child: FutureBuilder<List<NotificationData>>(
          future: _future,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return ErrorStateWidget(
                title: '알림을 불러오지 못했어요',
                description: '잠시 후 다시 시도해주세요.',
                onRetry: _refresh,
                onSecondary: () => Navigator.pushNamed(context, AppRoutes.home),
                secondaryLabel: '인근 시장 안내',
              );
            }
            final allItems = snapshot.data ?? const <NotificationData>[];
            final items = _applyTab(allItems);
            return ListView(
              padding: const EdgeInsets.fromLTRB(10, 16, 10, 32),
              children: [
                Row(
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
                      child: const Icon(Icons.arrow_back, color: Color(0xFF4A7B29)),
                    ),
                    const SizedBox(width: 6),
                    const Text('알림함', style: TextStyle(fontSize: 23, fontWeight: FontWeight.w900, color: Color(0xFF4A7B29))),
                    const Spacer(),
                    TextButton(
                      onPressed: () => _markAllRead(items),
                      child: const Text('전체 읽음 처리'),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    _tabChip('전체', 0),
                    const SizedBox(width: 8),
                    _tabChip('드랍', 1),
                    const SizedBox(width: 8),
                    _tabChip('주문', 2),
                    const SizedBox(width: 8),
                    _tabChip('정보', 3),
                  ],
                ),
                const SizedBox(height: 18),
                if (items.isEmpty)
                  Container(
                    padding: const EdgeInsets.all(18),
                    decoration: BoxDecoration(
                      color: const Color(0xFFE8EDE3),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: const Column(
                      children: [
                        Icon(Icons.notifications_off_outlined, size: 30, color: Color(0xFF7C8579)),
                        SizedBox(height: 8),
                        Text('새로운 알림이 없습니다', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF5C655A))),
                        SizedBox(height: 4),
                        Text('푸시 실패 시 인앱 알림으로 대체되어 안내됩니다.', style: TextStyle(fontSize: 12, color: Color(0xFF7F877C))),
                      ],
                    ),
                  )
                else
                  ...items.map((item) => _NotificationCard(item: item, onTap: () => _openNotification(item))),
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _tabChip(String label, int idx) {
    final selected = _tabIndex == idx;
    return GestureDetector(
      onTap: () => setState(() => _tabIndex = idx),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: selected ? const Color(0xFF3E7C18) : const Color(0xFFDCE3D6),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w700,
            color: selected ? Colors.white : const Color(0xFF6A7366),
          ),
        ),
      ),
    );
  }
}

class _NotificationCard extends StatelessWidget {
  const _NotificationCard({required this.item, required this.onTap});

  final NotificationData item;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final isGuideCard = item.type == 'event';
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: isGuideCard ? const Color(0xFFDDE6D3) : const Color(0xFFF3F5F0),
        borderRadius: BorderRadius.circular(14),
        border: item.isRead
            ? null
            : Border(
                left: BorderSide(
                  color: item.targetType == 'drop' ? const Color(0xFF3F7B1D) : const Color(0xFFC7744E),
                  width: 3,
                ),
              ),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(12, 12, 12, 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 30,
                    height: 30,
                    decoration: BoxDecoration(
                      color: item.isRead ? const Color(0xFFE1E5DE) : const Color(0xFF9BDC6E),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      item.targetType == 'drop' ? Icons.notifications_active : Icons.info_outline,
                      size: 17,
                      color: item.isRead ? const Color(0xFF8D9689) : const Color(0xFF426726),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      item.title,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: item.isRead ? FontWeight.w600 : FontWeight.w900,
                        color: const Color(0xFF30352F),
                      ),
                    ),
                  ),
                  Text(item.createdAt, style: const TextStyle(fontSize: 11, color: Color(0xFF8A9287))),
                ],
              ),
              const SizedBox(height: 8),
              Text(item.body, style: const TextStyle(fontSize: 13, color: Color(0xFF596156), height: 1.35)),
              const SizedBox(height: 8),
              Row(
                children: [
                  Text(
                    item.isRead ? 'READ' : 'NEW',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: item.isRead ? const Color(0xFF8D9589) : const Color(0xFFC6663A),
                    ),
                  ),
                  const Spacer(),
                  if (isGuideCard)
                    FilledButton(
                      onPressed: onTap,
                      style: FilledButton.styleFrom(
                        backgroundColor: const Color(0xFF3F7B1D),
                        minimumSize: const Size(88, 32),
                      ),
                      child: const Text('리포트 읽기'),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
