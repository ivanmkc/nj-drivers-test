import SwiftUI

struct StatsView: View {
    @ObservedObject var vm: QuizViewModel
    @ObservedObject var localizer: Localizer
    @State private var showResetAlert = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Back button
                Button {
                    vm.goHome()
                } label: {
                    HStack(spacing: 6) {
                        Image(systemName: "chevron.left")
                        Text(localizer.t("back"))
                    }
                    .font(.system(size: 15, weight: .semibold))
                    .foregroundColor(Color("Blue"))
                }

                Text(localizer.t("yourProgress"))
                    .font(.system(size: 22, weight: .bold))

                // Top stats grid
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                ], spacing: 10) {
                    StatCardView(value: "\(vm.quizHistory.count)", label: localizer.t("quizzes"), color: Color("Blue"))
                    StatCardView(value: "\(vm.averageScore)%", label: localizer.t("avgScore"), color: Color("Green"))
                    StatCardView(value: "\(vm.questionsSeen)", label: localizer.t("qsSeen"), color: .primary)
                }

                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                ], spacing: 10) {
                    StatCardView(value: "\(vm.passStreak)", label: localizer.t("passStreak"), color: Color("Green"))
                    StatCardView(value: "\(vm.bestScore)%", label: localizer.t("bestScore"), color: .primary)
                }

                // Score history chart
                VStack(alignment: .leading, spacing: 12) {
                    Text(localizer.t("scoreHistory"))
                        .font(.system(size: 15, weight: .semibold))

                    if vm.quizHistory.count >= 2 {
                        ScoreChartView(
                            history: vm.quizHistory,
                            passingPct: vm.currentState?.passingScorePct ?? 70
                        )
                        .frame(height: 180)
                    } else {
                        Text(vm.quizHistory.isEmpty ? "Take a quiz to see your progress" : "Take one more quiz to see the chart")
                            .font(.system(size: 14))
                            .foregroundColor(Color("Gray"))
                            .frame(maxWidth: .infinity)
                            .frame(height: 120)
                    }
                }
                .padding(16)
                .background(Color.white)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color(.systemGray4), lineWidth: 1)
                )
                .clipShape(RoundedRectangle(cornerRadius: 12))

                // Category bars
                if !vm.categoryStats.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text(localizer.t("accuracyByCategory"))
                            .font(.system(size: 15, weight: .semibold))

                        ForEach(vm.categoryStats, id: \.category) { cat in
                            CategoryBarView(category: cat.category, pct: cat.pct)
                        }
                    }
                }

                // Weak questions
                let weak = vm.weakQuestions
                if !weak.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text(localizer.t("mostMissed"))
                            .font(.system(size: 15, weight: .semibold))

                        ForEach(weak.prefix(15)) { w in
                            WeakItemView(weak: w, localizer: localizer)
                        }
                    }
                }

                // Reset button
                Divider()
                    .padding(.top, 8)

                Button {
                    showResetAlert = true
                } label: {
                    Text(localizer.t("resetAll"))
                        .font(.system(size: 15, weight: .semibold))
                        .foregroundColor(Color("Red"))
                        .frame(maxWidth: .infinity)
                        .padding(12)
                        .background(Color.white)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color("RedLight"), lineWidth: 2)
                        )
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .alert(localizer.t("resetConfirm", vars: ["state_name": vm.currentState?.name ?? ""]), isPresented: $showResetAlert) {
                    Button("Cancel", role: .cancel) {}
                    Button("Reset", role: .destructive) {
                        vm.clearData()
                    }
                }
            }
            .padding(16)
        }
        .background(Color("GrayLight"))
    }
}

struct StatCardView: View {
    let value: String
    let label: String
    let color: Color

    var body: some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.system(size: 26, weight: .bold))
                .foregroundColor(color)
            Text(label)
                .font(.system(size: 11))
                .foregroundColor(Color("Gray"))
                .textCase(.uppercase)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 16)
        .background(Color.white)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color(.systemGray4), lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

struct CategoryBarView: View {
    let category: String
    let pct: Int

    private var barColor: Color {
        if pct >= 80 { return Color("Green") }
        if pct >= 60 { return Color("Orange") }
        return Color("Red")
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
                        .fill(Color(.systemGray4))
                        .frame(height: 10)
                    RoundedRectangle(cornerRadius: 5)
                        .fill(barColor)
                        .frame(width: geo.size.width * CGFloat(pct) / 100.0, height: 10)
                }
            }
            .frame(height: 10)

            Text("\(pct)%")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(barColor)
                .frame(width: 36, alignment: .trailing)
        }
    }
}

struct WeakItemView: View {
    let weak: WeakQuestion
    @ObservedObject var localizer: Localizer

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("Q\(weak.id)")
                .font(.system(size: 14, weight: .semibold))
            HStack(spacing: 4) {
                Text(localizer.t("missed"))
                    .font(.system(size: 12))
                    .foregroundColor(Color("Gray"))
                Text("\(weak.wrong)/\(weak.seen) (\(Int(round(weak.missRate * 100)))%)")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(Color("Red"))
                Text("·")
                    .foregroundColor(Color("Gray"))
                Text(weak.category.replacingOccurrences(of: "_", with: " "))
                    .font(.system(size: 12))
                    .foregroundColor(Color("Gray"))
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 14)
        .padding(.vertical, 12)
        .background(Color.white)
        .overlay(
            HStack(spacing: 0) {
                Rectangle()
                    .fill(Color("Orange"))
                    .frame(width: 4)
                Spacer()
            }
        )
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color(.systemGray4), lineWidth: 1)
        )
    }
}

// Simple score chart using SwiftUI Canvas
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
                context.stroke(path, with: .color(Color(.systemGray4)), lineWidth: 1)

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
            context.stroke(passPath, with: .color(Color.green.opacity(0.3)), style: StrokeStyle(lineWidth: 2, dash: [6, 4]))

            // Data points
            let points: [CGPoint] = data.enumerated().map { i, d in
                let x = pad.leading + (n == 1 ? plotW / 2 : CGFloat(i) / CGFloat(n - 1) * plotW)
                let y = pad.top + plotH - (CGFloat(d.pct) / 100.0) * plotH
                return CGPoint(x: x, y: y)
            }

            // Line
            if points.count >= 2 {
                var linePath = Path()
                linePath.move(to: points[0])
                for p in points.dropFirst() { linePath.addLine(to: p) }
                context.stroke(linePath, with: .color(Color("Blue")), lineWidth: 2.5)

                // Fill
                var fillPath = linePath
                fillPath.addLine(to: CGPoint(x: points.last!.x, y: pad.top + plotH))
                fillPath.addLine(to: CGPoint(x: points.first!.x, y: pad.top + plotH))
                fillPath.closeSubpath()

                let gradient = Gradient(colors: [Color("Blue").opacity(0.2), Color("Blue").opacity(0.02)])
                context.fill(fillPath, with: .linearGradient(gradient, startPoint: CGPoint(x: 0, y: pad.top), endPoint: CGPoint(x: 0, y: pad.top + plotH)))
            }

            // Dots
            for (i, p) in points.enumerated() {
                let color: Color = data[i].pct >= passingPct ? Color("Green") : Color("Red")
                var dotPath = Path()
                dotPath.addEllipse(in: CGRect(x: p.x - 4, y: p.y - 4, width: 8, height: 8))
                context.fill(dotPath, with: .color(color))
                context.stroke(dotPath, with: .color(.white), lineWidth: 2)
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
