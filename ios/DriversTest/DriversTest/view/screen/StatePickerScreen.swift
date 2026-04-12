import SwiftUI

struct StatePickerScreen: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                LanguageBarView(localizer: localizer)
                    .padding(.bottom, 4)

                Text(localizer.localized("appTitle"))
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(AppTheme.blue)

                Text(localizer.localized("selectStateDesc"))
                    .font(.system(size: 15))
                    .foregroundColor(AppTheme.gray)
                    .padding(.bottom, 8)

                ForEach(vm.allStates) { state in
                    StateCard(state: state, localizer: localizer) {
                        if state.hasQuestions {
                            vm.selectState(state)
                        }
                    }
                }
            }
            .padding(.horizontal, 16)
            .padding(.top, 40)
        }
        .background(AppTheme.grayLight)
    }
}

struct StateCard: View {
    let state: StateInfo
    @ObservedObject var localizer: Localizer
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text(state.name)
                        .font(.system(size: 17, weight: .semibold))
                        .foregroundColor(.primary)

                    Text(passingText)
                        .font(.system(size: 13))
                        .foregroundColor(AppTheme.gray)
                }

                Spacer()

                if state.hasQuestions {
                    Text(localizer.localized("questionsAvailable", substitutions: ["count": "\(state.totalQuestions)"]))
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(AppTheme.blue)
                } else {
                    Text(localizer.localized("comingSoon"))
                        .font(.system(size: 11))
                        .foregroundColor(AppTheme.gray)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 2)
                        .background(AppTheme.grayLight)
                        .clipShape(RoundedRectangle(cornerRadius: 10))
                }
            }
            .padding(16)
            .cardStyle()
            .opacity(state.hasQuestions ? 1 : 0.5)
        }
        .disabled(!state.hasQuestions)
    }

    private var passingText: String {
        "\(state.agency) \u{00B7} " + localizer.localized("passingScore", substitutions: [
            "pass_pct": "\(state.passingScorePct)",
            "pass_count": "\(state.passCount)",
            "test_count": "\(state.testQuestionCount)",
        ])
    }
}
