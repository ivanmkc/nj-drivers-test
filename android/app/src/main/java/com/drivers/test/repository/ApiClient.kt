package com.drivers.test.repository

import com.drivers.test.model.AnswerResponse
import com.drivers.test.model.QuizResponse
import com.drivers.test.model.StatesResponse
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface ApiClient {

    @GET("api/states")
    suspend fun getStates(): StatesResponse

    @GET("api/quiz/{count}")
    suspend fun getQuiz(
        @Path("count") count: Int,
        @Query("state") state: String,
        @Query("lang") lang: String,
    ): QuizResponse

    @GET("api/answer/{questionId}")
    suspend fun getAnswer(
        @Path("questionId") questionId: Int,
        @Query("state") state: String,
        @Query("lang") lang: String,
    ): AnswerResponse

    companion object {
        // For emulator use 10.0.2.2; for physical device use your machine's IP
        const val BASE_URL = "http://10.0.2.2:8080/"

        fun create(): ApiClient {
            return Retrofit.Builder()
                .baseUrl(BASE_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
                .create(ApiClient::class.java)
        }

        fun signImageUrl(state: String, filename: String): String {
            return "${BASE_URL}signs/$state/$filename"
        }
    }
}
