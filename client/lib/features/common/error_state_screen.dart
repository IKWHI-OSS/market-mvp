import 'package:flutter/material.dart';

import '../../app/router.dart';
import '../../shared/widgets/error_state.dart';

class ErrorStateScreen extends StatelessWidget {
  const ErrorStateScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('에러/빈 상태')),
      body: ErrorStateWidget(
        title: '문제가 발생했어요',
        description: '네트워크 상태를 확인하고 다시 시도해주세요.',
        onRetry: () => Navigator.pushNamedAndRemoveUntil(
          context,
          AppRoutes.consumerShell,
          (route) => false,
        ),
        onSecondary: () => Navigator.pushNamedAndRemoveUntil(
          context,
          AppRoutes.consumerShell,
          (route) => false,
        ),
        secondaryLabel: '인근 시장 보기',
      ),
    );
  }
}
