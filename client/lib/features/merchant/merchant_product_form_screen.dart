import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../shared/widgets/market_logo_title.dart';

class MerchantProductFormScreen extends StatefulWidget {
  const MerchantProductFormScreen({super.key});

  @override
  State<MerchantProductFormScreen> createState() => _MerchantProductFormScreenState();
}

class _MerchantProductFormScreenState extends State<MerchantProductFormScreen> {
  final _priceController = TextEditingController();
  final _stockController = TextEditingController();
  bool _analyzing = false;

  @override
  void dispose() {
    _priceController.dispose();
    _stockController.dispose();
    super.dispose();
  }

  Future<void> _onAnalyze() async {
    setState(() => _analyzing = true);
    await Future<void>.delayed(const Duration(milliseconds: 450));
    if (!mounted) return;
    setState(() => _analyzing = false);
    Navigator.pushNamed(context, AppRoutes.merchantProductReview);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F7EC),
      appBar: AppBar(
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
      body: SafeArea(
        top: false,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 10, 16, 20),
          children: [
            Text(
              '새로운 상품\n등록하기',
              style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                    color: const Color(0xFF1E1D18),
                    height: 1.1,
                  ),
            ),
            const SizedBox(height: 14),
            _ImageCaptureCard(
              onTap: () => ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('카메라/갤러리 연동은 다음 단계에서 연결됩니다.')),
              ),
            ),
            const SizedBox(height: 10),
            _VoiceInputCard(
              onTap: () => ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('음성 입력 기능은 다음 단계에서 연결됩니다.')),
              ),
            ),
            const SizedBox(height: 18),
            const Row(
              children: [
                Expanded(child: Divider(color: Color(0xFFC8C4BB))),
                Padding(
                  padding: EdgeInsets.symmetric(horizontal: 8),
                  child: Text(
                    '직접 입력 (선택)',
                    style: TextStyle(fontSize: 12, color: Color(0xFF928E84), fontWeight: FontWeight.w600),
                  ),
                ),
                Expanded(child: Divider(color: Color(0xFFC8C4BB))),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _LinedNumberField(
                    label: '단가 (PRICE)',
                    controller: _priceController,
                    suffix: '원',
                  ),
                ),
                const SizedBox(width: 20),
                Expanded(
                  child: _LinedNumberField(
                    label: '재고수량 (STOCK)',
                    controller: _stockController,
                    suffix: '개',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: _analyzing ? null : _onAnalyze,
                icon: const Icon(Icons.auto_awesome_outlined),
                label: Text(_analyzing ? 'AI 분석 중...' : 'AI 분석 시작'),
                style: FilledButton.styleFrom(
                  minimumSize: const Size.fromHeight(50),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                ),
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              '상품 사진이나 음성을 분석하여 상품명, 정보, 특징 등을 생성합니다.',
              style: TextStyle(fontSize: 12, color: Color(0xFF7A8176), height: 1.4),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 10),
            Center(
              child: TextButton(
                onPressed: _analyzing
                    ? null
                    : () => Navigator.pushNamed(context, AppRoutes.merchantProductReview),
                child: const Text('수동 입력으로 계속하기'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ImageCaptureCard extends StatelessWidget {
  const _ImageCaptureCard({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: Ink(
          height: 190,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(18),
            image: const DecorationImage(
              image: NetworkImage('https://images.unsplash.com/photo-1534723328310-e82dad3ee43f?auto=format&fit=crop&w=1200&q=80'),
              fit: BoxFit.cover,
            ),
          ),
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(18),
              color: const Color(0xA3F2F7EC),
            ),
            child: const Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CircleAvatar(
                  radius: 27,
                  backgroundColor: Color(0xFFFDFBF5),
                  child: Icon(Icons.photo_camera_outlined, color: Color(0xFF4A7D1A), size: 26),
                ),
                SizedBox(height: 10),
                Text('사진 찍기', style: TextStyle(fontSize: 30 / 1.75, color: Color(0xFF1E1D18), fontWeight: FontWeight.w800)),
                SizedBox(height: 4),
                Text('AI가 상품의 정보를 자동으로 추출합니다.', style: TextStyle(fontSize: 12, color: Color(0xFF625E55))),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _VoiceInputCard extends StatelessWidget {
  const _VoiceInputCard({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: const Color(0xFFEBF3E3),
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: const Padding(
          padding: EdgeInsets.all(14),
          child: Row(
            children: [
              CircleAvatar(
                radius: 20,
                backgroundColor: Color(0xFFF5CDB5),
                child: Icon(Icons.mic_none, color: Color(0xFFA34220), size: 21),
              ),
              SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('음성으로 등록', style: TextStyle(fontSize: 18 / 1.15, color: Color(0xFF1E1D18), fontWeight: FontWeight.w800)),
                    SizedBox(height: 2),
                    Text('말씀만 하세요. 제가 받아적겠습니다.', style: TextStyle(fontSize: 12, color: Color(0xFF625E55))),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _LinedNumberField extends StatelessWidget {
  const _LinedNumberField({
    required this.label,
    required this.controller,
    required this.suffix,
  });

  final String label;
  final TextEditingController controller;
  final String suffix;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(fontSize: 11, color: Color(0xFF928E84), fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 6),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: controller,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  isDense: true,
                  hintText: '0',
                  border: InputBorder.none,
                ),
              ),
            ),
            Text(
              suffix,
              style: const TextStyle(fontSize: 20, color: Color(0xFF928E84), fontWeight: FontWeight.w700),
            ),
          ],
        ),
        const Divider(color: Color(0xFF928E84), thickness: 1),
      ],
    );
  }
}
