import SwiftUI

struct CardStyle: ViewModifier {
    var cornerRadius: CGFloat = 12
    var borderColor: Color = AppTheme.border
    var borderWidth: CGFloat = 2

    func body(content: Content) -> some View {
        content
            .background(AppTheme.card)
            .overlay(RoundedRectangle(cornerRadius: cornerRadius).stroke(borderColor, lineWidth: borderWidth))
            .clipShape(RoundedRectangle(cornerRadius: cornerRadius))
    }
}

extension View {
    func cardStyle(cornerRadius: CGFloat = 12, borderColor: Color = AppTheme.border, borderWidth: CGFloat = 2) -> some View {
        modifier(CardStyle(cornerRadius: cornerRadius, borderColor: borderColor, borderWidth: borderWidth))
    }
}

// MARK: - LanguageBarView

struct LanguageBarView: View {
    @ObservedObject var localizer: Localizer
    var availableLangs: [String]?

    private var langs: [String] {
        availableLangs ?? ["en", "es"]
    }

    var body: some View {
        HStack(spacing: 6) {
            Spacer()
            ForEach(langs, id: \.self) { lang in
                Button {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        localizer.currentLang = lang
                    }
                } label: {
                    Text(localizer.langLabels[lang] ?? lang.uppercased())
                        .font(.system(size: 13, weight: .semibold))
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .foregroundColor(lang == localizer.currentLang ? AppTheme.blue : AppTheme.gray)
                        .background(lang == localizer.currentLang ? AppTheme.blueLight : AppTheme.card)
                        .cardStyle(cornerRadius: 20, borderColor: lang == localizer.currentLang ? AppTheme.blue : AppTheme.border, borderWidth: 1.5)
                        .frame(minHeight: 44)
                        .contentShape(Rectangle())
                }
            }
        }
    }
}

// MARK: - StatItem (from HomeView)

struct StatItem: View {
    let value: String
    let label: String

    var body: some View {
        VStack(spacing: 2) {
            Text(value)
                .font(.system(size: 22, weight: .bold))
                .monospacedDigit()
            Text(label)
                .font(.system(size: 11))
                .foregroundColor(AppTheme.gray)
                .textCase(.uppercase)
        }
    }
}

// MARK: - StatsBannerView (from HomeView)

struct StatsBannerView: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer

    var body: some View {
        HStack {
            HStack(spacing: 16) {
                StatItem(value: "\(vm.quizHistory.count)", label: localizer.localized("quizzes"))
                StatItem(value: "\(vm.averageScore)%", label: localizer.localized("avgScore"))
                StatItem(value: "\(vm.passStreak)", label: localizer.localized("passStreak"))
            }
            Spacer()
            Button {
                vm.showStats()
            } label: {
                Text(localizer.localized("viewStats"))
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(AppTheme.blue)
            }
        }
        .padding(14)
        .cardStyle(borderWidth: 1)
    }
}

// MARK: - ModeButton (from HomeView)

struct ModeButton: View {
    let title: String
    let desc: String
    let systemImage: String
    let isActive: Bool
    var badgeCount: Int = 0
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Image(systemName: systemImage)
                    .font(.system(size: 20))
                    .foregroundColor(isActive ? AppTheme.blue : AppTheme.gray)
                HStack(spacing: 4) {
                    Text(title).font(.system(size: 14, weight: .semibold))
                    if badgeCount > 0 {
                        Text("\(badgeCount)")
                            .font(.system(size: 11, weight: .bold))
                            .foregroundColor(.white)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 1)
                            .background(AppTheme.red)
                            .clipShape(RoundedRectangle(cornerRadius: 10))
                    }
                }
                Text(desc)
                    .font(.system(size: 11))
                    .foregroundColor(isActive ? AppTheme.blue : AppTheme.gray)
            }
            .frame(maxWidth: .infinity)
            .padding(12)
            .foregroundColor(isActive ? AppTheme.blue : .primary)
            .background(isActive ? AppTheme.blueLight : AppTheme.card)
            .cardStyle(borderColor: isActive ? AppTheme.blue : AppTheme.border)
        }
    }
}

// MARK: - ChoiceButton & ChoiceButtonState (from QuizView)

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
                ZStack {
                    if state == .correct {
                        Image(systemName: "checkmark")
                            .font(.system(size: 14, weight: .bold))
                            .foregroundColor(letterForeground)
                    } else if state == .wrong {
                        Image(systemName: "xmark")
                            .font(.system(size: 14, weight: .bold))
                            .foregroundColor(letterForeground)
                    } else {
                        Text(letter)
                            .font(.system(size: 14, weight: .bold))
                            .foregroundColor(letterForeground)
                    }
                }
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
            .cardStyle(borderColor: borderColor)
        }
        .disabled(state != .normal)
        .opacity(state == .disabled ? 0.7 : 1)
    }

    private var letterForeground: Color {
        switch state {
        case .correct, .wrong: return .white
        default: return AppTheme.gray
        }
    }

    private var letterBackground: Color {
        switch state {
        case .correct: return AppTheme.green
        case .wrong: return AppTheme.red
        default: return AppTheme.grayLight
        }
    }

    private var cardBackground: Color {
        switch state {
        case .correct: return AppTheme.greenLight
        case .wrong: return AppTheme.redLight
        default: return AppTheme.card
        }
    }

    private var borderColor: Color {
        switch state {
        case .correct: return AppTheme.green
        case .wrong: return AppTheme.red
        default: return AppTheme.border
        }
    }
}

// MARK: - ReviewItemView (from ResultsView)

struct ReviewItemView: View {
    let result: SessionResult
    @ObservedObject var localizer: Localizer

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(result.question)
                .font(.system(size: 14, weight: .semibold))

            HStack(spacing: 4) {
                Text(localizer.localized("yourAnswer") + ":")
                    .font(.system(size: 13))
                    .foregroundColor(AppTheme.gray)
                Text("\(result.yourAnswer): \(result.yourAnswerText)")
                    .font(.system(size: 13, weight: .semibold))
            }

            HStack(spacing: 4) {
                Text(localizer.localized("correct") + ":")
                    .font(.system(size: 13))
                    .foregroundColor(AppTheme.gray)
                Text("\(result.correctAnswer): \(result.correctAnswerText)")
                    .font(.system(size: 13, weight: .semibold))
            }

            Text(result.explanation)
                .font(.system(size: 13))
                .foregroundColor(AppTheme.gray)
                .italic()
                .padding(.top, 2)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(14)
        .background(AppTheme.card)
        .overlay(
            HStack(spacing: 0) {
                Rectangle()
                    .fill(AppTheme.red)
                    .frame(width: 4)
                Spacer()
            }
        )
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

// MARK: - StatCardView (from StatsView)

struct StatCardView: View {
    let value: String
    let label: String
    let color: Color

    var body: some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.system(size: 26, weight: .bold))
                .monospacedDigit()
                .foregroundColor(color)
            Text(label)
                .font(.system(size: 11))
                .foregroundColor(AppTheme.gray)
                .textCase(.uppercase)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 16)
        .cardStyle(borderWidth: 1)
    }
}

// MARK: - CategoryBarView (from StatsView)

struct CategoryBarView: View {
    let category: String
    let pct: Int

    private var barColor: Color {
        if pct >= 80 { return AppTheme.green }
        if pct >= 60 { return AppTheme.orange }
        return AppTheme.red
    }

    var body: some View {
        HStack(spacing: 10) {
            Text(category.replacingOccurrences(of: "_", with: " ").capitalized)
                .font(.system(size: 13))
                .frame(width: 110, alignment: .leading)
                .lineLimit(1)

            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 5)
                        .fill(AppTheme.border)
                        .frame(height: 10)
                    RoundedRectangle(cornerRadius: 5)
                        .fill(barColor)
                        .frame(width: geo.size.width * CGFloat(pct) / 100.0, height: 10)
                }
            }
            .frame(height: 10)

            Text("\(pct)%")
                .font(.system(size: 13, weight: .semibold))
                .monospacedDigit()
                .foregroundColor(barColor)
                .frame(width: 36, alignment: .trailing)
        }
    }
}

// MARK: - WeakItemView (from StatsView)

struct WeakItemView: View {
    let weak: WeakQuestion
    @ObservedObject var localizer: Localizer

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("Q\(weak.id)")
                .font(.system(size: 14, weight: .semibold))
            HStack(spacing: 4) {
                Text(localizer.localized("missed"))
                    .font(.system(size: 12))
                    .foregroundColor(AppTheme.gray)
                Text("\(weak.wrong)/\(weak.seen) (\(Int(round(weak.missRate * 100)))%)")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(AppTheme.red)
                Text("\u{00B7}")
                    .foregroundColor(AppTheme.gray)
                Text(weak.category.replacingOccurrences(of: "_", with: " "))
                    .font(.system(size: 12))
                    .foregroundColor(AppTheme.gray)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 14)
        .padding(.vertical, 12)
        .background(AppTheme.card)
        .overlay(
            HStack(spacing: 0) {
                Rectangle()
                    .fill(AppTheme.orange)
                    .frame(width: 4)
                Spacer()
            }
        )
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(AppTheme.border, lineWidth: 1)
        )
    }
}

// MARK: - ScoreChartView (from StatsView)

struct ScoreChartView: View {
    let history: [QuizHistoryEntry]
    let passingPct: Int

    var body: some View {
        Canvas { context, size in
            let pad = EdgeInsets(top: 20, leading: 36, bottom: 30, trailing: 16)
            let plotW = size.width - pad.leading - pad.trailing
            let plotH = size.height - pad.top - pad.bottom
            let data = Array(history.suffix(20))
            let n = data.count

            // Grid lines
            for pct in [0, 25, 50, 75, 100] {
                let y = pad.top + plotH - (CGFloat(pct) / 100.0) * plotH
                var path = Path()
                path.move(to: CGPoint(x: pad.leading, y: y))
                path.addLine(to: CGPoint(x: size.width - pad.trailing, y: y))
                context.stroke(path, with: .color(AppTheme.border), lineWidth: 1)

                context.draw(
                    Text("\(pct)%").font(.system(size: 10)).foregroundColor(Color(.systemGray)),
                    at: CGPoint(x: pad.leading - 8, y: y),
                    anchor: .trailing
                )
            }

            // Passing line
            let passY = pad.top + plotH - (CGFloat(passingPct) / 100.0) * plotH
            var passPath = Path()
            passPath.move(to: CGPoint(x: pad.leading, y: passY))
            passPath.addLine(to: CGPoint(x: size.width - pad.trailing, y: passY))
            context.stroke(passPath, with: .color(AppTheme.green.opacity(0.3)), style: StrokeStyle(lineWidth: 2, dash: [6, 4]))

            // Data points
            let points: [CGPoint] = data.enumerated().map { i, d in
                let x = pad.leading + (n == 1 ? plotW / 2 : CGFloat(i) / CGFloat(n - 1) * plotW)
                let y = pad.top + plotH - (CGFloat(d.pct) / 100.0) * plotH
                return CGPoint(x: x, y: y)
            }

            // Line
            if points.count >= 2, let lastPoint = points.last, let firstPoint = points.first {
                var linePath = Path()
                linePath.move(to: points[0])
                for p in points.dropFirst() { linePath.addLine(to: p) }
                context.stroke(linePath, with: .color(AppTheme.blue), lineWidth: 2.5)

                // Fill
                var fillPath = linePath
                fillPath.addLine(to: CGPoint(x: lastPoint.x, y: pad.top + plotH))
                fillPath.addLine(to: CGPoint(x: firstPoint.x, y: pad.top + plotH))
                fillPath.closeSubpath()

                let gradient = Gradient(colors: [AppTheme.blue.opacity(0.2), AppTheme.blue.opacity(0.02)])
                context.fill(
                    fillPath,
                    with: .linearGradient(
                        gradient,
                        startPoint: CGPoint(x: 0, y: pad.top),
                        endPoint: CGPoint(x: 0, y: pad.top + plotH)
                    )
                )
            }

            // Dots
            for (i, p) in points.enumerated() {
                let color: Color = data[i].pct >= passingPct ? AppTheme.green : AppTheme.red
                var dotPath = Path()
                dotPath.addEllipse(in: CGRect(x: p.x - 4, y: p.y - 4, width: 8, height: 8))
                context.fill(dotPath, with: .color(color))
                context.stroke(dotPath, with: .color(AppTheme.card), lineWidth: 2)
            }

            // X-axis labels
            let startNum = history.count - data.count + 1
            let step = n <= 10 ? 1 : 2
            for (i, p) in points.enumerated() {
                if i % step == 0 || i == n - 1 {
                    context.draw(
                        Text("#\(startNum + i)").font(.system(size: 10)).foregroundColor(Color(.systemGray)),
                        at: CGPoint(x: p.x, y: size.height - pad.bottom + 16),
                        anchor: .center
                    )
                }
            }
        }
    }
}
