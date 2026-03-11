package com.drivers.test.view.screen

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.drivers.test.model.QuizMode
import com.drivers.test.theme.AppTheme
import com.drivers.test.view.components.LanguageBar
import com.drivers.test.view.components.PrimaryButton
import com.drivers.test.view.components.StatItem
import com.drivers.test.viewmodel.QuizViewModel
import kotlin.math.ceil

@Composable
fun HomeScreen(vm: QuizViewModel) {
    val c = AppTheme.colors
    val state = vm.currentState ?: return

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
            .padding(top = 24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        LanguageBar(
            vm.currentLang,
            langs = state.languages.ifEmpty { listOf("en", "ja", "es") },
            langLabels = vm.localizer.langLabels,
        ) { vm.switchLang(it) }

        Spacer(Modifier.height(16.dp))

        Text(
            vm.t("title", mapOf("state" to state.code.uppercase(), "state_name" to state.name)),
            fontSize = 28.sp, fontWeight = FontWeight.Bold, color = c.blue, textAlign = TextAlign.Center,
        )
        Spacer(Modifier.height(8.dp))
        Text(
            vm.t("subtitle", mapOf("state_name" to state.name, "agency" to state.agency)),
            fontSize = 15.sp, color = c.gray, textAlign = TextAlign.Center,
        )
        Spacer(Modifier.height(4.dp))
        val passCount = ceil(state.testQuestionCount * state.passingScorePct / 100.0).toInt()
        Text(
            vm.t("passingScore", mapOf(
                "pass_pct" to "${state.passingScorePct}",
                "pass_count" to "$passCount",
                "test_count" to "${state.testQuestionCount}",
            )),
            fontSize = 13.sp, color = c.gray,
        )

        Spacer(Modifier.height(16.dp))

        // Stats banner
        val history = vm.quizHistory()
        if (history.isNotEmpty()) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(c.card)
                    .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(12.dp))
                    .padding(14.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    StatItem("${history.size}", vm.t("quizzes"))
                    StatItem("${vm.averageScore()}%", vm.t("avgScore"))
                    StatItem("${vm.passStreak()}", vm.t("passStreak"))
                }
                Text(
                    vm.t("viewStats"),
                    fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = c.blue,
                    modifier = Modifier.clickable { vm.showStats() },
                )
            }
            Spacer(Modifier.height(16.dp))
        }

        // Mode selector
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            ModeButton(
                title = vm.t("modeRandom"), desc = vm.t("modeRandomDesc"), icon = "\uD83C\uDFB2",
                isActive = vm.quizMode == QuizMode.RANDOM,
                modifier = Modifier.weight(1f),
            ) { vm.quizMode = QuizMode.RANDOM }

            ModeButton(
                title = vm.t("modeWeak"), desc = vm.t("modeWeakDesc"), icon = "\uD83C\uDFAF",
                isActive = vm.quizMode == QuizMode.WEAK,
                badgeCount = vm.weakQuestions().size,
                modifier = Modifier.weight(1f),
            ) { vm.quizMode = QuizMode.WEAK }
        }

        Spacer(Modifier.height(16.dp))

        Text(vm.t("numQuestions"), fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(8.dp))

        // Count selector
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            vm.countOptions().forEach { count ->
                val isAll = count == state.totalQuestions
                val isSelected = vm.selectedCount == count
                Text(
                    text = if (isAll) "All" else "$count",
                    fontSize = 16.sp, fontWeight = FontWeight.SemiBold,
                    color = if (isSelected) Color.White else c.blue,
                    modifier = Modifier
                        .clip(RoundedCornerShape(12.dp))
                        .background(if (isSelected) c.blue else c.card)
                        .border(2.dp, c.blue, RoundedCornerShape(12.dp))
                        .clickable { vm.selectedCount = count }
                        .padding(horizontal = 20.dp, vertical = 10.dp),
                )
            }
        }

        Spacer(Modifier.height(20.dp))

        val weakEmpty = vm.quizMode == QuizMode.WEAK && vm.weakQuestions().isEmpty()
        PrimaryButton(
            text = if (weakEmpty) vm.t("noWeakSpots") else vm.t("startQuiz"),
            enabled = !weakEmpty && !vm.isLoading,
        ) { vm.startQuiz() }

        Spacer(Modifier.height(10.dp))

        Text(
            vm.t("changeState"),
            fontSize = 14.sp, color = c.gray,
            modifier = Modifier.clickable { vm.goStatePicker() }.padding(10.dp),
        )

        if (vm.isLoading) {
            Spacer(Modifier.height(12.dp))
            CircularProgressIndicator()
        }
    }
}

@Composable
private fun ModeButton(
    title: String, desc: String, icon: String,
    isActive: Boolean, badgeCount: Int = 0,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    val c = AppTheme.colors
    Column(
        modifier = modifier
            .clip(RoundedCornerShape(12.dp))
            .background(if (isActive) c.blueLight else c.card)
            .border(2.dp, if (isActive) c.blue else MaterialTheme.colorScheme.outline, RoundedCornerShape(12.dp))
            .clickable(onClick = onClick)
            .padding(12.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(icon, fontSize = 20.sp)
        Spacer(Modifier.height(4.dp))
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(title, fontSize = 14.sp, fontWeight = FontWeight.SemiBold,
                color = if (isActive) c.blue else MaterialTheme.colorScheme.onSurface)
            if (badgeCount > 0) {
                Text(
                    "$badgeCount",
                    fontSize = 11.sp, fontWeight = FontWeight.Bold, color = Color.White,
                    modifier = Modifier
                        .clip(RoundedCornerShape(10.dp))
                        .background(c.red)
                        .padding(horizontal = 6.dp, vertical = 1.dp),
                )
            }
        }
        Text(desc, fontSize = 11.sp, color = if (isActive) c.blue else c.gray)
    }
}
