import Foundation

struct QuestionBundle: Codable {
    let states: [StateInfo]
    let questions: [String: [String: [BundledQuestion]]]
}

struct BundledQuestion: Codable {
    let id: Int
    let category: String
    let question: String
    let choices: [String: String]
    let answer: String
    let explanation: String
    let image: String?
}

class ApiClient {
    static let shared = ApiClient()

    private var bundle: QuestionBundle?

    init() {
        loadBundle()
    }

    private func loadBundle() {
        guard let url = Bundle.main.url(forResource: "questions_bundle.json", withExtension: "gz") else {
            return
        }
        guard let compressed = try? Data(contentsOf: url) else { return }
        guard let decompressed = decompress(compressed) else { return }
        bundle = try? JSONDecoder().decode(QuestionBundle.self, from: decompressed)
    }

    private func decompress(_ data: Data) -> Data? {
        // gzip starts with 1f 8b
        guard data.count > 2, data[0] == 0x1f, data[1] == 0x8b else { return data }
        var result = Data()
        _ = data.withUnsafeBytes { rawBuffer in
            guard let baseAddress = rawBuffer.baseAddress else { return }
            var stream = z_stream()
            stream.next_in = UnsafeMutablePointer(mutating: baseAddress.assumingMemoryBound(to: UInt8.self))
            stream.avail_in = uInt(data.count)
            guard inflateInit2_(&stream, 15 + 32, ZLIB_VERSION, Int32(MemoryLayout<z_stream>.size)) == Z_OK else { return }
            defer { inflateEnd(&stream) }
            var buffer = [UInt8](repeating: 0, count: 65536)
            repeat {
                stream.next_out = &buffer
                stream.avail_out = uInt(buffer.count)
                let status = inflate(&stream, Z_NO_FLUSH)
                let outputCount = buffer.count - Int(stream.avail_out)
                if outputCount > 0 {
                    result.append(buffer, count: outputCount)
                }
                if status == Z_STREAM_END { break }
                if status != Z_OK { break }
            } while true
        }
        return result.isEmpty ? nil : result
    }

    func fetchStates() -> [StateInfo] {
        bundle?.states ?? []
    }

    func fetchQuiz(state: String, lang: String, count: Int) -> [QuizQuestion] {
        guard let stateQuestions = bundle?.questions[state],
              let langQuestions = stateQuestions[lang] ?? stateQuestions["en"] else {
            return []
        }

        let selected = Array(langQuestions.shuffled().prefix(count))
        return selected.map { q in
            QuizQuestion(
                id: q.id,
                category: q.category,
                question: q.question,
                choices: q.choices,
                image: q.image
            )
        }
    }

    func fetchAnswer(questionId: Int, state: String, lang: String) -> AnswerResponse? {
        guard let stateQuestions = bundle?.questions[state],
              let langQuestions = stateQuestions[lang] ?? stateQuestions["en"],
              let q = langQuestions.first(where: { $0.id == questionId }) else {
            return nil
        }
        return AnswerResponse(id: q.id, answer: q.answer, explanation: q.explanation)
    }

    func signImageName(_ filename: String) -> String {
        "signs/\(filename)"
    }
}
