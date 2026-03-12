package com.drivers.test.viewmodel

import android.app.Application
import android.util.Log
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import com.drivers.test.model.*
import com.drivers.test.repository.ApiClient
import com.drivers.test.repository.LocalStore
import com.drivers.test.repository.Localizer
import kotlin.math.roundToInt

class QuizViewModel(application: Application) : AndroidViewModel(application) {
    private val api = ApiClient(application)
    private val storage = LocalStore(application)
    val localizer = Localizer()

    var screen by mutableStateOf(AppScreen.STATE_PICKER)
    var allStates = mutableStateListOf<StateInfo>()
    var currentState by mutableStateOf<StateInfo?>(null)
    var isLoading by mutableStateOf(false)
    var errorMessage by mutableStateOf<String?>(null)
    var currentLang by mutableStateOf(storage.savedLanguage)

    // Quiz state
    var questions = mutableStateListOf<QuizQuestion>()
    var currentIndex by mutableIntStateOf(0)
    var correctCount by mutableIntStateOf(0)
    var wrongCount by mutableIntStateOf(0)
    var answered by mutableStateOf(false)
    var selectedAnswer by mutableStateOf<String?>(null)
    var correctAnswer by mutableStateOf<String?>(null)
    var explanation by mutableStateOf<String?>(null)
    var sessionResults = mutableStateListOf<SessionResult>()

    // Settings
    var quizMode by mutableStateOf(QuizMode.RANDOM)
    var selectedCount by mutableIntStateOf(50)

    // Derived state helpers
    private fun store(): QuizStore {
        val state = currentState ?: return QuizStore()
        return storage.loadStore(state.code)
    }

    fun weakQuestions(): List<WeakQuestion> {
        val state = currentState ?: return emptyList()
        return storage.getWeakQuestions(state.code)
    }

    fun quizHistory(): List<QuizHistoryEntry> = store().history

    fun averageScore(): Int {
        val h = quizHistory()
        if (h.isEmpty()) return 0
        return (h.sumOf { it.pct.toDouble() } / h.size).roundToInt()
    }

    fun passStreak(): Int {
        val state = currentState ?: return 0
        var streak = 0
        for (entry in quizHistory().reversed()) {
            if (entry.pct >= state.passingScorePct) streak++ else break
        }
        return streak
    }

    fun bestScore(): Int = quizHistory().maxOfOrNull { it.pct } ?: 0
    fun questionsSeen(): Int = store().questions.size

    fun countOptions(): List<Int> {
        val total = currentState?.totalQuestions ?: return listOf(10, 25, 50)
        val counts = mutableListOf<Int>()
        for (n in listOf(10, 25, 50, 100)) { if (n <= total) counts.add(n) }
        if (!counts.contains(total)) counts.add(total)
        return counts
    }

    val currentQuestion: QuizQuestion?
        get() = if (currentIndex < questions.size) questions[currentIndex] else null

    val resultPct: Int
        get() = if (questions.isEmpty()) 0 else (correctCount.toDouble() / questions.size * 100).roundToInt()

    val didPass: Boolean
        get() = resultPct >= (currentState?.passingScorePct ?: 100)

    val wrongResults: List<SessionResult>
        get() = sessionResults.filter { !it.correct }

    fun categoryStats(): List<Pair<String, Int>> {
        val cats = mutableMapOf<String, Pair<Int, Int>>() // seen, correct
        for ((_, record) in store().questions) {
            val cat = record.category.ifEmpty { "unknown" }
            val (seen, correct) = cats.getOrDefault(cat, 0 to 0)
            cats[cat] = (seen + record.seen) to (correct + record.seen - record.wrong)
        }
        return cats.map { (cat, pair) ->
            cat to if (pair.first > 0) (pair.second.toDouble() / pair.first * 100).roundToInt() else 0
        }.sortedBy { it.second }
    }

    fun questionMissInfo(questionId: Int): Pair<Int, Int>? {
        val record = store().questions[questionId.toString()] ?: return null
        if (record.wrong <= 0) return null
        return record.wrong to record.seen
    }

    fun t(key: String, vars: Map<String, String> = emptyMap()): String {
        return localizer.t(key, currentLang, vars)
    }

    // Actions
    fun loadStates() {
        val states = api.fetchStates()
        allStates.clear()
        allStates.addAll(states)
        val savedCode = storage.savedStateCode
        if (savedCode != null) {
            val saved = states.find { it.code == savedCode && it.hasQuestions }
            if (saved != null) {
                currentState = saved
                selectedCount = minOf(50, saved.totalQuestions)
                screen = AppScreen.HOME
            }
        }
    }

    fun switchLang(lang: String) {
        currentLang = lang
        storage.savedLanguage = lang
    }

    fun selectState(state: StateInfo) {
        currentState = state
        storage.savedStateCode = state.code
        selectedCount = minOf(50, state.totalQuestions)
        quizMode = QuizMode.RANDOM
        screen = AppScreen.HOME
    }

    fun goStatePicker() { screen = AppScreen.STATE_PICKER }
    fun goHome() { quizMode = QuizMode.RANDOM; screen = AppScreen.HOME }
    fun showStats() { screen = AppScreen.STATS }

    fun startQuiz() {
        val state = currentState ?: return
        val qs = if (quizMode == QuizMode.WEAK) {
            val weak = weakQuestions()
            if (weak.isEmpty()) return
            val count = minOf(selectedCount, weak.size)
            val weakIds = weak.take(count).map { it.id }.toSet()
            val all = api.fetchQuiz(state.code, currentLang, state.totalQuestions)
            all.filter { it.id in weakIds }.shuffled().take(count)
        } else {
            api.fetchQuiz(state.code, currentLang, selectedCount)
        }
        questions.clear()
        questions.addAll(qs)
        currentIndex = 0; correctCount = 0; wrongCount = 0
        sessionResults.clear()
        answered = false; selectedAnswer = null; correctAnswer = null; explanation = null
        screen = AppScreen.QUIZ
    }

    fun selectAnswer(letter: String) {
        if (answered) return
        val q = currentQuestion ?: return
        val state = currentState ?: return
        answered = true
        selectedAnswer = letter

        val response = api.fetchAnswer(q.id, state.code, currentLang) ?: return
        correctAnswer = response.answer
        explanation = response.explanation
        val isCorrect = letter == response.answer
        if (isCorrect) correctCount++ else wrongCount++

        val s = storage.loadStore(state.code)
        val idStr = q.id.toString()
        val record = s.questions.getOrPut(idStr) { QuestionRecord(category = q.category) }
        record.seen++
        if (!isCorrect) record.wrong++
        storage.saveStore(s, state.code)

        sessionResults.add(SessionResult(
            id = q.id, question = q.question,
            yourAnswer = letter, yourAnswerText = q.choices[letter] ?: "",
            correctAnswer = response.answer, correctAnswerText = q.choices[response.answer] ?: "",
            correct = isCorrect, explanation = response.explanation,
        ))
    }

    fun nextQuestion() {
        currentIndex++
        if (currentIndex >= questions.size) {
            finishQuiz()
            return
        }
        answered = false; selectedAnswer = null; correctAnswer = null; explanation = null
    }

    private fun finishQuiz() {
        val state = currentState ?: return
        val s = storage.loadStore(state.code)
        s.history.add(QuizHistoryEntry(
            correct = correctCount, total = questions.size,
            pct = resultPct, mode = quizMode.name.lowercase(),
        ))
        storage.saveStore(s, state.code)
        screen = AppScreen.RESULTS
    }

    fun clearData() {
        val state = currentState ?: return
        storage.clearStore(state.code)
        screen = AppScreen.HOME
    }
}
