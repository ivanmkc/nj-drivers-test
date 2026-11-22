import Foundation
import SwiftUI

class Localizer: ObservableObject {
    static let shared = Localizer()

    @Published var currentLang: String {
        didSet { storage.savedLanguage = currentLang }
    }

    let langLabels: [String: String] = ["en": "EN", "ja": "日本語", "es": "ES", "fr": "FR"]

    private var translations: [String: [String: String]] = [:]

    private let storage: LocalStore

    init(storage: LocalStore = .shared) {
        self.storage = storage
        self.currentLang = storage.savedLanguage
        loadTranslations()
    }

    private func loadTranslations() {
        guard let url = Bundle.main.url(forResource: "translations", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let decoded = try? JSONDecoder().decode([String: [String: String]].self, from: data) else {
            assertionFailure("Required translations.json resource could not load")
            return
        }
        translations = decoded
    }

    func localized(_ key: String, substitutions: [String: String] = [:]) -> String {
        var s = translations[currentLang]?[key] ?? translations["en"]?[key] ?? key
        for (k, v) in substitutions {
            s = s.replacingOccurrences(of: "{\(k)}", with: v)
        }
        return s
    }

    func localizedCategory(_ key: String) -> String {
        let i18nKey = "cat_" + key
        let result = translations[currentLang]?[i18nKey] ?? translations["en"]?[i18nKey]
        if let result, result != i18nKey { return result }
        return key.replacingOccurrences(of: "_", with: " ").capitalized
    }

    func fromManualLabel() -> String {
        let base = localized("fromTheManual")
        let note = localized("fromTheManualEnNote")
        if note.isEmpty { return base }
        return base + " " + note
    }
}
