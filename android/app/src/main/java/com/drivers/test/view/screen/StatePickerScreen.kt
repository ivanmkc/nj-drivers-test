package com.drivers.test.view.screen

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.drivers.test.model.StateInfo
import com.drivers.test.theme.AppTheme
import com.drivers.test.view.components.LanguageBar
import com.drivers.test.viewmodel.QuizViewModel

@Composable
fun StatePickerScreen(vm: QuizViewModel) {
    val c = AppTheme.colors
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
            .padding(top = 40.dp),
    ) {
        LanguageBar(vm.currentLang, langLabels = vm.localizer.langLabels) { vm.switchLang(it) }

        Spacer(Modifier.height(16.dp))

        Text(
            vm.t("appTitle"),
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = c.blue,
            modifier = Modifier.fillMaxWidth(),
            textAlign = TextAlign.Center,
        )
        Spacer(Modifier.height(4.dp))
        Text(
            vm.t("selectStateDesc"),
            fontSize = 15.sp,
            color = c.gray,
            modifier = Modifier.fillMaxWidth(),
            textAlign = TextAlign.Center,
        )
        Spacer(Modifier.height(24.dp))

        vm.allStates.forEach { state ->
            StateCard(state, vm)
            Spacer(Modifier.height(10.dp))
        }
    }
}

@Composable
private fun StateCard(
    state: StateInfo,
    vm: QuizViewModel,
) {
    val c = AppTheme.colors

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(c.card)
            .border(2.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(12.dp))
            .alpha(if (state.hasQuestions) 1f else 0.5f)
            .clickable(enabled = state.hasQuestions) { vm.selectState(state) }
            .padding(16.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(state.name, fontSize = 17.sp, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(2.dp))
            Text(
                "${state.agency} \u00B7 " + vm.t(
                    "passingScore",
                    mapOf(
                        "pass_pct" to "${state.passingScorePct}",
                        "pass_count" to "${state.passCount}",
                        "test_count" to "${state.testQuestionCount}",
                    ),
                ),
                fontSize = 13.sp,
                color = c.gray,
            )
        }
        if (state.hasQuestions) {
            Text(
                vm.t("questionsAvailable", mapOf("count" to "${state.totalQuestions}")),
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                color = c.blue,
            )
        } else {
            Text(
                vm.t("comingSoon"),
                fontSize = 11.sp,
                color = c.gray,
                modifier = Modifier
                    .clip(RoundedCornerShape(10.dp))
                    .background(c.grayLight)
                    .padding(horizontal = 8.dp, vertical = 2.dp),
            )
        }
    }
}
