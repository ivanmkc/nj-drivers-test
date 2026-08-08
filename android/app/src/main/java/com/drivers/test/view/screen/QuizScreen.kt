package com.drivers.test.view.screen

import android.graphics.BitmapFactory
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.drivers.test.theme.AppTheme
import com.drivers.test.view.components.PrimaryButton
import com.drivers.test.viewmodel.QuizViewModel
import kotlinx.coroutines.launch
import kotlin.math.roundToInt

@Composable
fun QuizScreen(vm: QuizViewModel) {
    BackHandler { vm.goHome() }

    val c = AppTheme.colors
    val scrollState = rememberScrollState()
    val scope = rememberCoroutineScope()
    val q = vm.currentQuestion ?: return

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .verticalScroll(scrollState)
            .padding(16.dp),
    ) {
        // Progress bar
        val progress = if (vm.questions.isEmpty()) 0f else vm.currentIndex.toFloat() / vm.questions.size
        Box(
            modifier = Modifier.fillMaxWidth().height(6.dp)
                .clip(RoundedCornerShape(3.dp)).background(MaterialTheme.colorScheme.outline),
        ) {
            Box(
                modifier = Modifier.fillMaxHeight().fillMaxWidth(progress)
                    .clip(RoundedCornerShape(3.dp)).background(c.blue),
            )
        }

        Spacer(Modifier.height(12.dp))

        // Header
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(
                "${vm.currentIndex + 1} / ${vm.questions.size}",
                fontSize = 14.sp,
                color = c.gray,
                style = TextStyle(fontFeatureSettings = "tnum"),
            )
            Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(
                    "${vm.correctCount}",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = c.green,
                    style = TextStyle(fontFeatureSettings = "tnum"),
                )
                Text("/", fontSize = 14.sp, color = c.gray)
                Text(
                    "${vm.wrongCount}",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = c.red,
                    style = TextStyle(fontFeatureSettings = "tnum"),
                )
            }
        }

        Spacer(Modifier.height(12.dp))

        // Category + miss badge
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(
                q.category.replace("_", " ").uppercase(),
                fontSize = 12.sp,
                fontWeight = FontWeight.SemiBold,
                color = c.blue,
                modifier = Modifier.clip(RoundedCornerShape(20.dp)).background(c.blueLight)
                    .padding(horizontal = 10.dp, vertical = 4.dp),
            )
            vm.questionMissInfo(q.id)?.let { (wrong, seen) ->
                Text(
                    "${vm.t("missed")} ${(wrong.toDouble() / seen * 100).roundToInt()}%",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = c.red,
                    style = TextStyle(fontFeatureSettings = "tnum"),
                    modifier = Modifier.clip(RoundedCornerShape(20.dp)).background(c.redLight)
                        .padding(horizontal = 10.dp, vertical = 4.dp),
                )
            }
        }

        Spacer(Modifier.height(12.dp))

        // Question text
        Text(q.question, fontSize = 18.sp, fontWeight = FontWeight.SemiBold, lineHeight = 26.sp)

        // Question image
        q.image?.let { imageName ->
            val context = LocalContext.current
            val assetPath = "signs/$imageName"
            val bitmap = remember(assetPath) {
                try {
                    context.assets.open(assetPath).use { BitmapFactory.decodeStream(it) }
                } catch (e: Exception) {
                    null
                }
            }
            bitmap?.let {
                Spacer(Modifier.height(12.dp))
                Image(
                    bitmap = it.asImageBitmap(),
                    contentDescription = "Road sign",
                    contentScale = ContentScale.Fit,
                    modifier = Modifier
                        .fillMaxWidth().heightIn(max = 240.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(8.dp)),
                )
            }
        }

        Spacer(Modifier.height(20.dp))

        // Choices
        q.sortedChoiceKeys.forEach { letter ->
            val choiceText = q.choices[letter] ?: return@forEach
            val state = choiceState(letter, vm.answered, vm.selectedAnswer, vm.correctAnswer)
            ChoiceButton(letter, choiceText, state) { vm.selectAnswer(letter) }
            Spacer(Modifier.height(10.dp))
        }

        // Explanation
        vm.explanation?.let { exp ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(IntrinsicSize.Min)
                    .clip(RoundedCornerShape(topEnd = 12.dp, bottomEnd = 12.dp))
                    .background(c.blueLight),
            ) {
                Box(modifier = Modifier.width(4.dp).fillMaxHeight().background(c.blue))
                Text(
                    exp,
                    fontSize = 14.sp,
                    lineHeight = 22.sp,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f),
                    modifier = Modifier.padding(12.dp),
                )
            }
            Spacer(Modifier.height(8.dp))
        }

        // Evidence from the manual
        vm.evidence?.let { evidence ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(IntrinsicSize.Min)
                    .clip(RoundedCornerShape(topEnd = 12.dp, bottomEnd = 12.dp))
                    .background(c.grayLight),
            ) {
                Box(modifier = Modifier.width(4.dp).fillMaxHeight().background(c.gray))
                Column(modifier = Modifier.padding(12.dp)) {
                    Text(
                        vm.t("fromManual"),
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = c.gray,
                    )
                    Spacer(Modifier.height(4.dp))
                    evidence.forEach { quote ->
                        Text(
                            "“$quote”",
                            fontSize = 13.sp,
                            lineHeight = 20.sp,
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f),
                        )
                    }
                    vm.currentState?.source?.let { src ->
                        Spacer(Modifier.height(4.dp))
                        Text(
                            "— $src",
                            fontSize = 11.sp,
                            color = c.gray,
                        )
                    }
                }
            }
            Spacer(Modifier.height(16.dp))
        }

        if (vm.explanation == null && vm.evidence == null && vm.answered) {
            Spacer(Modifier.height(16.dp))
        }

        // Next button
        if (vm.answered) {
            val isLast = vm.currentIndex >= vm.questions.size - 1
            PrimaryButton(
                text = if (isLast) vm.t("seeResults") else vm.t("next"),
            ) {
                vm.nextQuestion()
                scope.launch { scrollState.animateScrollTo(0) }
            }
        }
    }
}

private data class ChoiceColors(val bg: Color, val border: Color, val letterBg: Color, val letterFg: Color)

private enum class ChoiceState { NORMAL, CORRECT, WRONG, DISABLED }

private fun choiceState(
    letter: String,
    answered: Boolean,
    selected: String?,
    correct: String?,
): ChoiceState {
    if (!answered) return ChoiceState.NORMAL
    if (letter == correct) return ChoiceState.CORRECT
    if (letter == selected && letter != correct) return ChoiceState.WRONG
    return ChoiceState.DISABLED
}

@Composable
private fun ChoiceButton(
    letter: String,
    text: String,
    state: ChoiceState,
    onClick: () -> Unit,
) {
    val c = AppTheme.colors
    val (bg, borderColor, letterBg, letterFg) = when (state) {
        ChoiceState.NORMAL -> ChoiceColors(c.card, MaterialTheme.colorScheme.outline, c.grayLight, c.gray)
        ChoiceState.CORRECT -> ChoiceColors(c.greenLight, c.green, c.green, Color.White)
        ChoiceState.WRONG -> ChoiceColors(c.redLight, c.red, c.red, Color.White)
        ChoiceState.DISABLED -> ChoiceColors(c.card, MaterialTheme.colorScheme.outline, c.grayLight, c.gray)
    }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(bg)
            .border(2.dp, borderColor, RoundedCornerShape(12.dp))
            .alpha(if (state == ChoiceState.DISABLED) 0.7f else 1f)
            .clickable(enabled = state == ChoiceState.NORMAL, onClick = onClick)
            .padding(14.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Box(
            modifier = Modifier
                .size(28.dp)
                .clip(CircleShape)
                .background(letterBg),
            contentAlignment = Alignment.Center,
        ) {
            when (state) {
                ChoiceState.CORRECT -> Icon(
                    Icons.Filled.Check,
                    contentDescription = null,
                    tint = Color.White,
                    modifier = Modifier.size(18.dp),
                )
                ChoiceState.WRONG -> Icon(
                    Icons.Filled.Close,
                    contentDescription = null,
                    tint = Color.White,
                    modifier = Modifier.size(18.dp),
                )
                else -> Text(
                    letter,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    color = letterFg,
                )
            }
        }
        Spacer(Modifier.width(12.dp))
        Text(text, fontSize = 16.sp, lineHeight = 22.sp)
    }
}
