import SwiftUI

struct ResultsView: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                // Score circle
                ZStack {
                    Circle()
                        .stroke(vm.didPass ? Color("Green") : Color("Red"), lineWidth: 6)
                        .frame(width: 160, height: 160)

                    VStack(spacing: 2) {
                        Text("\(vm.resultPct)%")
                            .font(.system(size: 42, weight: .bold))
                            .foregroundColor(vm.didPass ? Color("Green") : Color("Red"))
                        Text(vm.didPass ? localizer.t("pass") : localizer.t("fail"))
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundColor(vm.didPass ? Color("Green") : Color("Red"))
                            .textCase(.uppercase)
                    }
                }
                .padding(.top, 24)

                Text(vm.didPass ? localizer.t("congratulations") : localizer.t("keepPracticing"))
                    .font(.system(size: 22, weight: .bold))

                if let state = vm.currentState {
                    Text(localizer.t("resultDetail", vars: [
                        "correct": "\(vm.correctCount)",
                        "total": "\(vm.questions.count)",
                        "pass_pct": "\(state.passingScorePct)",
                        "agency": state.agency,
                    ]))
                    .font(.system(size: 15))
                    .foregroundColor(Color("Gray"))
                    .multilineTextAlignment(.center)
                    .lineSpacing(3)
                }

                // Action buttons
                Button {
                    vm.goHome()
                } label: {
                    Text(localizer.t("newQuiz"))
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(16)
                        .background(Color("Blue"))
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }

                Button {
                    vm.showStats()
                } label: {
                    Text(localizer.t("viewStats"))
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(Color("Blue"))
                        .frame(maxWidth: .infinity)
                        .padding(16)
                        .background(Color.white)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color("Blue"), lineWidth: 2)
                        )
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }

                // Review section
                if !vm.wrongResults.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text(localizer.t("reviewMissed", vars: ["count": "\(vm.wrongResults.count)"]))
                            .font(.system(size: 18, weight: .semibold))

                        ForEach(vm.wrongResults, id: \.id) { result in
                            ReviewItemView(result: result, localizer: localizer)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.top, 8)
                } else {
                    VStack(spacing: 8) {
                        Text(localizer.t("perfectScore"))
                            .font(.system(size: 18, weight: .semibold))
                        Text(localizer.t("perfectMsg"))
                            .font(.system(size: 15))
                            .foregroundColor(Color("Gray"))
                    }
                    .padding(.top, 8)
                }
            }
            .padding(16)
        }
        .background(Color("GrayLight"))
    }
}

struct ReviewItemView: View {
    let result: SessionResult
    @ObservedObject var localizer: Localizer

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(result.question)
                .font(.system(size: 14, weight: .semibold))

            HStack(spacing: 4) {
                Text(localizer.t("yourAnswer") + ":")
                    .font(.system(size: 13))
                    .foregroundColor(Color("Gray"))
                Text("\(result.yourAnswer): \(result.yourAnswerText)")
                    .font(.system(size: 13, weight: .semibold))
            }

            HStack(spacing: 4) {
                Text(localizer.t("correct") + ":")
                    .font(.system(size: 13))
                    .foregroundColor(Color("Gray"))
                Text("\(result.correctAnswer): \(result.correctAnswerText)")
                    .font(.system(size: 13, weight: .semibold))
            }

            Text(result.explanation)
                .font(.system(size: 13))
                .foregroundColor(Color("Gray"))
                .italic()
                .padding(.top, 2)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(14)
        .background(Color.white)
        .overlay(
            HStack(spacing: 0) {
                Rectangle()
                    .fill(Color("Red"))
                    .frame(width: 4)
                Spacer()
            }
        )
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}
