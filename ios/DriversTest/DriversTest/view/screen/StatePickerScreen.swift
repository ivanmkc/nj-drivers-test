import SwiftUI

struct StatePickerScreen: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer

    @State private var search = ""
    @FocusState private var searching: Bool

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                LanguageBarView(localizer: localizer)
                    .padding(.bottom, 4)

                Text(localizer.localized("appTitle"))
                    .font(AppTheme.display(28)).fontWeight(.bold)
                    .foregroundColor(AppTheme.navy)

                Text(localizer.localized("selectStateDesc"))
                    .font(AppTheme.body(15))
                    .foregroundColor(AppTheme.secondaryText)
                    .padding(.bottom, 8)

                TextField(localizer.localized("searchStates"), text: $search)
                    .textFieldStyle(.roundedBorder)
                    .focused($searching)
                    .submitLabel(.search)
                    .onSubmit { searching = false }
                    .frame(minHeight: 44)
                    .accessibilityIdentifier("state-search")
                Text(localizer.localized("unofficialNotice"))
                    .font(.subheadline)
                    .foregroundColor(AppTheme.secondaryText)

                if vm.isLoading {
                    VStack(spacing: 12) {
                        ProgressView()
                        Text(localizer.localized("loadingQuestions"))
                    }
                    .padding(.top, 40)
                } else if let error = vm.loadError {
                    VStack(spacing: 8) {
                        Text("Failed to load questions")
                            .font(AppTheme.body(15)).fontWeight(.semibold)
                            .foregroundColor(AppTheme.errorText)
                        Button(localizer.localized("retryLoad")) { vm.loadStates() }
                            .frame(minHeight: 44)
                        Text(error)
                            .font(AppTheme.body(14))
                            .foregroundColor(AppTheme.secondaryText)
                    }
                    .padding(.top, 40)
                } else {
                    let matches = vm.allStates.sorted {
                        $0.name.localizedStandardCompare($1.name) == .orderedAscending
                    }.filter {
                        search.isEmpty || $0.name.localizedCaseInsensitiveContains(search) || $0.code.localizedCaseInsensitiveContains(search)
                    }
                    if matches.isEmpty { Text(localizer.localized("noStates")) }
                    ForEach(matches) { state in
                        StateCard(state: state, localizer: localizer) {
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
                        .font(AppTheme.body(17)).fontWeight(.semibold)
                        .foregroundColor(.primary)

                    Text(passingText)
                        .font(AppTheme.body(14))
                        .foregroundColor(AppTheme.secondaryText)
                }

                Spacer()

                if state.hasQuestions {
                    Text(localizer.localized("questionsAvailable", substitutions: ["count": "\(state.totalQuestions)"]))
                        .font(AppTheme.body(14)).fontWeight(.semibold)
                        .foregroundColor(AppTheme.blue)
                } else {
                    Text(localizer.localized("comingSoon"))
                        .font(AppTheme.body(14))
                        .foregroundColor(AppTheme.secondaryText)
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
