import SwiftUI

struct QuizScreen: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer
    @State private var showExitConfirmation = false

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    Button(localizer.localized("exitQuiz")) { showExitConfirmation = true }
                        .frame(minHeight: 44)
                        .accessibilityIdentifier("exit-quiz")
                    if let error = vm.quizError {
                        Text(error).foregroundColor(AppTheme.errorText).accessibilityIdentifier("quiz-error")
                    }
                    if vm.needsStudyWarning {
                        Text(localizer.localized("studyLanguageFooter"))
                            .font(.subheadline)
                            .foregroundColor(AppTheme.secondaryText)
                    }
                    // Progress bar
                    GeometryReader { geo in
                        ZStack(alignment: .leading) {
                            RoundedRectangle(cornerRadius: 3)
                                .fill(AppTheme.border)
                                .frame(height: 6)
                            RoundedRectangle(cornerRadius: 3)
                                .fill(AppTheme.blue)
                                .frame(width: geo.size.width * progress, height: 6)
                                .animation(.easeInOut(duration: 0.3), value: progress)
                        }
                    }
                    .frame(height: 6)
                    .id("top")

                    // Header
                    HStack {
                        Text("\(vm.currentIndex + 1) / \(vm.questions.count)")
                            .font(AppTheme.body(14))
                            .monospacedDigit()
                            .foregroundColor(AppTheme.secondaryText)
                        Spacer()
                        Text(localizer.localized("answerTally", substitutions: [
                            "correct": "\(vm.correctCount)", "wrong": "\(vm.wrongCount)",
                        ]))
                        .font(.subheadline).fontWeight(.semibold)
                        .foregroundColor(.primary)
                        .multilineTextAlignment(.trailing)
                        .fixedSize(horizontal: false, vertical: true)
                    }

                    if let q = vm.currentQuestion {
                        // Category badge
                        HStack(spacing: 6) {
                            Text(localizer.localizedCategory(q.category).uppercased())
                                .font(AppTheme.body(14)).fontWeight(.semibold)
                                .foregroundColor(AppTheme.blue)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 4)
                                .background(AppTheme.blueLight)
                                .clipShape(RoundedRectangle(cornerRadius: 20))

                            if let miss = vm.questionMissInfo(q.id) {
                                Text("\(localizer.localized("missed")) \(Int(round(Double(miss.wrong) / Double(miss.seen) * 100)))%")
                                    .font(AppTheme.body(14)).fontWeight(.semibold)
                                    .foregroundColor(AppTheme.errorText)
                                    .padding(.horizontal, 10)
                                    .padding(.vertical, 4)
                                    .background(AppTheme.redLight)
                                    .clipShape(RoundedRectangle(cornerRadius: 20))
                            }
                        }

                        SourceCitationView(state: vm.currentState)
                        // Question text
                        Text(q.question)
                            .font(AppTheme.body(18)).fontWeight(.semibold)
                            .lineSpacing(4)
                            .fixedSize(horizontal: false, vertical: true)

                        signImage(for: q)

                        // Choices
                        ForEach(q.sortedChoiceKeys, id: \.self) { letter in
                            ChoiceButton(
                                letter: letter,
                                text: q.choices[letter] ?? "",
                                state: choiceState(for: letter),
                                action: {
                                    vm.selectAnswer(letter)
                                }
                            )
                            .accessibilityIdentifier("answer-\(letter)")
                        }

                        // Explanation
                        if let explanation = vm.explanation {
                            HStack(spacing: 0) {
                                Rectangle()
                                    .fill(AppTheme.blue)
                                    .frame(width: 4)
                                Text(explanation)
                                    .font(AppTheme.body(14))
                                    .lineSpacing(4)
                                    .foregroundColor(AppTheme.secondaryText)
                                    .padding(12)
                            }
                            .background(AppTheme.blueLight)
                            .clipShape(RoundedRectangle(cornerRadius: 0))
                            .clipShape(
                                .rect(topLeadingRadius: 0, bottomLeadingRadius: 0, bottomTrailingRadius: 12, topTrailingRadius: 12)
                            )
                            .transition(.opacity)
                        }

                        // Evidence from the manual
                        if let evidence = vm.evidenceForCurrentQuestion(),
                           !evidence.isEmpty {
                            EvidenceBlockView(
                                evidence: evidence,
                                sourceName: vm.currentState?.source,
                                localizer: localizer
                            )
                            .transition(.opacity)
                        }

                        // Next button
                        if vm.answered {
                            let isLast = vm.currentIndex >= vm.questions.count - 1
                            Button {
                                vm.nextQuestion()
                                withAnimation {
                                    proxy.scrollTo("top", anchor: .top)
                                }
                            } label: {
                                Text(isLast ? localizer.localized("seeResults") : localizer.localized("next"))
                                    .font(AppTheme.body(17)).fontWeight(.semibold)
                                    .foregroundColor(AppTheme.onPrimary)
                                    .frame(maxWidth: .infinity)
                                    .padding(16)
                                    .background(AppTheme.blue)
                                    .clipShape(RoundedRectangle(cornerRadius: 12))
                            }
                            .accessibilityIdentifier("quiz-next")
                            .transition(.move(edge: .bottom).combined(with: .opacity))
                        }
                    }
                }
                .padding(16)
                .animation(.easeInOut(duration: 0.25), value: vm.answered)
            }
            .background(AppTheme.grayLight)
        }
        .alert(localizer.localized("exitQuiz"), isPresented: $showExitConfirmation) {
            Button(localizer.localized("leaveQuiz"), role: .destructive) { vm.abandonQuiz() }
            Button(localizer.localized("keepPracticing"), role: .cancel) {}
        } message: {
            Text(localizer.localized("exitQuizMessage"))
        }
    }

    @ViewBuilder
    private func signImage(for question: QuizQuestion) -> some View {
        if let imageName = question.image,
           let path = Bundle.main.path(
               forResource: (imageName as NSString).deletingPathExtension,
               ofType: (imageName as NSString).pathExtension,
               inDirectory: "signs"
           ),
           let uiImage = UIImage(contentsOfFile: path) {
            Image(uiImage: uiImage)
                .resizable()
                .scaledToFit()
                .frame(maxHeight: 240)
                .clipShape(RoundedRectangle(cornerRadius: 8))
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(AppTheme.border, lineWidth: 1)
                )
                .frame(maxWidth: .infinity)
                .accessibilityLabel(SignImageDescriptions.description(for: imageName))
        }
    }

    private var progress: CGFloat {
        guard !vm.questions.isEmpty else { return 0 }
        return CGFloat(vm.currentIndex) / CGFloat(vm.questions.count)
    }

    private func choiceState(for letter: String) -> ChoiceButtonState {
        guard vm.answered else { return .normal }
        if letter == vm.correctAnswer { return .correct }
        if letter == vm.selectedAnswer && letter != vm.correctAnswer { return .wrong }
        return .disabled
    }
}

// MARK: - Evidence Block

private struct EvidenceBlockView: View {
    let evidence: [String]
    let sourceName: String?
    @ObservedObject var localizer: Localizer

    var body: some View {
        HStack(spacing: 0) {
            Rectangle()
                .fill(AppTheme.gray)
                .frame(width: 4)

            VStack(alignment: .leading, spacing: 8) {
                HStack(spacing: 4) {
                    Image(systemName: "text.book.closed").accessibilityHidden(true)
                        .font(AppTheme.body(14))
                    Text(localizer.fromManualLabel())
                        .font(AppTheme.body(14)).fontWeight(.semibold)
                }
                .foregroundColor(AppTheme.secondaryText)

                ForEach(evidence, id: \.self) { passage in
                    Text(passage)
                        .font(AppTheme.body(14))
                        .italic()
                        .foregroundColor(AppTheme.secondaryText)
                        .lineSpacing(3)
                        .fixedSize(horizontal: false, vertical: true)
                }

                if let source = sourceName {
                    Text("-- \(source)")
                        .font(AppTheme.body(14))
                        .foregroundColor(AppTheme.secondaryText)
                }
            }
            .padding(12)
        }
        .background(AppTheme.grayLight)
        .clipShape(
            .rect(topLeadingRadius: 0, bottomLeadingRadius: 0, bottomTrailingRadius: 12, topTrailingRadius: 12)
        )
    }
}
