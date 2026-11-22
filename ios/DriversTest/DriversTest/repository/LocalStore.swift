import Foundation

class LocalStore {
    static let shared = LocalStore()
    private let defaults: UserDefaults

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()

    private func storeKey(for stateCode: String, language: String? = nil) -> String {
        "quiz_\(stateCode)" + (language.map { "_\($0)" } ?? "")
    }

    func loadStore(for stateCode: String, language: String? = nil) -> QuizStore {
        guard let data = defaults.data(forKey: storeKey(for: stateCode, language: language)),
              let store = try? decoder.decode(QuizStore.self, from: data) else {
            return .empty
        }
        return store
    }

    func saveStore(_ store: QuizStore, for stateCode: String, language: String? = nil) {
        if let data = try? encoder.encode(store) {
            defaults.set(data, forKey: storeKey(for: stateCode, language: language))
        }
    }

    func clearStore(for stateCode: String) {
        let prefix = storeKey(for: stateCode)
        for key in defaults.dictionaryRepresentation().keys where key == prefix || key.hasPrefix(prefix + "_")
            || key.hasPrefix("study_ack_\(stateCode)_") {
            defaults.removeObject(forKey: key)
        }
    }

    func hasAcknowledgedStudyLanguage(state: String, language: String) -> Bool {
        defaults.bool(forKey: "study_ack_\(state)_\(language)")
    }

    func acknowledgeStudyLanguage(state: String, language: String) {
        defaults.set(true, forKey: "study_ack_\(state)_\(language)")
    }

    var savedStateCode: String? {
        get { defaults.string(forKey: "quiz_state") }
        set { defaults.set(newValue, forKey: "quiz_state") }
    }

    var savedLanguage: String {
        get { defaults.string(forKey: "quiz_lang") ?? "en" }
        set { defaults.set(newValue, forKey: "quiz_lang") }
    }

    func getWeakQuestions(for stateCode: String, language: String? = nil) -> [WeakQuestion] {
        let store = loadStore(for: stateCode, language: language)
        var weak: [WeakQuestion] = []
        for (idStr, record) in store.questions {
            guard let id = Int(idStr), record.wrong > 0, record.seen >= 1 else { continue }
            weak.append(WeakQuestion(
                id: id,
                missRate: Double(record.wrong) / Double(record.seen),
                wrong: record.wrong,
                seen: record.seen,
                category: record.category
            ))
        }
        weak.sort { ($0.missRate, $0.wrong) > ($1.missRate, $1.wrong) }
        return weak
    }
}
