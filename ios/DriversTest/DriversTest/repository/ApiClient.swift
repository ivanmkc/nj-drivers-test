import Compression
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

    // Not thread-safe — must only be called from QuizViewModel's single load path.
    func loadBundle() throws {
        guard !loaded else { return }
        guard let url = Bundle.main.url(forResource: "questions_bundle.json", withExtension: "gz") else {
            throw LoadError.fileNotFound
        }
        let compressed = try Data(contentsOf: url)
        guard let decompressed = Self.decompress(compressed) else {
            throw LoadError.decompressFailed
        }
        do {
            bundle = try JSONDecoder().decode(QuestionBundle.self, from: decompressed)
        } catch {
            throw LoadError.decodeFailed(error)
        }
        buildAnswerIndex()
        loaded = true
    }

    private func buildAnswerIndex() {
        guard let bundle = bundle else { return }
        var index: [String: [String: [Int: BundledQuestion]]] = [:]
        for (state, langs) in bundle.questions {
            for (lang, questions) in langs {
                var byId: [Int: BundledQuestion] = [:]
                for q in questions { byId[q.id] = q }
                index[state, default: [:]][lang] = byId
            }
        }
        answerIndex = index
    }

    private static func decompress(_ data: Data) -> Data? {
        // gzip starts with 1f 8b; strip the 10-byte gzip header for raw DEFLATE
        guard data.count > 10, data[0] == 0x1f, data[1] == 0x8b else { return data }
        // Find start of DEFLATE stream: skip 10-byte header + optional extras
        var offset = 10
        let flags = data[3]
        if flags & 0x04 != 0 { // FEXTRA
            guard offset + 2 <= data.count else { return nil }
            let xlen = Int(data[offset]) | (Int(data[offset + 1]) << 8)
            offset += 2 + xlen
        }
        if flags & 0x08 != 0 { // FNAME
            while offset < data.count && data[offset] != 0 { offset += 1 }
            offset += 1
        }
        if flags & 0x10 != 0 { // FCOMMENT
            while offset < data.count && data[offset] != 0 { offset += 1 }
            offset += 1
        }
        if flags & 0x02 != 0 { offset += 2 } // FHCRC

        let deflateData = data.subdata(in: offset..<(data.count - 8)) // strip 8-byte trailer
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
        guard let langIndex = answerIndex[state]?[lang] ?? answerIndex[state]?["en"],
              let q = langIndex[questionId] else {
            return nil
        }
        return AnswerResponse(id: q.id, answer: q.answer, explanation: q.explanation)
    }

}
