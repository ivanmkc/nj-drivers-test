import SwiftUI

struct HomeScreen: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                LanguageBarView(localizer: localizer, availableLangs: vm.currentState?.languages)
                    .padding(.bottom, 4)

                Text(localizer.t("title", vars: [
                    "state": vm.currentState?.code.uppercased() ?? "",
                    "state_name": vm.currentState?.name ?? "",
                ]))
                .font(.system(size: 28, weight: .bold))
                .foregroundColor(AppTheme.blue)

                Text(localizer.t("subtitle", vars: [
                    "state_name": vm.currentState?.name ?? "",
                    "agency": vm.currentState?.agency ?? "",
                ]))
                .font(.system(size: 15))
                .foregroundColor(AppTheme.gray)

                if let state = vm.currentState {
                    Text(localizer.t("passingScore", vars: [
                        "pass_pct": "\(state.passingScorePct)",
                        "pass_count": "\(state.passCount)",
                        "test_count": "\(state.testQuestionCount)",
                    ]))
                    .font(.system(size: 13))
                    .foregroundColor(AppTheme.gray)
                }

                // Stats banner
                if !vm.quizHistory.isEmpty {
                    StatsBannerView(vm: vm, localizer: localizer)
                }

                // Mode selector
                HStack(spacing: 8) {
                    ModeButton(
                        title: localizer.t("modeRandom"),
                        desc: localizer.t("modeRandomDesc"),
                        icon: "\u{1F3B2}",
                        isActive: vm.quizMode == .random
                    ) { vm.quizMode = .random }

                    ModeButton(
                        title: localizer.t("modeWeak"),
                        desc: localizer.t("modeWeakDesc"),
                        icon: "\u{1F3AF}",
                        isActive: vm.quizMode == .weak,
                        badgeCount: vm.weakQuestions.count
                    ) { vm.quizMode = .weak }
                }

                // Count selector
                Text(localizer.t("numQuestions"))
                    .font(.system(size: 15, weight: .semibold))

                HStack(spacing: 8) {
                    ForEach(vm.countOptions, id: \.self) { count in
                        let isAll = count == vm.currentState?.totalQuestions
                        Button {
                            vm.selectedCount = count
                        } label: {
                            Text(isAll ? "All" : "\(count)")
                                .font(.system(size: 16, weight: .semibold))
                                .padding(.horizontal, 20)
                                .padding(.vertical, 10)
                                .foregroundColor(vm.selectedCount == count ? .white : AppTheme.blue)
                                .background(vm.selectedCount == count ? AppTheme.blue : AppTheme.card)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 12)
                                        .stroke(AppTheme.blue, lineWidth: 2)
                                )
                                .clipShape(RoundedRectangle(cornerRadius: 12))
                        }
                    }
                }

                // Start button
                let weakEmpty = vm.quizMode == .weak && vm.weakQuestions.isEmpty
                Button {
                    vm.startQuiz()
                } label: {
                    Text(weakEmpty ? localizer.t("noWeakSpots") : localizer.t("startQuiz"))
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(16)
                        .background(weakEmpty ? AppTheme.blue.opacity(0.5) : AppTheme.blue)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .disabled(weakEmpty || vm.isLoading)

                // Change state
                Button {
                    vm.goStatePicker()
                } label: {
                    Text(localizer.t("changeState"))
                        .font(.system(size: 14))
                        .foregroundColor(AppTheme.gray)
                }

                if vm.isLoading {
                    ProgressView()
                }
            }
            .padding(.horizontal, 16)
            .padding(.top, 24)
        }
        .background(AppTheme.grayLight)
    }
}
