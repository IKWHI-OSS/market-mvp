import 'package:flutter/material.dart';

import '../../app/router.dart';

class ShoppingListScreen extends StatefulWidget {
  const ShoppingListScreen({super.key});

  @override
  State<ShoppingListScreen> createState() => _ShoppingListScreenState();
}

class _ShoppingListScreenState extends State<ShoppingListScreen> {
  final _items = <_ShoppingItem>[
    _ShoppingItem(name: '유기농 햇감자', qty: 2, unit: '개', checked: false, price: 8500, storeStatus: 'A구역: 채소'),
    _ShoppingItem(name: '무항생제 달걀 15구', qty: 1, unit: '팩', checked: true, price: 6800, storeStatus: 'B구역: 축산'),
    _ShoppingItem(name: '샤인머스켓 1송이', qty: 1, unit: '송이', checked: false, price: 12000, storeStatus: 'A구역: 과일'),
    _ShoppingItem(name: '대파 한 단', qty: 1, unit: '단', checked: false, price: 3200, storeStatus: 'A구역: 채소'),
    _ShoppingItem(name: '두부 (재개봉)', qty: 1, unit: '모', checked: false, price: 3500, storeStatus: 'C구역: 가공'),
  ];

  int get _totalPrice => _items.fold<int>(0, (sum, item) => sum + (item.price * item.qty));

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5EB),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(14, 8, 14, 28),
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
                  child: const Icon(Icons.arrow_back, color: Color(0xFF4C792F)),
                ),
                const SizedBox(width: 8),
                const Text(
                  '나의 장보기 리스트',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF4C792F)),
                ),
                const Spacer(),
                InkWell(
                  onTap: () => Navigator.pushNamed(context, AppRoutes.notification),
                  borderRadius: BorderRadius.circular(12),
                  child: const Icon(Icons.notifications_none, color: Color(0xFF4C792F)),
                ),
              ],
            ),
            const SizedBox(height: 18),
            Text(
              '장보기 리스트',
              style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                    color: const Color(0xFF3F7422),
                    height: 1.0,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              '총 ${_items.length}개 품목 / 예상 비용 ${_totalPrice.toString()}원',
              style: const TextStyle(fontSize: 17, color: Color(0xFF5F665C), fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: () => Navigator.pushNamed(context, AppRoutes.route),
                    icon: const Icon(Icons.accessibility_new, size: 18),
                    label: const Text('동선 추천받기'),
                    style: FilledButton.styleFrom(
                      backgroundColor: const Color(0xFF2F7312),
                      minimumSize: const Size.fromHeight(45),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: FilledButton.tonalIcon(
                    onPressed: () => Navigator.pushNamed(context, AppRoutes.search),
                    icon: const Icon(Icons.add, size: 18),
                    label: const Text('품목 추가'),
                    style: FilledButton.styleFrom(
                      backgroundColor: const Color(0xFFECEFE8),
                      foregroundColor: const Color(0xFF4C6141),
                      minimumSize: const Size.fromHeight(45),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 18),
            Row(
              children: [
                Text(
                  '필수 품목',
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(color: const Color(0xFF2B2E2A)),
                ),
              ],
            ),
            const SizedBox(height: 10),
            ..._items.map(_buildItemCard),
            const SizedBox(height: 8),
            GestureDetector(
              onTap: () => Navigator.pushNamed(context, AppRoutes.route),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(14),
                child: Stack(
                  children: [
                    Image.network(
                      'https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=1200&q=80',
                      height: 120,
                      width: double.infinity,
                      fit: BoxFit.cover,
                    ),
                    Positioned.fill(
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.topCenter,
                            end: Alignment.bottomCenter,
                            colors: [
                              Colors.black.withValues(alpha: 0.12),
                              Colors.black.withValues(alpha: 0.52),
                            ],
                          ),
                        ),
                      ),
                    ),
                    const Positioned(
                      left: 12,
                      bottom: 10,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('MARKET FLOW', style: TextStyle(fontSize: 10, color: Color(0xFFE6EAE0), fontWeight: FontWeight.w700, letterSpacing: 1)),
                          SizedBox(height: 2),
                          Text('최적 동선 확인하기', style: TextStyle(fontSize: 24, color: Colors.white, fontWeight: FontWeight.w900)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.small(
        onPressed: () {},
        backgroundColor: const Color(0xFFA64A1F),
        child: const Icon(Icons.share, color: Colors.white),
      ),
    );
  }

  Widget _buildItemCard(_ShoppingItem item) {
    return Stack(
      children: [
        Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFFE8EDE1),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        children: [
          InkWell(
            onTap: () => setState(() => item.checked = !item.checked),
            child: Container(
              width: 23,
              height: 23,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: item.checked ? const Color(0xFF3D7721) : Colors.transparent,
                border: Border.all(color: item.checked ? const Color(0xFF3D7721) : const Color(0xFFB6BCAE)),
              ),
              child: item.checked ? const Icon(Icons.check, size: 15, color: Colors.white) : null,
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item.name, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: Color(0xFF374036))),
                const SizedBox(height: 5),
                Row(
                  children: [
                    _QtyStepper(
                      qty: item.qty,
                      onMinus: () => setState(() {
                        if (item.qty > 1) {
                          item.qty -= 1;
                        }
                      }),
                      onPlus: () => setState(() => item.qty += 1),
                    ),
                    const Spacer(),
                    Text(item.storeStatus, style: const TextStyle(fontSize: 11, color: Color(0xFFAF6B47), fontWeight: FontWeight.w700)),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Text('${(item.price * item.qty).toString()}원', style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: Color(0xFF5A6158))),
        ],
      ),
        ),
        if (item.checked)
          Positioned.fill(
            child: Container(
              margin: const EdgeInsets.only(bottom: 10),
              decoration: BoxDecoration(
                color: Colors.black.withValues(alpha: 0.16),
                borderRadius: BorderRadius.circular(14),
              ),
            ),
          ),
      ],
    );
  }
}

class _QtyStepper extends StatelessWidget {
  const _QtyStepper({
    required this.qty,
    required this.onMinus,
    required this.onPlus,
  });

  final int qty;
  final VoidCallback onMinus;
  final VoidCallback onPlus;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 25,
      padding: const EdgeInsets.symmetric(horizontal: 5),
      decoration: BoxDecoration(
        color: const Color(0xFFDCE4D2),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        children: [
          GestureDetector(
            onTap: onMinus,
            child: const Icon(Icons.remove, size: 15, color: Color(0xFF677562)),
          ),
          const SizedBox(width: 8),
          Text('$qty', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
          const SizedBox(width: 8),
          GestureDetector(
            onTap: onPlus,
            child: const Icon(Icons.add, size: 15, color: Color(0xFF677562)),
          ),
        ],
      ),
    );
  }
}

class _ShoppingItem {
  _ShoppingItem({
    required this.name,
    required this.qty,
    required this.unit,
    required this.checked,
    required this.price,
    required this.storeStatus,
  });

  final String name;
  int qty;
  final String unit;
  bool checked;
  final int price;
  final String storeStatus;
}
