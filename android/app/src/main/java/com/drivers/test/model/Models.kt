package com.drivers.test.model

import com.google.gson.annotations.SerializedName
import kotlin.math.ceil

// API responses

data class Verification(
    @SerializedName("verified_at") val verifiedAt: String? = null,
    val overall: String? = null,
    @SerializedName("manual_url") val manualUrl: String? = null,
    val edition: String? = null,
    @SerializedName("manual_pages") val manualPages: Int? = null,
    @SerializedName("precision_avg_fidelity") val precisionAvgFidelity: Double? = null,
    @SerializedName("precision_grade") val precisionGrade: String? = null,
    @SerializedName("questions_judged") val questionsJudged: Int? = null,
    @SerializedName("recall_coverage_pct") val recallCoveragePct: Double? = null,
    val translations: Map<String, String>? = null,
)

data class StateInfo(
    val code: String,
    val name: String,
    val agency: String,
    val passingScorePct: Int,
    val testQuestionCount: Int,
    val languages: List<String>,
    val totalQuestions: Int,
    val hasQuestions: Boolean,
    val source: String? = null,
    val categories: Map<String, Int>? = null,
    val verification: Verification? = null,
    val officialTestLanguages: List<String>? = null,
) {
    val passCount: Int get() = ceil(testQuestionCount * passingScorePct / 100.0).toInt()
}

data class QuizQuestion(
    val id: Int,
    val category: String,
    val question: String,
    val choices: Map<String, String>,
    val image: String? = null,
) {
    val sortedChoiceKeys: List<String> get() = choices.keys.sorted()
}

data class AnswerResponse(
    val id: Int,
    val answer: String,
    val explanation: String,
)

// Local storage

data class QuestionRecord(
    val seen: Int = 0,
    val wrong: Int = 0,
    val category: String = "",
)

data class QuizHistoryEntry(
    val date: Long = System.currentTimeMillis(),
    val correct: Int,
    val total: Int,
    val pct: Int,
    val mode: String,
)

data class QuizStore(
    val history: List<QuizHistoryEntry> = emptyList(),
    val questions: Map<String, QuestionRecord> = emptyMap(),
)

// Session

data class SessionResult(
    val id: Int,
    val question: String,
    val yourAnswer: String,
    val yourAnswerText: String,
    val correctAnswer: String,
    val correctAnswerText: String,
    val correct: Boolean,
    val explanation: String,
)

data class WeakQuestion(
    val id: Int,
    val missRate: Double,
    val wrong: Int,
    val seen: Int,
    val category: String,
)

enum class QuizMode { RANDOM, WEAK }

enum class AppScreen { STATE_PICKER, HOME, QUIZ, RESULTS, STATS }
