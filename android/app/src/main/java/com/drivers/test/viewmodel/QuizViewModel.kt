package com.drivers.test.viewmodel

import android.app.Application
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.drivers.test.model.AppScreen
import com.drivers.test.model.QuestionRecord
import com.drivers.test.model.QuizHistoryEntry
import com.drivers.test.model.QuizMode
import com.drivers.test.model.QuizQuestion
import com.drivers.test.model.QuizStore
import com.drivers.test.model.SessionResult
import com.drivers.test.model.StateInfo
import com.drivers.test.model.WeakQuestion
import com.drivers.test.repository.ApiClient
import com.drivers.test.repository.LocalStore
import com.drivers.test.repository.Localizer
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlin.math.roundToInt

class QuizViewModel(application: Application) : AndroidViewModel(application) {
    companion object {
        private const val DEFAULT_QUESTION_COUNT = 50
        private val QUESTION_COUNT_OPTIONS = listOf(10, 25, 50, 100)
    }

    private val api = ApiClient()
    private val storage = LocalStore(application)
    val localizer = Localizer()

    var bundleLoading by mutableStateOf(true)
        private set
    var bundleError by mutableStateOf<String?>(null)
        private set

    var screen by mutableStateOf(AppScreen.STATE_PICKER)
    var allStates = mutableStateListOf<StateInfo>()
    var currentState by mutableStateOf<StateInfo?>(null)
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
    var evidence by mutableStateOf<List<String>?>(null)
        private set
    var sessionResults = mutableStateListOf<SessionResult>()

    // Settings
    var quizMode by mutableStateOf(QuizMode.RANDOM)
    var selectedCount by mutableIntStateOf(DEFAULT_QUESTION_COUNT)

    init {
        viewModelScope.launch {
            try {
                withContext(Dispatchers.IO) {
                    api.loadBundle(application)
                }
                bundleLoading = false
                loadStates()
            } catch (e: Exception) {
                bundleLoading = false
                bundleError = e.message ?: "Failed to load question data"
            }
        }
    }

    // Derived state helpers
    private var cachedStore: QuizStore? = null
    private var cachedStoreCode: String? = null

    private fun store(): QuizStore {
        val state = currentState ?: return QuizStore()
        if (cachedStoreCode == state.code) {
            cachedStore?.let { return it }
        }
        val loaded = storage.loadStore(state.code)
        cachedStore = loaded
        cachedStoreCode = state.code
        return loaded
    }

    private fun invalidateStoreCache() {
        cachedStore = null
        cachedStoreCode = null
        cachedWeakQuestions = null
    }

    private fun updateStoreCache(store: QuizStore) {
        cachedStore = store
        cachedWeakQuestions = null
    }

    private var cachedWeakQuestions: List<WeakQuestion>? = null

    fun weakQuestions(): List<WeakQuestion> {
        cachedWeakQuestions?.let { return it }
        val state = currentState ?: return emptyList()
        val result = storage.getWeakQuestions(state.code)
        cachedWeakQuestions = result
        return result
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
        val total = currentState?.totalQuestions
            ?: return QUESTION_COUNT_OPTIONS.filter { it <= DEFAULT_QUESTION_COUNT }
        val counts = mutableListOf<Int>()
        for (n in QUESTION_COUNT_OPTIONS) {
            if (n <= total) counts.add(n)
        }
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

    fun t(
        key: String,
        vars: Map<String, String> = emptyMap(),
    ): String {
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
                selectedCount = minOf(DEFAULT_QUESTION_COUNT, saved.totalQuestions)
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
        invalidateStoreCache()
        storage.savedStateCode = state.code
        selectedCount = minOf(DEFAULT_QUESTION_COUNT, state.totalQuestions)
        quizMode = QuizMode.RANDOM
        screen = AppScreen.HOME
    }

    fun goStatePicker() {
        screen = AppScreen.STATE_PICKER
    }

    fun goHome() {
        quizMode = QuizMode.RANDOM
        screen = AppScreen.HOME
    }

    fun showStats() {
        screen = AppScreen.STATS
    }

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
        currentIndex = 0
        correctCount = 0
        wrongCount = 0
        sessionResults.clear()
        answered = false
        selectedAnswer = null
        correctAnswer = null
        explanation = null
        evidence = null
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
        evidence = api.fetchEvidence(q.id, state.code)
        val isCorrect = letter == response.answer
        if (isCorrect) correctCount++ else wrongCount++

        val s = store()
        val idStr = q.id.toString()
        val record = s.questions[idStr] ?: QuestionRecord(category = q.category)
        val updatedRecord = record.copy(
            seen = record.seen + 1,
            wrong = if (!isCorrect) record.wrong + 1 else record.wrong,
        )
        val updatedStore = s.copy(questions = s.questions + (idStr to updatedRecord))
        storage.saveStore(updatedStore, state.code)
        updateStoreCache(updatedStore)

        sessionResults.add(
            SessionResult(
                id = q.id,
                question = q.question,
                yourAnswer = letter,
                yourAnswerText = q.choices[letter] ?: "",
                correctAnswer = response.answer,
                correctAnswerText = q.choices[response.answer] ?: "",
                correct = isCorrect,
                explanation = response.explanation,
            ),
        )
    }

    fun nextQuestion() {
        currentIndex++
        if (currentIndex >= questions.size) {
            finishQuiz()
            return
        }
        answered = false
        selectedAnswer = null
        correctAnswer = null
        explanation = null
        evidence = null
    }

    private fun finishQuiz() {
        val state = currentState ?: return
        val s = store()
        val updatedStore = s.copy(
            history = s.history + QuizHistoryEntry(
                correct = correctCount,
                total = questions.size,
                pct = resultPct,
                mode = quizMode.name.lowercase(),
            ),
        )
        storage.saveStore(updatedStore, state.code)
        updateStoreCache(updatedStore)
        screen = AppScreen.RESULTS
    }

    fun clearData() {
        val state = currentState ?: return
        storage.clearStore(state.code)
        invalidateStoreCache()
        screen = AppScreen.HOME
    }
}
