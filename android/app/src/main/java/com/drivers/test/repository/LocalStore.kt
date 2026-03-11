package com.drivers.test.repository

import android.content.Context
import android.content.SharedPreferences
import com.drivers.test.model.QuestionRecord
import com.drivers.test.model.QuizStore
import com.drivers.test.model.WeakQuestion
import com.google.gson.Gson

class LocalStore(context: Context) {
    private val prefs: SharedPreferences =
        context.getSharedPreferences("drivers_test", Context.MODE_PRIVATE)
    private val gson = Gson()

    fun loadStore(stateCode: String): QuizStore {
        val json = prefs.getString("quiz_$stateCode", null) ?: return QuizStore()
        return try {
            gson.fromJson(json, QuizStore::class.java) ?: QuizStore()
        } catch (_: Exception) {
            QuizStore()
        }
    }

    fun saveStore(store: QuizStore, stateCode: String) {
        prefs.edit().putString("quiz_$stateCode", gson.toJson(store)).apply()
    }

    fun clearStore(stateCode: String) {
        prefs.edit().remove("quiz_$stateCode").apply()
    }

    var savedStateCode: String?
        get() = prefs.getString("quiz_state", null)
        set(value) = prefs.edit().putString("quiz_state", value).apply()

    var savedLanguage: String
        get() = prefs.getString("quiz_lang", "en") ?: "en"
        set(value) = prefs.edit().putString("quiz_lang", value).apply()

    fun getWeakQuestions(stateCode: String): List<WeakQuestion> {
        val store = loadStore(stateCode)
        return store.questions
            .filter { (_, record) -> record.wrong > 0 && record.seen >= 1 }
            .map { (idStr, record) ->
                WeakQuestion(
                    id = idStr.toIntOrNull() ?: 0,
                    missRate = record.wrong.toDouble() / record.seen,
                    wrong = record.wrong,
                    seen = record.seen,
                    category = record.category,
                )
            }
            .sortedWith(compareByDescending<WeakQuestion> { it.missRate }.thenByDescending { it.wrong })
    }
}
