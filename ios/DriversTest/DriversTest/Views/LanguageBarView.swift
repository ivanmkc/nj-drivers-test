import SwiftUI

struct LanguageBarView: View {
    @ObservedObject var localizer: Localizer
    var availableLangs: [String]?

    private var langs: [String] {
        availableLangs ?? ["en", "ja", "es"]
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
                        .foregroundColor(lang == localizer.currentLang ? Color("Blue") : Color("Gray"))
                        .background(lang == localizer.currentLang ? Color("BlueLight") : Color.white)
                        .overlay(
                            RoundedRectangle(cornerRadius: 20)
                                .stroke(lang == localizer.currentLang ? Color("Blue") : Color(.systemGray4), lineWidth: 1.5)
                        )
                        .clipShape(RoundedRectangle(cornerRadius: 20))
                }
            }
        }
    }
}
