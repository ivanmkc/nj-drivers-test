package com.drivers.test.model

import com.google.gson.annotations.SerializedName
import kotlin.math.ceil

// API responses

data class StatesResponse(val states: List<StateInfo>)

data class StateInfo(
    val code: String,
    val name: String,
    val agency: String,
    @SerializedName("passing_score_pct") val passingScorePct: Int,
    @SerializedName("test_question_count") val testQuestionCount: Int,
    val languages: List<String>,
    @SerializedName("total_questions") val totalQuestions: Int,
    @SerializedName("has_questions") val hasQuestions: Boolean,
) {
    val passCount: Int get() = ceil(testQuestionCount * passingScorePct / 100.0).toInt()
}

data class QuizResponse(val questions: List<QuizQuestion>, val total: Int)

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
    var seen: Int = 0,
    var wrong: Int = 0,
    var category: String = "",
)

data class QuizHistoryEntry(
    val date: Long = System.currentTimeMillis(),
    val correct: Int,
    val total: Int,
    val pct: Int,
    val mode: String,
)

data class QuizStore(
    var history: MutableList<QuizHistoryEntry> = mutableListOf(),
    var questions: MutableMap<String, QuestionRecord> = mutableMapOf(),
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
