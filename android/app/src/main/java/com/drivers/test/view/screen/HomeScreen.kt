package com.drivers.test.view.screen

import android.content.Intent
import android.net.Uri
import androidx.activity.compose.BackHandler
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.expandVertically
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.drivers.test.model.QuizMode
import com.drivers.test.model.StateInfo
import com.drivers.test.theme.AppTheme
import com.drivers.test.view.components.LanguageBar
import com.drivers.test.view.components.PrimaryButton
import com.drivers.test.view.components.StatItem
import com.drivers.test.viewmodel.QuizViewModel

@Composable
fun HomeScreen(vm: QuizViewModel) {
    BackHandler { vm.goStatePicker() }

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
            langs = state.languages.ifEmpty { listOf("en", "es") },
            langLabels = vm.localizer.langLabels,
            officialTestLanguages = state.officialTestLanguages,
        ) { vm.switchLang(it) }

        state.officialTestLanguages?.let {
            Spacer(Modifier.height(4.dp))
            Text(
                vm.t("officialTestCaption", mapOf("agency" to state.agency)),
                fontSize = 11.sp,
                color = c.gray,
            )
        }

        Spacer(Modifier.height(16.dp))

        Text(
            vm.t("title", mapOf("state" to state.code.uppercase(), "state_name" to state.name)),
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = c.blue,
            textAlign = TextAlign.Center,
        )
        Spacer(Modifier.height(8.dp))
        Text(
            vm.t("subtitle", mapOf("state_name" to state.name, "agency" to state.agency)),
            fontSize = 15.sp,
            color = c.gray,
            textAlign = TextAlign.Center,
        )
        Spacer(Modifier.height(4.dp))
        Text(
            vm.t(
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

        Spacer(Modifier.height(16.dp))

        if (state.source != null || state.verification != null || state.categories != null) {
            AboutThisTestSection(state, vm)
            Spacer(Modifier.height(16.dp))
        }

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
                    fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = c.blue,
                    modifier = Modifier.clickable { vm.showStats() },
                )
            }
            Spacer(Modifier.height(16.dp))
        }

        // Mode selector
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            ModeButton(
                title = vm.t("modeRandom"),
                desc = vm.t("modeRandomDesc"),
                icon = Icons.Filled.Refresh,
                isActive = vm.quizMode == QuizMode.RANDOM,
                modifier = Modifier.weight(1f),
            ) { vm.quizMode = QuizMode.RANDOM }

            ModeButton(
                title = vm.t("modeWeak"),
                desc = vm.t("modeWeakDesc"),
                icon = Icons.Filled.Star,
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
                    text = if (isAll) vm.t("all") else "$count",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = if (isSelected) c.onPrimary else c.blue,
                    style = TextStyle(fontFeatureSettings = "tnum"),
                    modifier = Modifier
                        .defaultMinSize(minHeight = 44.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(if (isSelected) c.blue else c.card)
                        .border(2.dp, c.blue, RoundedCornerShape(12.dp))
                        .clickable { vm.selectedCount = count }
                        .padding(horizontal = 20.dp, vertical = 10.dp)
                        .wrapContentSize(Alignment.Center),
                )
            }
        }

        Spacer(Modifier.height(20.dp))

        val weakEmpty = vm.quizMode == QuizMode.WEAK && vm.weakQuestions().isEmpty()
        PrimaryButton(
            text = if (weakEmpty) vm.t("noWeakSpots") else vm.t("startQuiz"),
            enabled = !weakEmpty,
        ) { vm.startQuiz() }

        Spacer(Modifier.height(10.dp))

        Text(
            vm.t("changeState"),
            fontSize = 14.sp,
            color = c.gray,
            modifier = Modifier.clickable { vm.goStatePicker() }.padding(10.dp),
        )
    }
}

@Composable
private fun AboutThisTestSection(
    state: StateInfo,
    vm: QuizViewModel,
) {
    var expanded by remember { mutableStateOf(false) }
    val c = AppTheme.colors
    val chevronRotation by animateFloatAsState(if (expanded) 180f else 0f, label = "chevron")
    val context = LocalContext.current

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(c.card)
            .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(12.dp)),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { expanded = !expanded }
                .padding(14.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                vm.t("aboutThisTest"),
                fontSize = 15.sp,
                fontWeight = FontWeight.SemiBold,
            )
            Icon(
                Icons.Filled.KeyboardArrowDown,
                contentDescription = if (expanded) "Collapse" else "Expand",
                tint = c.gray,
                modifier = Modifier.size(20.dp).rotate(chevronRotation),
            )
        }

        AnimatedVisibility(
            visible = expanded,
            enter = expandVertically() + fadeIn(),
            exit = shrinkVertically() + fadeOut(),
        ) {
            Column(
                modifier = Modifier.padding(horizontal = 14.dp).padding(bottom = 14.dp),
            ) {
                state.source?.let { src ->
                    val manualUrl = state.verification?.manualUrl
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            "${vm.t("sourceLabel")}: ",
                            fontSize = 13.sp,
                            color = c.gray,
                        )
                        Text(
                            src,
                            fontSize = 13.sp,
                            color = if (manualUrl != null) c.blue else MaterialTheme.colorScheme.onSurface,
                            fontWeight = if (manualUrl != null) FontWeight.SemiBold else FontWeight.Normal,
                            modifier = if (manualUrl != null) {
                                Modifier.clickable {
                                    context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(manualUrl)))
                                }
                            } else {
                                Modifier
                            },
                        )
                    }
                }

                state.verification?.edition?.let { ed ->
                    Spacer(Modifier.height(6.dp))
                    Text(
                        "${vm.t("editionLabel")}: $ed",
                        fontSize = 13.sp,
                        color = c.gray,
                    )
                }

                Spacer(Modifier.height(6.dp))
                val officialLangs = state.officialTestLanguages
                val officialLangsText = if (officialLangs != null) {
                    formatOfficialLanguages(officialLangs, vm.t("officialTestLangsAndOthers"))
                } else {
                    vm.t("officialTestLangsUnknown", mapOf("agency" to state.agency))
                }
                Text(
                    "${vm.t("officialTestLangsLabel")}: $officialLangsText",
                    fontSize = 13.sp,
                    color = c.gray,
                )
                if (state.languages.size > 1) {
                    Spacer(Modifier.height(4.dp))
                    Text(
                        vm.t("officialTestPracticeNote"),
                        fontSize = 12.sp,
                        color = c.gray,
                    )
                }

                state.verification?.let { v ->
                    val hasBadges = v.precisionGrade != null ||
                        v.precisionAvgFidelity != null ||
                        v.recallCoveragePct != null
                    if (hasBadges) {
                        Spacer(Modifier.height(10.dp))
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(6.dp),
                            modifier = Modifier.fillMaxWidth(),
                        ) {
                            v.precisionGrade?.let { grade ->
                                VerificationBadge(
                                    "${vm.t("gradeLabel")} $grade",
                                    c.green,
                                    c.greenLight,
                                )
                            }
                            v.precisionAvgFidelity?.let { fid ->
                                val fidStr = if (fid % 1.0 == 0.0) "${fid.toInt()}" else "%.1f".format(fid)
                                VerificationBadge(
                                    "$fidStr/10 ${vm.t("fidelityLabel")}",
                                    c.green,
                                    c.greenLight,
                                )
                            }
                            v.recallCoveragePct?.let { cov ->
                                val covStr = if (cov % 1.0 == 0.0) "${cov.toInt()}" else "%.1f".format(cov)
                                VerificationBadge(
                                    "$covStr% ${vm.t("coverageLabel")}",
                                    c.green,
                                    c.greenLight,
                                )
                            }
                        }
                    }

                    v.translations?.takeIf { it.isNotEmpty() }?.let { trans ->
                        Spacer(Modifier.height(8.dp))
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            trans.forEach { (lang, verdict) ->
                                val isPassing = verdict == "PASS"
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(2.dp),
                                ) {
                                    Icon(
                                        if (isPassing) Icons.Filled.Check else Icons.Filled.Close,
                                        contentDescription = verdict,
                                        tint = if (isPassing) c.green else c.red,
                                        modifier = Modifier.size(14.dp),
                                    )
                                    Text(
                                        "${lang.uppercase()} ${verdict.lowercase()}",
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        color = if (isPassing) c.green else c.red,
                                    )
                                }
                            }
                        }
                    }
                }

                state.categories?.takeIf { it.isNotEmpty() }?.let { cats ->
                    Spacer(Modifier.height(12.dp))
                    val maxCount = cats.values.maxOrNull() ?: 1
                    cats.entries.sortedByDescending { it.value }.forEach { (cat, count) ->
                        CategoryRow(cat, count, maxCount, vm)
                        Spacer(Modifier.height(4.dp))
                    }
                }
            }
        }
    }
}

@Composable
private fun VerificationBadge(
    text: String,
    fg: Color,
    bg: Color,
) {
    Text(
        text,
        fontSize = 11.sp,
        fontWeight = FontWeight.SemiBold,
        color = fg,
        modifier = Modifier
            .clip(RoundedCornerShape(20.dp))
            .background(bg)
            .padding(horizontal = 8.dp, vertical = 3.dp),
    )
}

@Composable
private fun CategoryRow(
    cat: String,
    count: Int,
    maxCount: Int,
    vm: QuizViewModel,
) {
    val c = AppTheme.colors
    val label = cat.split("_").joinToString(" ") { word ->
        word.replaceFirstChar { it.uppercase() }
    }
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            label,
            fontSize = 12.sp,
            color = c.gray,
            modifier = Modifier.width(130.dp),
        )
        Box(
            modifier = Modifier
                .weight(1f)
                .height(6.dp)
                .clip(RoundedCornerShape(3.dp))
                .background(c.grayLight),
        ) {
            Box(
                modifier = Modifier
                    .fillMaxHeight()
                    .fillMaxWidth(count.toFloat() / maxCount)
                    .clip(RoundedCornerShape(3.dp))
                    .background(c.blue),
            )
        }
        Spacer(Modifier.width(8.dp))
        Text(
            "$count",
            fontSize = 12.sp,
            fontWeight = FontWeight.SemiBold,
            color = c.blue,
            style = TextStyle(fontFeatureSettings = "tnum"),
        )
    }
}

@Composable
private fun ModeButton(
    title: String,
    desc: String,
    icon: ImageVector,
    isActive: Boolean,
    badgeCount: Int = 0,
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
        Icon(
            icon,
            contentDescription = null,
            tint = if (isActive) c.blue else c.gray,
            modifier = Modifier.size(24.dp),
        )
        Spacer(Modifier.height(4.dp))
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(
                title,
                fontSize = 14.sp,
                fontWeight = FontWeight.SemiBold,
                color = if (isActive) c.blue else MaterialTheme.colorScheme.onSurface,
            )
            if (badgeCount > 0) {
                Text(
                    "$badgeCount",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White,
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

private fun formatOfficialLanguages(
    languages: List<String>,
    andOthersText: String,
): String {
    val named = languages.filter { !it.equals("many", ignoreCase = true) }
    val hasMany = languages.any { it.equals("many", ignoreCase = true) }
    return when {
        named.isNotEmpty() && hasMany -> "${named.joinToString(", ")}, $andOthersText"
        named.isNotEmpty() -> named.joinToString(", ")
        hasMany -> andOthersText
        else -> ""
    }
}
