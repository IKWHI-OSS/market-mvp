import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../shared/widgets/market_logo_title.dart';

class MerchantProductReviewScreen extends StatefulWidget {
  const MerchantProductReviewScreen({super.key});

  @override
  State<MerchantProductReviewScreen> createState() => _MerchantProductReviewScreenState();
}

class _MerchantProductReviewScreenState extends State<MerchantProductReviewScreen> {
  final _nameController = TextEditingController(text: '산지 직송 유기농 표고버섯');
  final _priceController = TextEditingController(text: '12000');
  final _descriptionController = TextEditingController(
    text: '오늘 아침 강원도 숲에서 직접 채취한 무농약 표고버섯입니다. 육질이 단단하고 향이 매우 깊습니다. 된장찌개나 구이용으로 강력 추천드립니다.',
  );
  String _category = '신선 채소';

  @override
  void dispose() {
    _nameController.dispose();
    _priceController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _onPublish() async {
    await showModalBottomSheet<void>(
      context: context,
      backgroundColor: const Color(0xFFFDFBF5),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.fromLTRB(16, 14, 16, 22),
          child: Row(
            children: [
              const CircleAvatar(
                radius: 16,
                backgroundColor: Color(0xFFDFF0CF),
                child: Icon(Icons.check_circle, color: Color(0xFF2F5710), size: 20),
              ),
              const SizedBox(width: 10),
              const Expanded(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('상품 등록 준비 완료', style: TextStyle(fontSize: 13, color: Color(0xFF1E1D18), fontWeight: FontWeight.w800)),
                    SizedBox(height: 2),
                    Text('모든 정보가 구조화되었습니다.', style: TextStyle(fontSize: 12, color: Color(0xFF625E55))),
                  ],
                ),
              ),
              IconButton(
                onPressed: () => Navigator.pop(context),
                icon: const Icon(Icons.close, size: 18),
              ),
            ],
          ),
        );
      },
    );
    if (!mounted) return;
    Navigator.pushNamedAndRemoveUntil(
      context,
      AppRoutes.merchantDashboard,
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F7EC),
      appBar: AppBar(
        title: const MarketLogoTitle(),
        actions: const [
          Padding(
            padding: EdgeInsets.only(right: 6),
            child: Icon(Icons.notifications_none),
          ),
        ],
      ),
      body: SafeArea(
        top: false,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 22),
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(
                color: const Color(0xFFF5CDB5),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text(
                'AI ANALYSIS COMPLETE',
                style: TextStyle(fontSize: 11, color: Color(0xFFA34220), fontWeight: FontWeight.w800, letterSpacing: 0.5),
              ),
            ),
            const SizedBox(height: 10),
            Text(
              '분석 결과 검토',
              style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                    color: const Color(0xFF1E1D18),
                  ),
            ),
            const SizedBox(height: 6),
            const Text(
              'AI가 사진과 음성을 토대로 정보를 정리했습니다.\n내용을 확인하고 필요한 부분을 수정해주세요.',
              style: TextStyle(fontSize: 13, color: Color(0xFF625E55), height: 1.4),
            ),
            const SizedBox(height: 12),
            _PreviewCard(),
            const SizedBox(height: 14),
            const _FieldLabel('PRODUCT NAME'),
            const SizedBox(height: 6),
            TextField(
              controller: _nameController,
              decoration: const InputDecoration(
                isDense: true,
                filled: true,
                fillColor: Color(0xFFFDFBF5),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.all(Radius.circular(10)),
                  borderSide: BorderSide(color: Color(0xFFA8D175)),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.all(Radius.circular(10)),
                  borderSide: BorderSide(color: Color(0xFFA8D175)),
                ),
              ),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const _FieldLabel('CATEGORY'),
                      const SizedBox(height: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10),
                        decoration: BoxDecoration(
                          color: const Color(0xFFE8EDE3),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: DropdownButton<String>(
                          value: _category,
                          isExpanded: true,
                          underline: const SizedBox.shrink(),
                          items: const [
                            DropdownMenuItem(value: '신선 채소', child: Text('신선 채소')),
                            DropdownMenuItem(value: '과일', child: Text('과일')),
                            DropdownMenuItem(value: '수산', child: Text('수산')),
                          ],
                          onChanged: (value) {
                            if (value == null) return;
                            setState(() => _category = value);
                          },
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const _FieldLabel('SUGGESTED PRICE'),
                      const SizedBox(height: 6),
                      TextField(
                        controller: _priceController,
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(
                          isDense: true,
                          filled: true,
                          fillColor: Color(0xFFE8EDE3),
                          suffixText: '원',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.all(Radius.circular(10)),
                            borderSide: BorderSide.none,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            const _FieldLabel('DESCRIPTION'),
            const SizedBox(height: 6),
            TextField(
              controller: _descriptionController,
              minLines: 4,
              maxLines: 6,
              decoration: const InputDecoration(
                filled: true,
                fillColor: Color(0xFFE8EDE3),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.all(Radius.circular(10)),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 18),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: _onPublish,
                style: FilledButton.styleFrom(
                  minimumSize: const Size.fromHeight(50),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                ),
                child: const Text('이대로 게시하기'),
              ),
            ),
            const SizedBox(height: 10),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: () => Navigator.pushNamed(
                  context,
                  AppRoutes.merchantProductForm,
                ),
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size.fromHeight(44),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                child: const Text('수정하기'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PreviewCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: const Color(0xFFFDFBF5),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Stack(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(14),
            child: Image.network(
              'https://images.unsplash.com/photo-1504545102780-26774c1bb073?auto=format&fit=crop&w=1000&q=80',
              height: 260,
              width: double.infinity,
              fit: BoxFit.cover,
            ),
          ),
          Positioned(
            top: 8,
            left: 8,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: const Color(0xFFFDFBF5),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Text(
                '98% 일치',
                style: TextStyle(fontSize: 11, color: Color(0xFFA34220), fontWeight: FontWeight.w800),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _FieldLabel extends StatelessWidget {
  const _FieldLabel(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: const TextStyle(
        fontSize: 10,
        color: Color(0xFF928E84),
        letterSpacing: 0.5,
        fontWeight: FontWeight.w800,
      ),
    );
  }
}
