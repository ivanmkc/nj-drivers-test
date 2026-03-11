import SwiftUI

struct StatePickerView: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                LanguageBarView(localizer: localizer)
                    .padding(.bottom, 4)

                Text(localizer.t("appTitle"))
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(Color("Blue"))

                Text(localizer.t("selectStateDesc"))
                    .font(.system(size: 15))
                    .foregroundColor(Color("Gray"))
                    .padding(.bottom, 8)

                if vm.isLoading {
                    ProgressView()
                        .padding(.top, 40)
                } else if let error = vm.errorMessage {
                    VStack(spacing: 12) {
                        Text(error)
                            .foregroundColor(.red)
                            .multilineTextAlignment(.center)
                        Button("Retry") {
                            Task { await vm.loadStates() }
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    .padding(.top, 40)
                } else {
                    ForEach(vm.allStates) { state in
                        StateCardView(state: state, localizer: localizer) {
                            if state.hasQuestions {
                                vm.selectState(state)
                            }
                        }
                    }
                }
            }
            .padding(.horizontal, 16)
            .padding(.top, 40)
        }
        .background(Color("GrayLight"))
    }
}

struct StateCardView: View {
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
                        .foregroundColor(Color("Gray"))
                }

                Spacer()

                if state.hasQuestions {
                    Text(localizer.t("questionsAvailable", vars: ["count": "\(state.totalQuestions)"]))
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(Color("Blue"))
                } else {
                    Text(localizer.t("comingSoon"))
                        .font(.system(size: 11))
                        .foregroundColor(Color("Gray"))
                        .padding(.horizontal, 8)
                        .padding(.vertical, 2)
                        .background(Color("GrayLight"))
                        .clipShape(RoundedRectangle(cornerRadius: 10))
                }
            }
            .padding(16)
            .background(Color.white)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color(.systemGray4), lineWidth: 2)
            )
            .clipShape(RoundedRectangle(cornerRadius: 12))
            .opacity(state.hasQuestions ? 1 : 0.5)
        }
        .disabled(!state.hasQuestions)
    }

    private var passingText: String {
        let passCount = Int(ceil(Double(state.testQuestionCount) * Double(state.passingScorePct) / 100.0))
        return "\(state.agency) \u{00B7} " + localizer.t("passingScore", vars: [
            "pass_pct": "\(state.passingScorePct)",
            "pass_count": "\(passCount)",
            "test_count": "\(state.testQuestionCount)",
        ])
    }
}
