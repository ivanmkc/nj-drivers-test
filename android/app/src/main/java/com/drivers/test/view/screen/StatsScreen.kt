package com.drivers.test.view.screen

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.drivers.test.theme.AppTheme
import com.drivers.test.view.components.StatCard
import com.drivers.test.viewmodel.QuizViewModel
import kotlin.math.roundToInt

@Composable
fun StatsScreen(vm: QuizViewModel) {
    val c = AppTheme.colors
    var showResetDialog by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
    ) {
        // Back
        Row(
            modifier = Modifier.clickable { vm.goHome() },
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = null, tint = c.blue, modifier = Modifier.size(18.dp))
            Spacer(Modifier.width(6.dp))
            Text(vm.t("back"), fontSize = 15.sp, fontWeight = FontWeight.SemiBold, color = c.blue)
        }

        Spacer(Modifier.height(20.dp))
        Text(vm.t("yourProgress"), fontSize = 22.sp, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(20.dp))

        // Top stats
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            Box(Modifier.weight(1f)) { StatCard("${vm.quizHistory().size}", vm.t("quizzes"), c.blue) }
            Box(Modifier.weight(1f)) { StatCard("${vm.averageScore()}%", vm.t("avgScore"), c.green) }
            Box(Modifier.weight(1f)) { StatCard("${vm.questionsSeen()}", vm.t("qsSeen")) }
        }
        Spacer(Modifier.height(10.dp))
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            Box(Modifier.weight(1f)) { StatCard("${vm.passStreak()}", vm.t("passStreak"), c.green) }
            Box(Modifier.weight(1f)) { StatCard("${vm.bestScore()}%", vm.t("bestScore")) }
        }

        Spacer(Modifier.height(20.dp))

        // Chart
        Column(
            modifier = Modifier.fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(c.card)
                .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(12.dp))
                .padding(16.dp),
        ) {
            Text(vm.t("scoreHistory"), fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(12.dp))
            val history = vm.quizHistory()
            if (history.size >= 2) {
                ScoreChart(
                    scores = history.takeLast(20).map { it.pct },
                    passingPct = vm.currentState?.passingScorePct ?: 70,
                    startIndex = (history.size - minOf(20, history.size)) + 1,
                    modifier = Modifier.fillMaxWidth().height(180.dp),
                )
            } else {
                Text(
                    if (history.isEmpty()) "Take a quiz to see your progress" else "Take one more quiz to see the chart",
                    fontSize = 14.sp, color = c.gray,
                    modifier = Modifier.fillMaxWidth().height(120.dp).wrapContentSize(),
                )
            }
        }

        Spacer(Modifier.height(20.dp))

        // Category bars
        val cats = vm.categoryStats()
        if (cats.isNotEmpty()) {
            Text(vm.t("accuracyByCategory"), fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(12.dp))
            cats.forEach { (cat, pct) ->
                CategoryBar(cat, pct)
                Spacer(Modifier.height(8.dp))
            }
            Spacer(Modifier.height(16.dp))
        }

        // Weak questions
        val weak = vm.weakQuestions()
        if (weak.isNotEmpty()) {
            Text(vm.t("mostMissed"), fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(12.dp))
            weak.take(15).forEach { w ->
                Row(
                    modifier = Modifier.fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(c.card)
                        .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(12.dp)),
                ) {
                    Box(modifier = Modifier.width(4.dp).fillMaxHeight().background(c.orange))
                    Column(modifier = Modifier.padding(horizontal = 14.dp, vertical = 12.dp)) {
                        Text("Q${w.id}", fontSize = 14.sp, fontWeight = FontWeight.SemiBold)
                        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            Text(vm.t("missed"), fontSize = 12.sp, color = c.gray)
                            Text(
                                "${w.wrong}/${w.seen} (${(w.missRate * 100).roundToInt()}%)",
                                fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = c.red,
                            )
                            Text("\u00B7", color = c.gray)
                            Text(w.category.replace("_", " "), fontSize = 12.sp, color = c.gray)
                        }
                    }
                }
                Spacer(Modifier.height(8.dp))
            }
            Spacer(Modifier.height(16.dp))
        }

        // Reset
        HorizontalDivider()
        Spacer(Modifier.height(20.dp))
        Box(
            modifier = Modifier.fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(c.card)
                .border(2.dp, c.redLight, RoundedCornerShape(12.dp))
                .clickable { showResetDialog = true }
                .padding(12.dp),
            contentAlignment = Alignment.Center,
        ) {
            Text(vm.t("resetAll"), fontSize = 15.sp, fontWeight = FontWeight.SemiBold, color = c.red)
        }
    }

    if (showResetDialog) {
        AlertDialog(
            onDismissRequest = { showResetDialog = false },
            title = { Text("Reset") },
            text = { Text(vm.t("resetConfirm", mapOf("state_name" to (vm.currentState?.name ?: "")))) },
            confirmButton = {
                TextButton(onClick = { showResetDialog = false; vm.clearData() }) { Text("Reset") }
            },
            dismissButton = {
                TextButton(onClick = { showResetDialog = false }) { Text("Cancel") }
            },
        )
    }
}

@Composable
private fun CategoryBar(category: String, pct: Int) {
    val c = AppTheme.colors
    val barColor = when {
        pct >= 80 -> c.green
        pct >= 60 -> c.orange
        else -> c.red
    }
    Row(verticalAlignment = Alignment.CenterVertically) {
        Text(
            category.replace("_", " ").replaceFirstChar { it.uppercase() },
            fontSize = 13.sp, modifier = Modifier.width(110.dp), maxLines = 1,
        )
        Spacer(Modifier.width(10.dp))
        Box(
            modifier = Modifier.weight(1f).height(10.dp)
                .clip(RoundedCornerShape(5.dp)).background(MaterialTheme.colorScheme.outline),
        ) {
            Box(
                modifier = Modifier.fillMaxHeight().fillMaxWidth(pct / 100f)
                    .clip(RoundedCornerShape(5.dp)).background(barColor),
            )
        }
        Spacer(Modifier.width(10.dp))
        Text("$pct%", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = barColor, modifier = Modifier.width(36.dp))
    }
}

@Composable
private fun ScoreChart(scores: List<Int>, passingPct: Int, startIndex: Int, modifier: Modifier) {
    val c = AppTheme.colors
    val textMeasurer = rememberTextMeasurer()

    Canvas(modifier = modifier) {
        val padLeft = 36.dp.toPx()
        val padRight = 16.dp.toPx()
        val padTop = 20.dp.toPx()
        val padBottom = 30.dp.toPx()
        val plotW = size.width - padLeft - padRight
        val plotH = size.height - padTop - padBottom
        val n = scores.size

        // Grid
        for (pct in listOf(0, 25, 50, 75, 100)) {
            val y = padTop + plotH - (pct / 100f) * plotH
            drawLine(Color.LightGray, Offset(padLeft, y), Offset(size.width - padRight, y), 1f)
            drawText(textMeasurer, "$pct%", topLeft = Offset(0f, y - 6.dp.toPx()),
                style = TextStyle(fontSize = 10.sp, color = Color.Gray))
        }

        // Passing line
        val passY = padTop + plotH - (passingPct / 100f) * plotH
        drawLine(
            c.green.copy(alpha = 0.3f), Offset(padLeft, passY), Offset(size.width - padRight, passY),
            strokeWidth = 2f, pathEffect = PathEffect.dashPathEffect(floatArrayOf(12f, 8f)),
        )

        // Points
        val points = scores.mapIndexed { i, pct ->
            val x = padLeft + if (n == 1) plotW / 2 else (i.toFloat() / (n - 1)) * plotW
            val y = padTop + plotH - (pct / 100f) * plotH
            Offset(x, y)
        }

        // Line + fill
        if (points.size >= 2) {
            val linePath = Path().apply {
                moveTo(points[0].x, points[0].y)
                points.drop(1).forEach { lineTo(it.x, it.y) }
            }
            drawPath(linePath, c.blue, style = Stroke(width = 2.5.dp.toPx()))

            val fillPath = Path().apply {
                moveTo(points[0].x, points[0].y)
                points.drop(1).forEach { lineTo(it.x, it.y) }
                lineTo(points.last().x, padTop + plotH)
                lineTo(points.first().x, padTop + plotH)
                close()
            }
            drawPath(fillPath, c.blue.copy(alpha = 0.1f))
        }

        // Dots
        points.forEachIndexed { i, p ->
            val dotColor = if (scores[i] >= passingPct) c.green else c.red
            drawCircle(Color.White, 6.dp.toPx(), p)
            drawCircle(dotColor, 4.dp.toPx(), p)
        }

        // X labels
        val step = if (n <= 10) 1 else 2
        points.forEachIndexed { i, p ->
            if (i % step == 0 || i == n - 1) {
                drawText(textMeasurer, "#${startIndex + i}",
                    topLeft = Offset(p.x - 10.dp.toPx(), size.height - padBottom + 4.dp.toPx()),
                    style = TextStyle(fontSize = 10.sp, color = Color.Gray))
            }
        }
    }
}
