package com.drivers.test.repository

import android.content.Context
import com.drivers.test.model.AnswerResponse
import com.drivers.test.model.QuizQuestion
import com.drivers.test.model.StateInfo
import com.google.gson.Gson
import com.google.gson.annotations.SerializedName
import java.io.ByteArrayOutputStream
import java.util.zip.GZIPInputStream

private data class QuestionBundle(
    val states: List<StateInfo>,
    val questions: Map<String, Map<String, List<BundledQuestion>>>,
)

private data class BundledQuestion(
    val id: Int,
    val category: String,
    val question: String,
    val choices: Map<String, String>,
    val answer: String,
    val explanation: String,
    val image: String? = null,
)

class ApiClient(context: Context) {
    private var bundle: QuestionBundle? = null

    init {
        loadBundle(context)
    }

    private fun loadBundle(context: Context) {
        try {
            val input = context.assets.open("questions_bundle.json.gz")
            val gzip = GZIPInputStream(input)
            val out = ByteArrayOutputStream()
            gzip.copyTo(out)
            gzip.close()
            bundle = Gson().fromJson(out.toString(Charsets.UTF_8.name()), QuestionBundle::class.java)
        } catch (e: Exception) {
            android.util.Log.e("ApiClient", "Failed to load bundle", e)
        }
    }

    fun fetchStates(): List<StateInfo> = bundle?.states ?: emptyList()

    fun fetchQuiz(state: String, lang: String, count: Int): List<QuizQuestion> {
        val stateQuestions = bundle?.questions?.get(state) ?: return emptyList()
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

    fun fetchAnswer(questionId: Int, state: String, lang: String): AnswerResponse? {
        val stateQuestions = bundle?.questions?.get(state) ?: return null
        val langQuestions = stateQuestions[lang] ?: stateQuestions["en"] ?: return null
        val q = langQuestions.find { it.id == questionId } ?: return null
        return AnswerResponse(id = q.id, answer = q.answer, explanation = q.explanation)
    }

    fun signImageName(filename: String): String = "signs/$filename"
}
