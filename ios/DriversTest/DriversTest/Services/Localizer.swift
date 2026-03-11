import Foundation
import SwiftUI

class Localizer: ObservableObject {
    static let shared = Localizer()

    @Published var currentLang: String {
        didSet { StorageService.shared.savedLanguage = currentLang }
    }

    let langLabels: [String: String] = ["en": "EN", "ja": "日本語", "es": "ES"]

    private var translations: [String: [String: String]] = [:]

    init() {
        self.currentLang = StorageService.shared.savedLanguage
        loadTranslations()
    }

    private func loadTranslations() {
        translations = [
            "en": [
                "appTitle": "Driver's Test Practice",
                "selectStateDesc": "Choose your state to start practicing",
                "questionsAvailable": "{count} questions",
                "comingSoon": "Coming soon",
                "title": "{state} Driver's Test",
                "subtitle": "Practice for your {state_name} {agency} written test.",
                "quizzes": "Quizzes",
                "avgScore": "Avg Score",
                "passStreak": "Pass Streak",
                "viewStats": "View Stats",
                "modeRandom": "Random",
                "modeRandomDesc": "All questions",
                "modeWeak": "Weak Spots",
                "modeWeakDesc": "Most missed",
                "numQuestions": "Number of questions:",
                "startQuiz": "Start Quiz",
                "noWeakSpots": "No weak spots yet",
                "next": "Next",
                "seeResults": "See Results",
                "missed": "Missed",
                "congratulations": "Congratulations!",
                "keepPracticing": "Keep Practicing!",
                "resultDetail": "You got {correct} out of {total} correct. You need {pass_pct}% to pass the actual {agency} test.",
                "newQuiz": "New Quiz",
                "reviewMissed": "Review Missed Questions ({count})",
                "perfectScore": "Perfect Score!",
                "perfectMsg": "You answered every question correctly.",
                "yourAnswer": "Your answer",
                "correct": "Correct",
                "back": "Back",
                "changeState": "Change State",
                "yourProgress": "Your Progress",
                "qsSeen": "Q's Seen",
                "bestScore": "Best Score",
                "scoreHistory": "Score History",
                "accuracyByCategory": "Accuracy by Category",
                "mostMissed": "Most Missed Questions",
                "resetAll": "Reset All Progress",
                "resetConfirm": "This will erase all your quiz history and question tracking for {state_name}. Continue?",
                "pass": "PASS",
                "fail": "FAIL",
                "passingScore": "Passing: {pass_pct}% ({pass_count}/{test_count})",
            ],
            "ja": [
                "appTitle": "運転免許テスト練習",
                "selectStateDesc": "練習を開始するには州を選んでください",
                "questionsAvailable": "{count}問",
                "comingSoon": "準備中",
                "title": "{state} 運転免許テスト",
                "subtitle": "{state_name} {agency}の筆記試験対策。",
                "quizzes": "テスト回数",
                "avgScore": "平均点",
                "passStreak": "連続合格",
                "viewStats": "統計を見る",
                "modeRandom": "ランダム",
                "modeRandomDesc": "全問題",
                "modeWeak": "弱点",
                "modeWeakDesc": "よく間違える問題",
                "numQuestions": "問題数：",
                "startQuiz": "テスト開始",
                "noWeakSpots": "弱点はまだありません",
                "next": "次へ",
                "seeResults": "結果を見る",
                "missed": "不正解率",
                "congratulations": "おめでとうございます！",
                "keepPracticing": "もっと練習しましょう！",
                "resultDetail": "{total}問中{correct}問正解です。{agency}試験の合格ラインは{pass_pct}%です。",
                "newQuiz": "新しいテスト",
                "reviewMissed": "間違えた問題を復習 ({count})",
                "perfectScore": "満点！",
                "perfectMsg": "すべての問題に正解しました。",
                "yourAnswer": "あなたの回答",
                "correct": "正解",
                "back": "戻る",
                "changeState": "州を変更",
                "yourProgress": "あなたの成績",
                "qsSeen": "出題済み",
                "bestScore": "最高点",
                "scoreHistory": "スコア推移",
                "accuracyByCategory": "カテゴリー別正答率",
                "mostMissed": "最もよく間違える問題",
                "resetAll": "すべての記録をリセット",
                "resetConfirm": "{state_name}のすべてのテスト履歴と問題追跡データが消去されます。よろしいですか？",
                "pass": "合格",
                "fail": "不合格",
                "passingScore": "合格ライン: {pass_pct}% ({pass_count}/{test_count})",
            ],
            "es": [
                "appTitle": "Práctica de Examen de Conducir",
                "selectStateDesc": "Elige tu estado para empezar a practicar",
                "questionsAvailable": "{count} preguntas",
                "comingSoon": "Próximamente",
                "title": "Examen de Conducir {state}",
                "subtitle": "Practica para el examen escrito del {agency} de {state_name}.",
                "quizzes": "Pruebas",
                "avgScore": "Promedio",
                "passStreak": "Racha",
                "viewStats": "Ver Estadísticas",
                "modeRandom": "Aleatorio",
                "modeRandomDesc": "Todas las preguntas",
                "modeWeak": "Puntos Débiles",
                "modeWeakDesc": "Más falladas",
                "numQuestions": "Número de preguntas:",
                "startQuiz": "Comenzar",
                "noWeakSpots": "Sin puntos débiles aún",
                "next": "Siguiente",
                "seeResults": "Ver Resultados",
                "missed": "Fallada",
                "congratulations": "¡Felicidades!",
                "keepPracticing": "¡Sigue Practicando!",
                "resultDetail": "Acertaste {correct} de {total}. Necesitas {pass_pct}% para aprobar el examen del {agency}.",
                "newQuiz": "Nuevo Examen",
                "reviewMissed": "Revisar Preguntas Falladas ({count})",
                "perfectScore": "¡Puntuación Perfecta!",
                "perfectMsg": "Respondiste correctamente todas las preguntas.",
                "yourAnswer": "Tu respuesta",
                "correct": "Correcta",
                "back": "Volver",
                "changeState": "Cambiar Estado",
                "yourProgress": "Tu Progreso",
                "qsSeen": "Vistas",
                "bestScore": "Mejor",
                "scoreHistory": "Historial de Puntuación",
                "accuracyByCategory": "Precisión por Categoría",
                "mostMissed": "Preguntas Más Falladas",
                "resetAll": "Borrar Todo el Progreso",
                "resetConfirm": "Esto borrará todo tu historial y seguimiento de {state_name}. ¿Continuar?",
                "pass": "APROBADO",
                "fail": "REPROBADO",
                "passingScore": "Aprobación: {pass_pct}% ({pass_count}/{test_count})",
            ],
        ]
    }

    func t(_ key: String, vars: [String: String] = [:]) -> String {
        var s = translations[currentLang]?[key] ?? translations["en"]?[key] ?? key
        for (k, v) in vars {
            s = s.replacingOccurrences(of: "{\(k)}", with: v)
        }
        return s
    }
}
