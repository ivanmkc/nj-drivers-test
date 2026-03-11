import Foundation

class StorageService {
    static let shared = StorageService()
    private let defaults = UserDefaults.standard

    private func storeKey(for stateCode: String) -> String {
        "quiz_\(stateCode)"
    }

    func loadStore(for stateCode: String) -> QuizStore {
        guard let data = defaults.data(forKey: storeKey(for: stateCode)),
              let store = try? JSONDecoder().decode(QuizStore.self, from: data) else {
            return .empty
        }
        return store
    }

    func saveStore(_ store: QuizStore, for stateCode: String) {
        if let data = try? JSONEncoder().encode(store) {
            defaults.set(data, forKey: storeKey(for: stateCode))
        }
    }

    func clearStore(for stateCode: String) {
        defaults.removeObject(forKey: storeKey(for: stateCode))
    }

    // Saved state code
    var savedStateCode: String? {
        get { defaults.string(forKey: "quiz_state") }
        set { defaults.set(newValue, forKey: "quiz_state") }
    }

    // Language
    var savedLanguage: String {
        get { defaults.string(forKey: "quiz_lang") ?? "en" }
        set { defaults.set(newValue, forKey: "quiz_lang") }
    }

    // Weak questions
    func getWeakQuestions(for stateCode: String) -> [WeakQuestion] {
        let store = loadStore(for: stateCode)
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
