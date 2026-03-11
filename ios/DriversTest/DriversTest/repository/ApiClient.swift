import Foundation

class ApiClient {
    static let shared = ApiClient()

    let baseURL = "http://localhost:8080"

    private let decoder = JSONDecoder()

    func fetchStates() async throws -> [StateInfo] {
        guard let url = URL(string: "\(baseURL)/api/states") else {
            throw APIError.invalidURL
        }
        let (data, _) = try await URLSession.shared.data(from: url)
        let response = try decoder.decode(StatesResponse.self, from: data)
        return response.states
    }

    func fetchQuiz(state: String, lang: String, count: Int) async throws -> [QuizQuestion] {
        var components = URLComponents(string: "\(baseURL)/api/quiz/\(count)")
        components?.queryItems = [
            URLQueryItem(name: "state", value: state),
            URLQueryItem(name: "lang", value: lang),
        ]
        guard let url = components?.url else {
            throw APIError.invalidURL
        }
        let (data, _) = try await URLSession.shared.data(from: url)
        let response = try decoder.decode(QuizResponse.self, from: data)
        return response.questions
    }

    func fetchAnswer(questionId: Int, state: String, lang: String) async throws -> AnswerResponse {
        var components = URLComponents(string: "\(baseURL)/api/answer/\(questionId)")
        components?.queryItems = [
            URLQueryItem(name: "state", value: state),
            URLQueryItem(name: "lang", value: lang),
        ]
        guard let url = components?.url else {
            throw APIError.invalidURL
        }
        let (data, _) = try await URLSession.shared.data(from: url)
        return try decoder.decode(AnswerResponse.self, from: data)
    }

    func signImageURL(state: String, filename: String) -> URL? {
        URL(string: "\(baseURL)/signs/\(state)/\(filename)")
    }
}

enum APIError: Error {
    case invalidURL
}
