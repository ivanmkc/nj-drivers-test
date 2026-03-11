package com.drivers.test.data

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface ApiService {

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

        fun create(): ApiService {
            return Retrofit.Builder()
                .baseUrl(BASE_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
                .create(ApiService::class.java)
        }

        fun signImageUrl(state: String, filename: String): String {
            return "${BASE_URL}signs/$state/$filename"
        }
    }
}
