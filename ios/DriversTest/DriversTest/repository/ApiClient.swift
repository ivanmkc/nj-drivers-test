import Compression
import Foundation

// MARK: - Bundle wire-format (private)

private struct RawBundle: Codable {
    let states: [BundleState]
}

private struct BundleState: Codable {
    let code: String
    let name: String
    let agency: String
    let passingScorePct: Int
    let testQuestionCount: Int
    let source: String?
    let officialTestLanguages: [String]?
    let categories: [String: Int]?
    let verification: BundleVerification?
    let languages: [String: [BundledQuestion]]

    enum CodingKeys: String, CodingKey {
        case code, name, agency, source, categories, verification, languages
        case passingScorePct = "passing_score_pct"
        case testQuestionCount = "test_question_count"
        case officialTestLanguages = "official_test_languages"
    }
}

private struct BundleVerification: Codable {
    let verifiedAt: String?
    let overall: String?
    let manualUrl: String?
    let edition: String?
    let manualPages: Int?
    let precisionAvgFidelity: Double?
    let precisionGrade: String?
    let questionsJudged: Int?
    let recallCoveragePct: Double?
    let translations: [String: String]?

    enum CodingKeys: String, CodingKey {
        case overall, edition, translations
        case verifiedAt = "verified_at"
        case manualUrl = "manual_url"
        case manualPages = "manual_pages"
        case precisionAvgFidelity = "precision_avg_fidelity"
        case precisionGrade = "precision_grade"
        case questionsJudged = "questions_judged"
        case recallCoveragePct = "recall_coverage_pct"
    }

    func toStateVerification() -> StateVerification {
        StateVerification(
            verifiedAt: verifiedAt,
            overall: overall,
            manualUrl: manualUrl,
            edition: edition,
            manualPages: manualPages,
            precisionAvgFidelity: precisionAvgFidelity,
            precisionGrade: precisionGrade,
            questionsJudged: questionsJudged,
            recallCoveragePct: recallCoveragePct,
            translations: translations
        )
    }
}

// MARK: - Public question model

struct BundledQuestion: Codable {
    let id: Int
    let category: String
    let question: String
    let choices: [String: String]
    let answer: String
    let explanation: String
    let image: String?
    let evidence: [String]?
}

// MARK: - ApiClient

class ApiClient {
    static let shared = ApiClient()

    private var stateList: [StateInfo] = []
    private var questionsByState: [String: [String: [BundledQuestion]]] = [:]
    private var answerIndex: [String: [String: [Int: BundledQuestion]]] = [:]
    private var loaded = false

    enum LoadError: Error, LocalizedError {
        case fileNotFound
        case decompressFailed
        case decodeFailed(Error)

        var errorDescription: String? {
            switch self {
            case .fileNotFound: return "Question bundle not found."
            case .decompressFailed: return "Failed to decompress question bundle."
            case .decodeFailed(let error): return "Failed to decode questions: \(error.localizedDescription)"
            }
        }
    }

    private init() {}

    func loadBundle() throws {
        guard !loaded else { return }
        guard let url = Bundle.main.url(forResource: "questions_bundle.json", withExtension: "gz") else {
            throw LoadError.fileNotFound
        }
        let compressed = try Data(contentsOf: url)
        guard let decompressed = Self.decompress(compressed) else {
            throw LoadError.decompressFailed
        }

        let raw: RawBundle
        do {
            raw = try JSONDecoder().decode(RawBundle.self, from: decompressed)
        } catch {
            throw LoadError.decodeFailed(error)
        }

        var infos: [StateInfo] = []
        var allQuestions: [String: [String: [BundledQuestion]]] = [:]

        for bs in raw.states {
            let langCodes = bs.languages.keys.sorted()
            let enCount = bs.languages["en"]?.count ?? 0

            let info = StateInfo(
                code: bs.code,
                name: bs.name,
                agency: bs.agency,
                passingScorePct: bs.passingScorePct,
                testQuestionCount: bs.testQuestionCount,
                languages: langCodes,
                totalQuestions: enCount,
                hasQuestions: enCount > 0,
                source: bs.source,
                categories: bs.categories,
                verification: bs.verification?.toStateVerification(),
                officialTestLanguages: bs.officialTestLanguages
            )
            infos.append(info)
            allQuestions[bs.code] = bs.languages
        }

        stateList = infos
        questionsByState = allQuestions
        buildAnswerIndex()
        loaded = true
    }

    private func buildAnswerIndex() {
        var index: [String: [String: [Int: BundledQuestion]]] = [:]
        for (state, langs) in questionsByState {
            for (lang, questions) in langs {
                var byId: [Int: BundledQuestion] = [:]
                for q in questions { byId[q.id] = q }
                index[state, default: [:]][lang] = byId
            }
        }
        answerIndex = index
    }

    private static func decompress(_ data: Data) -> Data? {
        guard data.count > 10, data[0] == 0x1f, data[1] == 0x8b else { return data }
        var offset = 10
        let flags = data[3]
        if flags & 0x04 != 0 {
            guard offset + 2 <= data.count else { return nil }
            let xlen = Int(data[offset]) | (Int(data[offset + 1]) << 8)
            offset += 2 + xlen
        }
        if flags & 0x08 != 0 {
            while offset < data.count && data[offset] != 0 { offset += 1 }
            offset += 1
        }
        if flags & 0x10 != 0 {
            while offset < data.count && data[offset] != 0 { offset += 1 }
            offset += 1
        }
        if flags & 0x02 != 0 { offset += 2 }

        let deflateData = data.subdata(in: offset..<(data.count - 8))
        return deflateData.withUnsafeBytes { src -> Data? in
            guard let srcPtr = src.baseAddress?.assumingMemoryBound(to: UInt8.self) else { return nil }
            var result = Data()
            let chunkSize = 65536
            let dst = UnsafeMutablePointer<UInt8>.allocate(capacity: chunkSize)
            defer { dst.deallocate() }
            let stream = UnsafeMutablePointer<compression_stream>.allocate(capacity: 1)
            defer { stream.deallocate() }
            var status = compression_stream_init(stream, COMPRESSION_STREAM_DECODE, COMPRESSION_ZLIB)
            guard status == COMPRESSION_STATUS_OK else { return nil }
            defer { compression_stream_destroy(stream) }
            stream.pointee.src_ptr = srcPtr
            stream.pointee.src_size = deflateData.count
            repeat {
                stream.pointee.dst_ptr = dst
                stream.pointee.dst_size = chunkSize
                status = compression_stream_process(stream, 0)
                let written = chunkSize - stream.pointee.dst_size
                if written > 0 { result.append(dst, count: written) }
            } while status == COMPRESSION_STATUS_OK
            return status == COMPRESSION_STATUS_END ? result : nil
        }
    }

    func fetchStates() -> [StateInfo] {
        stateList
    }

    func fetchQuiz(state: String, lang: String, count: Int) -> [QuizQuestion] {
        guard let langQuestions = questionsByState[state]?[lang] ?? questionsByState[state]?["en"] else {
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
        guard let langIndex = answerIndex[state]?[lang] ?? answerIndex[state]?["en"],
              let q = langIndex[questionId] else {
            return nil
        }
        return AnswerResponse(id: q.id, answer: q.answer, explanation: q.explanation)
    }

    func fetchEvidence(questionId: Int, state: String) -> [String]? {
        answerIndex[state]?["en"]?[questionId]?.evidence
    }

}
