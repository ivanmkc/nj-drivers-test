import SwiftUI

struct LanguageBarView: View {
    @ObservedObject var localizer: Localizer
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    var availableLangs: [String]?
    var officialTestLanguages: [String]?

    private var langs: [String] {
        availableLangs ?? ["en", "es"]
    }

    private static let langCodeToEnglish: [String: String] = [
        "en": "english", "es": "spanish", "ja": "japanese", "fr": "french",
    ]

    private func isOfficialLang(_ langCode: String) -> Bool {
        guard let official = officialTestLanguages else { return false }
        if official.contains(where: { $0.lowercased() == "many" }) && official.count == 1 {
            return false
        }
        guard let englishName = Self.langCodeToEnglish[langCode]?.lowercased() else { return false }
        return official.contains { $0.lowercased() == englishName }
    }

    @ViewBuilder
    private func languageLabel(_ lang: String, official: Bool) -> some View {
        Text(localizer.langLabels[lang] ?? lang.uppercased())
            .font(lang == "ja" ? .subheadline : AppTheme.body(14)).fontWeight(.semibold)
        if lang != "en" && !official {
            Text(localizer.localized("studyBadge"))
                .font(AppTheme.body(14, relativeTo: .caption))
                .multilineTextAlignment(.center)
        }
        if officialTestLanguages != nil && official {
            Image(systemName: "checkmark.seal").accessibilityHidden(true)
                .font(AppTheme.body(14))
                .foregroundColor(AppTheme.successText)
                .accessibilityHidden(true)
        }
    }

    var body: some View {
        LazyVGrid(columns: dynamicTypeSize.isAccessibilitySize ? [GridItem(.flexible())] :
                    [GridItem(.adaptive(minimum: 96), spacing: 8)], spacing: 8) {
            ForEach(langs, id: \.self) { lang in
                let isOfficial = isOfficialLang(lang)
                Button {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        localizer.currentLang = lang
                    }
                } label: {
                    VStack(spacing: 4) { languageLabel(lang, official: isOfficial) }
                    .frame(maxWidth: .infinity, minHeight: 44)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .foregroundColor(lang == localizer.currentLang ? AppTheme.navy : AppTheme.secondaryText)
                    .background(lang == localizer.currentLang ? AppTheme.blueLight : AppTheme.card)
                    .cardStyle(cornerRadius: 20, borderColor: lang == localizer.currentLang ? AppTheme.blue : AppTheme.border, borderWidth: 1.5)
                    .frame(minHeight: 44)
                    .contentShape(Rectangle())
                }
                .accessibilityIdentifier("language-\(lang)")
                .accessibilityHint(isOfficial ? "Official test language" : "")
            }
        }
    }
}
