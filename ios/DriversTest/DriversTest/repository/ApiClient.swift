import Foundation

class ApiClient {
    static let shared = ApiClient()

    // Change this to your server URL
    var baseURL: String {
        #if targetEnvironment(simulator)
        "http://localhost:8080"
        #else
        "http://localhost:8080" // Update for production
        #endif
    }

    private let decoder: JSONDecoder = {
        let d = JSONDecoder()
        return d
    }()

    func fetchStates() async throws -> [StateInfo] {
        let url = URL(string: "\(baseURL)/api/states")!
        let (data, _) = try await URLSession.shared.data(from: url)
        let response = try decoder.decode(StatesResponse.self, from: data)
        return response.states
    }

    func fetchQuiz(state: String, lang: String, count: Int) async throws -> [QuizQuestion] {
        let url = URL(string: "\(baseURL)/api/quiz/\(count)?state=\(state)&lang=\(lang)")!
        let (data, _) = try await URLSession.shared.data(from: url)
        let response = try decoder.decode(QuizResponse.self, from: data)
        return response.questions
    }

    func fetchAnswer(questionId: Int, state: String, lang: String) async throws -> AnswerResponse {
        let url = URL(string: "\(baseURL)/api/answer/\(questionId)?state=\(state)&lang=\(lang)")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try decoder.decode(AnswerResponse.self, from: data)
    }

    func signImageURL(state: String, filename: String) -> URL? {
        URL(string: "\(baseURL)/signs/\(state)/\(filename)")
    }
}
