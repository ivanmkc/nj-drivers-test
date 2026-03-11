import SwiftUI

struct QuizView: View {
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
                                .fill(Color(.systemGray4))
                                .frame(height: 6)
                            RoundedRectangle(cornerRadius: 3)
                                .fill(Color("Blue"))
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
                            .foregroundColor(Color("Gray"))
                        Spacer()
                        HStack(spacing: 4) {
                            Text("\(vm.correctCount)")
                                .foregroundColor(Color("Green"))
                                .font(.system(size: 14, weight: .semibold))
                            Text("/")
                                .foregroundColor(Color("Gray"))
                                .font(.system(size: 14))
                            Text("\(vm.wrongCount)")
                                .foregroundColor(Color("Red"))
                                .font(.system(size: 14, weight: .semibold))
                        }
                    }

                    if let q = vm.currentQuestion {
                        // Category badge
                        HStack(spacing: 6) {
                            Text(q.category.replacingOccurrences(of: "_", with: " ").uppercased())
                                .font(.system(size: 12, weight: .semibold))
                                .foregroundColor(Color("Blue"))
                                .padding(.horizontal, 10)
                                .padding(.vertical, 4)
                                .background(Color("BlueLight"))
                                .clipShape(RoundedRectangle(cornerRadius: 20))

                            if let miss = vm.questionMissInfo(q.id) {
                                Text("\(localizer.t("missed")) \(Int(round(Double(miss.wrong) / Double(miss.seen) * 100)))%")
                                    .font(.system(size: 12, weight: .semibold))
                                    .foregroundColor(Color("Red"))
                                    .padding(.horizontal, 10)
                                    .padding(.vertical, 4)
                                    .background(Color("RedLight"))
                                    .clipShape(RoundedRectangle(cornerRadius: 20))
                            }
                        }

                        // Question text
                        Text(q.question)
                            .font(.system(size: 18, weight: .semibold))
                            .lineSpacing(4)
                            .fixedSize(horizontal: false, vertical: true)

                        // Question image
                        if let imageName = q.image, let state = vm.currentState,
                           let url = APIService.shared.signImageURL(state: state.code, filename: imageName) {
                            AsyncImage(url: url) { image in
                                image
                                    .resizable()
                                    .aspectRatio(contentMode: .fit)
                                    .frame(maxHeight: 240)
                                    .clipShape(RoundedRectangle(cornerRadius: 8))
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 8)
                                            .stroke(Color(.systemGray4), lineWidth: 1)
                                    )
                            } placeholder: {
                                ProgressView()
                                    .frame(height: 120)
                            }
                            .frame(maxWidth: .infinity)
                        }

                        // Choices
                        ForEach(q.sortedChoiceKeys, id: \.self) { letter in
                            ChoiceButton(
                                letter: letter,
                                text: q.choices[letter] ?? "",
                                state: choiceState(for: letter),
                                action: {
                                    Task { await vm.selectAnswer(letter) }
                                }
                            )
                        }

                        // Explanation
                        if let explanation = vm.explanation {
                            HStack(spacing: 0) {
                                Rectangle()
                                    .fill(Color("Blue"))
                                    .frame(width: 4)
                                Text(explanation)
                                    .font(.system(size: 14))
                                    .lineSpacing(4)
                                    .foregroundColor(Color(.darkGray))
                                    .padding(12)
                            }
                            .background(Color("BlueLight"))
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
                                Text(isLast ? localizer.t("seeResults") : localizer.t("next"))
                                    .font(.system(size: 17, weight: .semibold))
                                    .foregroundColor(.white)
                                    .frame(maxWidth: .infinity)
                                    .padding(16)
                                    .background(Color("Blue"))
                                    .clipShape(RoundedRectangle(cornerRadius: 12))
                            }
                            .transition(.move(edge: .bottom).combined(with: .opacity))
                        }
                    }
                }
                .padding(16)
                .animation(.easeInOut(duration: 0.25), value: vm.answered)
            }
            .background(Color("GrayLight"))
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

enum ChoiceButtonState {
    case normal, correct, wrong, disabled
}

struct ChoiceButton: View {
    let letter: String
    let text: String
    let state: ChoiceButtonState
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(alignment: .top, spacing: 12) {
                Text(letter)
                    .font(.system(size: 14, weight: .bold))
                    .foregroundColor(letterForeground)
                    .frame(width: 28, height: 28)
                    .background(letterBackground)
                    .clipShape(Circle())

                Text(text)
                    .font(.system(size: 16))
                    .lineSpacing(3)
                    .foregroundColor(.primary)
                    .multilineTextAlignment(.leading)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(14)
            .background(cardBackground)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(borderColor, lineWidth: 2)
            )
            .clipShape(RoundedRectangle(cornerRadius: 12))
        }
        .disabled(state != .normal)
        .opacity(state == .disabled ? 0.7 : 1)
    }

    private var letterForeground: Color {
        switch state {
        case .correct, .wrong: return .white
        default: return Color("Gray")
        }
    }

    private var letterBackground: Color {
        switch state {
        case .correct: return Color("Green")
        case .wrong: return Color("Red")
        default: return Color("GrayLight")
        }
    }

    private var cardBackground: Color {
        switch state {
        case .correct: return Color("GreenLight")
        case .wrong: return Color("RedLight")
        default: return .white
        }
    }

    private var borderColor: Color {
        switch state {
        case .correct: return Color("Green")
        case .wrong: return Color("Red")
        default: return Color(.systemGray4)
        }
    }
}
