import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../core/network/api_client.dart';
import '../../shared/widgets/market_logo_title.dart';

class MerchantStoryScreen extends StatefulWidget {
  const MerchantStoryScreen({super.key});

  @override
  State<MerchantStoryScreen> createState() => _MerchantStoryScreenState();
}

class _MerchantStoryScreenState extends State<MerchantStoryScreen> {
  final _interviewController = TextEditingController(
    text: '20년째 시장에서 장사하며 제철 식재료를 가장 정직하게 소개하려고 노력합니다.',
  );
  final _keywordController = TextEditingController(text: '제철,신선,정직');
  String _tone = '친근한';
  String _selectedLength = 'normal';
  MerchantStoryData? _result;
  bool _loading = false;

  @override
  void dispose() {
    _interviewController.dispose();
    _keywordController.dispose();
    super.dispose();
  }

  Future<void> _generate() async {
    final interview = _interviewController.text.trim();
    if (interview.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('인터뷰 내용을 입력해주세요.')),
      );
      return;
    }
    final keywords = _keywordController.text
        .split(',')
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty)
        .toList(growable: false);

    setState(() => _loading = true);
    try {
      final data = await ApiClient.instance.createMerchantStory(
        storeId: 'store_001',
        interviewText: interview,
        keywords: keywords,
        tone: _tone,
        selectedLength: _selectedLength,
        saveToStore: false,
      );
      if (!mounted) return;
      setState(() => _result = data);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('스토리 생성 실패: $e')),
      );
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _publish() {
    if (_result == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('먼저 스토리를 생성해주세요.')),
      );
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('스토리를 게시했어요.')),
    );
    Navigator.pushNamedAndRemoveUntil(
      context,
      AppRoutes.merchantDashboard,
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7F6F3),
      appBar: AppBar(
        title: const MarketLogoTitle(),
        actions: [
          IconButton(
            onPressed: () => Navigator.pushNamed(context, AppRoutes.notification),
            icon: const Icon(Icons.notifications_none),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 10, 16, 24),
        children: [
          Text(
            '상인 스토리 에이전트',
            style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                  color: const Color(0xFF2F5710),
                ),
          ),
          const SizedBox(height: 6),
          const Text(
            '인터뷰 입력 + 톤 선택으로 점포 소개문을 자동 생성합니다.',
            style: TextStyle(fontSize: 13, color: Color(0xFF6B685F)),
          ),
          const SizedBox(height: 12),
          _InputCard(
            interviewController: _interviewController,
            keywordController: _keywordController,
            tone: _tone,
            selectedLength: _selectedLength,
            onToneChanged: (v) => setState(() => _tone = v),
            onLengthChanged: (v) => setState(() => _selectedLength = v),
            onGenerate: _loading ? null : _generate,
          ),
          if (_loading) ...[
            const SizedBox(height: 12),
            const Center(child: CircularProgressIndicator()),
          ],
          if (_result != null) ...[
            const SizedBox(height: 12),
            _PreviewCard(result: _result!),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: _publish,
                child: const Text('게시하기'),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _InputCard extends StatelessWidget {
  const _InputCard({
    required this.interviewController,
    required this.keywordController,
    required this.tone,
    required this.selectedLength,
    required this.onToneChanged,
    required this.onLengthChanged,
    required this.onGenerate,
  });

  final TextEditingController interviewController;
  final TextEditingController keywordController;
  final String tone;
  final String selectedLength;
  final ValueChanged<String> onToneChanged;
  final ValueChanged<String> onLengthChanged;
  final VoidCallback? onGenerate;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE3E0D8)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('인터뷰 입력', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
          const SizedBox(height: 8),
          TextField(
            controller: interviewController,
            maxLines: 4,
            decoration: const InputDecoration(
              hintText: '상인 이력, 점포 철학, 대표 상품을 입력하세요.',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 10),
          const Text('키워드 (쉼표 구분)', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
          const SizedBox(height: 8),
          TextField(
            controller: keywordController,
            decoration: const InputDecoration(
              hintText: '예: 제철, 신선, 정직',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 10),
          const Text('톤앤매너', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: ['친근한', '전문적인', '정겨운']
                .map((t) => ChoiceChip(
                      label: Text(t),
                      selected: tone == t,
                      onSelected: (_) => onToneChanged(t),
                    ))
                .toList(growable: false),
          ),
          const SizedBox(height: 10),
          const Text('출력 길이', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
          const SizedBox(height: 8),
          SegmentedButton<String>(
            segments: const [
              ButtonSegment(value: 'short', label: Text('짧음')),
              ButtonSegment(value: 'normal', label: Text('보통')),
              ButtonSegment(value: 'detailed', label: Text('상세')),
            ],
            selected: {selectedLength},
            onSelectionChanged: (v) => onLengthChanged(v.first),
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: FilledButton(
              onPressed: onGenerate,
              child: const Text('스토리 생성하기'),
            ),
          ),
        ],
      ),
    );
  }
}

class _PreviewCard extends StatelessWidget {
  const _PreviewCard({required this.result});
  final MerchantStoryData result;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE3E0D8)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('결과 미리보기', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
          const SizedBox(height: 8),
          Text(
            result.story,
            style: const TextStyle(fontSize: 14, color: Color(0xFF35322C), height: 1.45),
          ),
          const SizedBox(height: 10),
          if (result.interviewMasked.isNotEmpty)
            Text(
              '마스킹 적용: ${result.interviewMasked}',
              style: const TextStyle(fontSize: 12, color: Color(0xFF7C6B62)),
            ),
          if (result.hashtags.isNotEmpty) ...[
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: result.hashtags
                  .map((tag) => Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                        decoration: BoxDecoration(
                          color: const Color(0xFFE6EDE0),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          tag,
                          style: const TextStyle(fontSize: 12, color: Color(0xFF486938), fontWeight: FontWeight.w700),
                        ),
                      ))
                  .toList(growable: false),
            ),
          ],
          if (result.fallbackMode) ...[
            const SizedBox(height: 10),
            const Text(
              'AI 응답 실패로 기본 템플릿을 사용했습니다.',
              style: TextStyle(fontSize: 12, color: Color(0xFFA55A36), fontWeight: FontWeight.w700),
            ),
          ],
        ],
      ),
    );
  }
}
