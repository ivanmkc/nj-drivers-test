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
