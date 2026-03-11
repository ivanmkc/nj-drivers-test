import SwiftUI

struct HomeView: View {
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
                .foregroundColor(Color("Blue"))

                Text(localizer.t("subtitle", vars: [
                    "state_name": vm.currentState?.name ?? "",
                    "agency": vm.currentState?.agency ?? "",
                ]))
                .font(.system(size: 15))
                .foregroundColor(Color("Gray"))

                if let state = vm.currentState {
                    let passCount = Int(ceil(Double(state.testQuestionCount) * Double(state.passingScorePct) / 100.0))
                    Text(localizer.t("passingScore", vars: [
                        "pass_pct": "\(state.passingScorePct)",
                        "pass_count": "\(passCount)",
                        "test_count": "\(state.testQuestionCount)",
                    ]))
                    .font(.system(size: 13))
                    .foregroundColor(Color("Gray"))
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
                        icon: "🎲",
                        isActive: vm.quizMode == .random
                    ) { vm.quizMode = .random }

                    ModeButton(
                        title: localizer.t("modeWeak"),
                        desc: localizer.t("modeWeakDesc"),
                        icon: "🎯",
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
                                .foregroundColor(vm.selectedCount == count ? .white : Color("Blue"))
                                .background(vm.selectedCount == count ? Color("Blue") : Color.white)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 12)
                                        .stroke(Color("Blue"), lineWidth: 2)
                                )
                                .clipShape(RoundedRectangle(cornerRadius: 12))
                        }
                    }
                }

                // Start button
                let weakEmpty = vm.quizMode == .weak && vm.weakQuestions.isEmpty
                Button {
                    Task { await vm.startQuiz() }
                } label: {
                    Text(weakEmpty ? localizer.t("noWeakSpots") : localizer.t("startQuiz"))
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(16)
                        .background(weakEmpty ? Color("Blue").opacity(0.5) : Color("Blue"))
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .disabled(weakEmpty || vm.isLoading)

                // Change state
                Button {
                    vm.goStatePicker()
                } label: {
                    Text(localizer.t("changeState"))
                        .font(.system(size: 14))
                        .foregroundColor(Color("Gray"))
                }

                if vm.isLoading {
                    ProgressView()
                }
            }
            .padding(.horizontal, 16)
            .padding(.top, 24)
        }
        .background(Color("GrayLight"))
    }
}

struct StatsBannerView: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer

    var body: some View {
        HStack {
            HStack(spacing: 16) {
                StatItem(value: "\(vm.quizHistory.count)", label: localizer.t("quizzes"))
                StatItem(value: "\(vm.averageScore)%", label: localizer.t("avgScore"))
                StatItem(value: "\(vm.passStreak)", label: localizer.t("passStreak"))
            }
            Spacer()
            Button {
                vm.showStats()
            } label: {
                Text(localizer.t("viewStats"))
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(Color("Blue"))
            }
        }
        .padding(14)
        .background(Color.white)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color(.systemGray4), lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

struct StatItem: View {
    let value: String
    let label: String

    var body: some View {
        VStack(spacing: 2) {
            Text(value)
                .font(.system(size: 22, weight: .bold))
            Text(label)
                .font(.system(size: 11))
                .foregroundColor(Color("Gray"))
                .textCase(.uppercase)
        }
    }
}

struct ModeButton: View {
    let title: String
    let desc: String
    let icon: String
    let isActive: Bool
    var badgeCount: Int = 0
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Text(icon).font(.system(size: 20))
                HStack(spacing: 4) {
                    Text(title).font(.system(size: 14, weight: .semibold))
                    if badgeCount > 0 {
                        Text("\(badgeCount)")
                            .font(.system(size: 11, weight: .bold))
                            .foregroundColor(.white)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 1)
                            .background(Color.red)
                            .clipShape(RoundedRectangle(cornerRadius: 10))
                    }
                }
                Text(desc)
                    .font(.system(size: 11))
                    .foregroundColor(isActive ? Color("Blue") : Color("Gray"))
            }
            .frame(maxWidth: .infinity)
            .padding(12)
            .foregroundColor(isActive ? Color("Blue") : .primary)
            .background(isActive ? Color("BlueLight") : Color.white)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(isActive ? Color("Blue") : Color(.systemGray4), lineWidth: 2)
            )
            .clipShape(RoundedRectangle(cornerRadius: 12))
        }
    }
}
