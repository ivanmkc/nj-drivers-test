import SwiftUI

struct SourceCitationView: View {
    let state: StateInfo?
    @ObservedObject private var localizer = Localizer.shared

    var body: some View {
        if let state {
            HStack(alignment: .top, spacing: 10) {
                Rectangle().fill(AppTheme.accent).frame(width: 3)
                VStack(alignment: .leading, spacing: 4) {
                    Text(state.agency).font(AppTheme.body(14, relativeTo: .caption)).fontWeight(.semibold)
                    if let raw = state.manualURL ?? state.verification?.manualUrl, let url = URL(string: raw) {
                        Link(destination: url) {
                            Text(state.contentReviewRequired ? localizer.localized("currentHandbook") : (state.source ?? state.name))
                                .foregroundColor(AppTheme.navy)
                                .multilineTextAlignment(.leading)
                                .fixedSize(horizontal: false, vertical: true)
                                .frame(maxWidth: .infinity, minHeight: 44, alignment: .leading)
                                .contentShape(Rectangle())
                        }
                        .accessibilityIdentifier("current-handbook-link")
                    } else {
                        Text(state.source ?? state.name)
                    }
                    if state.contentReviewRequired {
                        Text(localizer.localized("contentReviewNotice"))
                            .accessibilityIdentifier("bank-content-review")
                            .font(.subheadline)
                            .foregroundColor(AppTheme.secondaryText)
                    }
                    if let edition = state.verification?.edition, !edition.isEmpty {
                        Text(localizer.localized("bankEdition") + " " + edition)
                            .font(AppTheme.body(14, relativeTo: .caption)).foregroundColor(AppTheme.secondaryText)
                    }
                }
                .font(.subheadline)
            }
            .fixedSize(horizontal: false, vertical: true)
            .padding(12)
            .background(AppTheme.card)
            .accessibilityElement(children: .contain)
        }
    }
}
