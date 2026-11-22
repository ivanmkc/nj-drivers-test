import SwiftUI

struct TapTargetButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .frame(minWidth: 44, minHeight: 44)
            .contentShape(Rectangle())
            .foregroundColor(AppTheme.blue)
            .opacity(configuration.isPressed ? 0.85 : 1)
    }
}

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

// MARK: - StatItem (from HomeView)
struct StatItem: View {
    let value: String
    let label: String

    var body: some View {
        VStack(spacing: 2) {
            Text(value)
                .font(AppTheme.display(22)).fontWeight(.bold)
                .monospacedDigit()
            Text(label)
                .font(AppTheme.body(14))
                .foregroundColor(AppTheme.secondaryText)
                .textCase(.uppercase)
        }
    }
}
// MARK: - StatsBannerView (from HomeView)

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
                Image(systemName: systemImage).accessibilityHidden(true)
                    .font(AppTheme.body(20))
                    .foregroundColor(isActive ? AppTheme.blue : AppTheme.gray)
                HStack(spacing: 4) {
                    Text(title).font(AppTheme.body(14)).fontWeight(.semibold)
                    if badgeCount > 0 {
                        Text("\(badgeCount)")
                            .font(AppTheme.body(14)).fontWeight(.bold)
                            .foregroundColor(AppTheme.onPrimary)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 1)
                            .background(AppTheme.red)
                            .clipShape(RoundedRectangle(cornerRadius: 10))
                    }
                }
                Text(desc)
                    .font(AppTheme.body(14))
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
                        Image(systemName: "checkmark").accessibilityHidden(true)
                            .font(AppTheme.body(14)).fontWeight(.bold)
                            .foregroundColor(letterForeground)
                    } else if state == .wrong {
                        Image(systemName: "xmark").accessibilityHidden(true)
                            .font(AppTheme.body(14)).fontWeight(.bold)
                            .foregroundColor(letterForeground)
                    } else {
                        Text(letter)
                            .font(AppTheme.body(14)).fontWeight(.bold)
                            .foregroundColor(letterForeground)
                    }
                }
                .frame(width: 28, height: 28)
                .background(letterBackground)
                .clipShape(Circle())

                Text(text)
                    .font(AppTheme.body(16))
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
    }

    private var letterForeground: Color {
        switch state {
        case .correct, .wrong: return AppTheme.onPrimary
        default: return AppTheme.secondaryText
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
                .font(AppTheme.body(14)).fontWeight(.semibold)

            HStack(spacing: 4) {
                Text(localizer.localized("yourAnswer") + ":")
                    .font(AppTheme.body(14))
                    .foregroundColor(AppTheme.secondaryText)
                Text("\(result.yourAnswer): \(result.yourAnswerText)")
                    .font(AppTheme.body(14)).fontWeight(.semibold)
            }

            HStack(spacing: 4) {
                Text(localizer.localized("correct") + ":")
                    .font(AppTheme.body(14))
                    .foregroundColor(AppTheme.secondaryText)
                Text("\(result.correctAnswer): \(result.correctAnswerText)")
                    .font(AppTheme.body(14)).fontWeight(.semibold)
            }

            Text(result.explanation)
                .font(AppTheme.body(14))
                .foregroundColor(AppTheme.secondaryText)
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
    var accessibilityID: String?

    var body: some View {
        VStack(spacing: 4) {
            Text(value)
                .accessibilityIdentifier(accessibilityID ?? label)
                .accessibilityLabel(label)
                .accessibilityValue(value)
                .font(AppTheme.display(26)).fontWeight(.bold)
                .monospacedDigit()
                .foregroundColor(color)
            Text(label)
                .font(AppTheme.body(14))
                .foregroundColor(AppTheme.secondaryText)
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
    @ObservedObject var localizer: Localizer = .shared

    private var barColor: Color {
        if pct >= 80 { return AppTheme.green }
        if pct >= 60 { return AppTheme.orange }
        return AppTheme.red
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(localizer.localizedCategory(category))
                .font(AppTheme.body(14))
                .fixedSize(horizontal: false, vertical: true)
            HStack(spacing: 10) {
                GeometryReader { geo in
                    ZStack(alignment: .leading) {
                        RoundedRectangle(cornerRadius: 5).fill(AppTheme.border).frame(height: 10)
                        RoundedRectangle(cornerRadius: 5).fill(barColor)
                            .frame(width: geo.size.width * CGFloat(pct) / 100.0, height: 10)
                    }
                }
                .frame(height: 10)
                .accessibilityHidden(true)
                Text("\(pct)%")
                    .font(AppTheme.body(14)).fontWeight(.semibold)
                    .monospacedDigit()
                    .foregroundColor(AppTheme.secondaryText)
                    .fixedSize()
            }
        }
        .accessibilityElement(children: .combine)
    }
}

// MARK: - WeakItemView (from StatsView)

struct WeakItemView: View {
    let weak: WeakQuestion
    @ObservedObject var localizer: Localizer

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("Q\(weak.id)")
                .font(AppTheme.body(14)).fontWeight(.semibold)
            HStack(spacing: 4) {
                Text(localizer.localized("missed"))
                    .font(AppTheme.body(14))
                    .foregroundColor(AppTheme.secondaryText)
                Text("\(weak.wrong)/\(weak.seen) (\(Int(round(weak.missRate * 100)))%)")
                    .font(AppTheme.body(14)).fontWeight(.semibold)
                    .foregroundColor(AppTheme.errorText)
                Text("\u{00B7}")
                    .foregroundColor(AppTheme.secondaryText)
                Text(localizer.localizedCategory(weak.category))
                    .font(AppTheme.body(14))
                    .foregroundColor(AppTheme.secondaryText)
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
                    Text("\(pct)%").font(AppTheme.body(14)).foregroundColor(AppTheme.secondaryText),
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
                let color: Color = data[i].total > 0 && data[i].correct * 100 >= data[i].total * passingPct ? AppTheme.green : AppTheme.red
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
                        Text("#\(startNum + i)").font(AppTheme.body(14)).foregroundColor(AppTheme.secondaryText),
                        at: CGPoint(x: p.x, y: size.height - pad.bottom + 16),
                        anchor: .center
                    )
                }
            }
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(Localizer.shared.localized("scoreHistory"))
        .accessibilityValue(history.suffix(20).enumerated().map { index, entry in
            "#\(history.count - min(history.count, 20) + index + 1): \(entry.correct)/\(entry.total), \(entry.pct)%"
        }.joined(separator: "; "))
    }
}
