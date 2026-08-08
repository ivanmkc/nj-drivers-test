package com.drivers.test.repository

import android.content.Context
import com.drivers.test.model.AnswerResponse
import com.drivers.test.model.QuizQuestion
import com.drivers.test.model.StateInfo
import com.drivers.test.model.Verification
import com.google.gson.Gson
import com.google.gson.annotations.SerializedName
import java.io.ByteArrayOutputStream
import java.util.zip.GZIPInputStream

private data class QuestionBundle(
    val states: List<BundledState>,
)

private data class BundledState(
    val code: String,
    val name: String,
    val agency: String,
    @SerializedName("passing_score_pct") val passingScorePct: Int,
    @SerializedName("test_question_count") val testQuestionCount: Int,
    val source: String? = null,
    val categories: Map<String, Int>? = null,
    val verification: Verification? = null,
    val languages: Map<String, List<BundledQuestion>>,
)

private data class BundledQuestion(
    val id: Int,
    val category: String,
    val question: String,
    val choices: Map<String, String>,
    val answer: String,
    val explanation: String,
    val image: String? = null,
    val evidence: List<String>? = null,
)

class ApiClient {
    private var stateInfos: List<StateInfo> = emptyList()
    private var questionsMap: Map<String, Map<String, List<BundledQuestion>>> = emptyMap()
    private var questionIndex: Map<String, Map<String, Map<Int, BundledQuestion>>> = emptyMap()

    fun loadBundle(context: Context) {
        val input = context.assets.open("questions_bundle.json.gz")
        val gzip = GZIPInputStream(input)
        val out = ByteArrayOutputStream()
        gzip.copyTo(out)
        gzip.close()
        val loaded = Gson().fromJson(out.toString(Charsets.UTF_8.name()), QuestionBundle::class.java)

        stateInfos = loaded.states.map { s ->
            val langCodes = s.languages.keys.sorted()
            val totalQs = s.languages["en"]?.size ?: s.languages.values.firstOrNull()?.size ?: 0
            StateInfo(
                code = s.code,
                name = s.name,
                agency = s.agency,
                passingScorePct = s.passingScorePct,
                testQuestionCount = s.testQuestionCount,
                languages = langCodes,
                totalQuestions = totalQs,
                hasQuestions = totalQs > 0,
                source = s.source,
                categories = s.categories,
                verification = s.verification,
            )
        }

        questionsMap = loaded.states.associate { s ->
            s.code to s.languages
        }

        questionIndex = loaded.states.associate { s ->
            s.code to s.languages.mapValues { (_, questions) ->
                questions.associateBy { it.id }
            }
        }
    }

    fun fetchStates(): List<StateInfo> = stateInfos

    fun fetchQuiz(
        state: String,
        lang: String,
        count: Int,
    ): List<QuizQuestion> {
        val stateQuestions = questionsMap[state] ?: return emptyList()
        val langQuestions = stateQuestions[lang] ?: stateQuestions["en"] ?: return emptyList()
        return langQuestions.shuffled().take(count).map { q ->
            QuizQuestion(
                id = q.id,
                category = q.category,
                question = q.question,
                choices = q.choices,
                image = q.image,
            )
        }
    }

    fun fetchAnswer(
        questionId: Int,
        state: String,
        lang: String,
    ): AnswerResponse? {
        val langIndex = questionIndex[state] ?: return null
        val q = (langIndex[lang] ?: langIndex["en"])?.get(questionId) ?: return null
        return AnswerResponse(id = q.id, answer = q.answer, explanation = q.explanation)
    }

    fun fetchEvidence(
        questionId: Int,
        state: String,
    ): List<String>? {
        val enIndex = questionIndex[state]?.get("en") ?: return null
        return enIndex[questionId]?.evidence?.takeIf { it.isNotEmpty() }
    }
}
