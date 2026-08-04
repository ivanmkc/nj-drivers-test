import SwiftUI

struct QuizScreen: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
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
                            .font(.system(size: 14))
                            .monospacedDigit()
                            .foregroundColor(AppTheme.gray)
                        Spacer()
                        HStack(spacing: 4) {
                            Text("\(vm.correctCount)")
                                .foregroundColor(AppTheme.green)
                                .font(.system(size: 14, weight: .semibold))
                                .monospacedDigit()
                            Text("/")
                                .foregroundColor(AppTheme.gray)
                                .font(.system(size: 14))
                            Text("\(vm.wrongCount)")
                                .foregroundColor(AppTheme.red)
                                .font(.system(size: 14, weight: .semibold))
                                .monospacedDigit()
                        }
                    }

                    if let q = vm.currentQuestion {
                        // Category badge
                        HStack(spacing: 6) {
                            Text(q.category.replacingOccurrences(of: "_", with: " ").uppercased())
                                .font(.system(size: 12, weight: .semibold))
                                .foregroundColor(AppTheme.blue)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 4)
                                .background(AppTheme.blueLight)
                                .clipShape(RoundedRectangle(cornerRadius: 20))

                            if let miss = vm.questionMissInfo(q.id) {
                                Text("\(localizer.localized("missed")) \(Int(round(Double(miss.wrong) / Double(miss.seen) * 100)))%")
                                    .font(.system(size: 12, weight: .semibold))
                                    .foregroundColor(AppTheme.red)
                                    .padding(.horizontal, 10)
                                    .padding(.vertical, 4)
                                    .background(AppTheme.redLight)
                                    .clipShape(RoundedRectangle(cornerRadius: 20))
                            }
                        }

                        // Question text
                        Text(q.question)
                            .font(.system(size: 18, weight: .semibold))
                            .lineSpacing(4)
                            .fixedSize(horizontal: false, vertical: true)

                        // Question image
                        if let imageName = q.image,
                           let path = Bundle.main.path(
                               forResource: (imageName as NSString).deletingPathExtension,
                               ofType: (imageName as NSString).pathExtension,
                               inDirectory: "signs"
                           ),
                           let uiImage = UIImage(contentsOfFile: path) {
                            Image(uiImage: uiImage)
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                                .frame(maxHeight: 240)
                                .clipShape(RoundedRectangle(cornerRadius: 8))
                                .overlay(
                                    RoundedRectangle(cornerRadius: 8)
                                        .stroke(AppTheme.border, lineWidth: 1)
                                )
                                .frame(maxWidth: .infinity)
                        }

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
                        }

                        // Explanation
                        if let explanation = vm.explanation {
                            HStack(spacing: 0) {
                                Rectangle()
                                    .fill(AppTheme.blue)
                                    .frame(width: 4)
                                Text(explanation)
                                    .font(.system(size: 14))
                                    .lineSpacing(4)
                                    .foregroundColor(.secondary)
                                    .padding(12)
                            }
                            .background(AppTheme.blueLight)
                            .clipShape(RoundedRectangle(cornerRadius: 0))
                            .clipShape(
                                .rect(topLeadingRadius: 0, bottomLeadingRadius: 0, bottomTrailingRadius: 12, topTrailingRadius: 12)
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
                                    .font(.system(size: 17, weight: .semibold))
                                    .foregroundColor(AppTheme.onPrimary)
                                    .frame(maxWidth: .infinity)
                                    .padding(16)
                                    .background(AppTheme.blue)
                                    .clipShape(RoundedRectangle(cornerRadius: 12))
                            }
                            .transition(.move(edge: .bottom).combined(with: .opacity))
                        }
                    }
                }
                .padding(16)
                .animation(.easeInOut(duration: 0.25), value: vm.answered)
            }
            .background(AppTheme.grayLight)
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
