package com.drivers.test.view.screen

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.drivers.test.model.SessionResult
import com.drivers.test.theme.AppTheme
import com.drivers.test.view.components.PrimaryButton
import com.drivers.test.view.components.SecondaryButton
import com.drivers.test.viewmodel.QuizViewModel

@Composable
fun ResultsScreen(vm: QuizViewModel) {
    val c = AppTheme.colors
    val state = vm.currentState ?: return

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Spacer(Modifier.height(24.dp))

        // Score circle
        Box(
            modifier = Modifier
                .size(160.dp)
                .border(6.dp, if (vm.didPass) c.green else c.red, CircleShape),
            contentAlignment = Alignment.Center,
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    "${vm.resultPct}%",
                    fontSize = 42.sp,
                    fontWeight = FontWeight.Bold,
                    color = if (vm.didPass) c.green else c.red,
                )
                Text(
                    if (vm.didPass) vm.t("pass") else vm.t("fail"),
                    fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = if (vm.didPass) c.green else c.red,
                )
            }
        }

        Spacer(Modifier.height(24.dp))

        Text(
            if (vm.didPass) vm.t("congratulations") else vm.t("keepPracticing"),
            fontSize = 22.sp,
            fontWeight = FontWeight.Bold,
        )
        Spacer(Modifier.height(8.dp))
        Text(
            vm.t(
                "resultDetail",
                mapOf(
                    "correct" to "${vm.correctCount}",
                    "total" to "${vm.questions.size}",
                    "pass_pct" to "${state.passingScorePct}",
                    "agency" to state.agency,
                ),
            ),
            fontSize = 15.sp,
            color = c.gray,
            textAlign = TextAlign.Center,
            lineHeight = 22.sp,
        )

        Spacer(Modifier.height(24.dp))

        PrimaryButton(vm.t("newQuiz")) { vm.goHome() }
        Spacer(Modifier.height(10.dp))
        SecondaryButton(vm.t("viewStats")) { vm.showStats() }

        Spacer(Modifier.height(24.dp))

        // Review section
        if (vm.wrongResults.isNotEmpty()) {
            Text(
                vm.t("reviewMissed", mapOf("count" to "${vm.wrongResults.size}")),
                fontSize = 18.sp,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.fillMaxWidth(),
            )
            Spacer(Modifier.height(12.dp))
            vm.wrongResults.forEach { result ->
                ReviewItem(result, vm)
                Spacer(Modifier.height(10.dp))
            }
        } else {
            Text(vm.t("perfectScore"), fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(8.dp))
            Text(vm.t("perfectMsg"), fontSize = 15.sp, color = c.gray)
        }
    }
}

@Composable
private fun ReviewItem(
    result: SessionResult,
    vm: QuizViewModel,
) {
    val c = AppTheme.colors
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(c.card),
    ) {
        Box(modifier = Modifier.width(4.dp).fillMaxHeight().background(c.red))
        Column(modifier = Modifier.padding(14.dp)) {
            Text(result.question, fontSize = 14.sp, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(6.dp))
            Text(
                "${vm.t("yourAnswer")}: ${result.yourAnswer}: ${result.yourAnswerText}",
                fontSize = 13.sp,
                color = c.gray,
            )
            Text(
                "${vm.t("correct")}: ${result.correctAnswer}: ${result.correctAnswerText}",
                fontSize = 13.sp,
                color = c.gray,
            )
            Spacer(Modifier.height(6.dp))
            Text(result.explanation, fontSize = 13.sp, color = c.gray, fontStyle = FontStyle.Italic)
        }
    }
}
