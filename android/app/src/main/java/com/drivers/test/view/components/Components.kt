package com.drivers.test.view.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.path
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.drivers.test.theme.AppTheme

@Composable
fun LanguageBar(
    currentLang: String,
    langs: List<String> = listOf("en", "es"),
    langLabels: Map<String, String>,
    officialTestLanguages: List<String>? = null,
    onSwitch: (String) -> Unit,
) {
    val c = AppTheme.colors
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = GlobeVector,
            contentDescription = null,
            tint = c.gray,
            modifier = Modifier.size(20.dp),
        )
        Spacer(Modifier.weight(1f))
        langs.forEach { lang ->
            val isActive = lang == currentLang
            val label = langLabels[lang] ?: lang.uppercase()
            val isOfficial = officialTestLanguages != null &&
                isOfficialLanguage(lang, officialTestLanguages)
            Row(
                modifier = Modifier
                    .padding(horizontal = 2.dp)
                    .defaultMinSize(minHeight = 44.dp)
                    .clip(RoundedCornerShape(20.dp))
                    .background(if (isActive) c.blueLight else c.card)
                    .border(
                        1.5.dp,
                        if (isActive) c.blue else MaterialTheme.colorScheme.outline,
                        RoundedCornerShape(20.dp),
                    )
                    .clickable { onSwitch(lang) }
                    .padding(horizontal = 12.dp, vertical = 6.dp)
                    .let { mod ->
                        if (officialTestLanguages != null) {
                            val desc = if (isOfficial) {
                                "$label, offered on the official test"
                            } else {
                                "$label, practice only"
                            }
                            mod.semantics { contentDescription = desc }
                        } else {
                            mod
                        }
                    },
                verticalAlignment = Alignment.CenterVertically,
            ) {
                if (isOfficial) {
                    Icon(
                        Icons.Filled.Check,
                        contentDescription = null,
                        tint = c.green,
                        modifier = Modifier.size(12.dp),
                    )
                    Spacer(Modifier.width(3.dp))
                }
                Text(
                    text = label,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = if (isActive) c.blue else c.gray,
                )
            }
        }
    }
}

private fun isOfficialLanguage(
    langCode: String,
    officialList: List<String>,
): Boolean {
    val codeToName = mapOf("en" to "english", "es" to "spanish", "ja" to "japanese", "fr" to "french")
    val name = codeToName[langCode] ?: return false
    return officialList.any { it.equals(name, ignoreCase = true) }
}

private val GlobeVector: ImageVector by lazy {
    ImageVector.Builder(
        name = "Globe",
        defaultWidth = 24.dp,
        defaultHeight = 24.dp,
        viewportWidth = 24f,
        viewportHeight = 24f,
    ).apply {
        path(fill = SolidColor(Color.Black)) {
            moveTo(11.99f, 2f)
            curveTo(6.47f, 2f, 2f, 6.48f, 2f, 12f)
            reflectiveCurveToRelative(4.47f, 10f, 9.99f, 10f)
            curveTo(17.52f, 22f, 22f, 17.52f, 22f, 12f)
            reflectiveCurveTo(17.52f, 2f, 11.99f, 2f)
            close()
            moveToRelative(6.93f, 6f)
            horizontalLineToRelative(-2.95f)
            curveToRelative(-0.32f, -1.25f, -0.78f, -2.45f, -1.38f, -3.56f)
            curveToRelative(1.84f, 0.63f, 3.37f, 1.91f, 4.33f, 3.56f)
            close()
            moveTo(12f, 4.04f)
            curveToRelative(0.83f, 1.2f, 1.48f, 2.53f, 1.91f, 3.96f)
            horizontalLineToRelative(-3.82f)
            curveToRelative(0.43f, -1.43f, 1.08f, -2.76f, 1.91f, -3.96f)
            close()
            moveTo(4.26f, 14f)
            curveTo(4.1f, 13.36f, 4f, 12.69f, 4f, 12f)
            reflectiveCurveToRelative(0.1f, -1.36f, 0.26f, -2f)
            horizontalLineToRelative(3.38f)
            curveToRelative(-0.08f, 0.66f, -0.14f, 1.32f, -0.14f, 2f)
            curveToRelative(0f, 0.68f, 0.06f, 1.34f, 0.14f, 2f)
            horizontalLineTo(4.26f)
            close()
            moveToRelative(0.82f, 2f)
            horizontalLineToRelative(2.95f)
            curveToRelative(0.32f, 1.25f, 0.78f, 2.45f, 1.38f, 3.56f)
            curveToRelative(-1.84f, -0.63f, -3.37f, -1.9f, -4.33f, -3.56f)
            close()
            moveToRelative(2.95f, -8f)
            horizontalLineTo(5.08f)
            curveToRelative(0.96f, -1.66f, 2.49f, -2.93f, 4.33f, -3.56f)
            curveTo(8.81f, 5.55f, 8.35f, 6.75f, 8.03f, 8f)
            close()
            moveTo(12f, 19.96f)
            curveToRelative(-0.83f, -1.2f, -1.48f, -2.53f, -1.91f, -3.96f)
            horizontalLineToRelative(3.82f)
            curveToRelative(-0.43f, 1.43f, -1.08f, 2.76f, -1.91f, 3.96f)
            close()
            moveTo(14.34f, 14f)
            horizontalLineTo(9.66f)
            curveToRelative(-0.09f, -0.66f, -0.16f, -1.32f, -0.16f, -2f)
            curveToRelative(0f, -0.68f, 0.07f, -1.35f, 0.16f, -2f)
            horizontalLineToRelative(4.68f)
            curveToRelative(0.09f, 0.65f, 0.16f, 1.32f, 0.16f, 2f)
            curveToRelative(0f, 0.68f, -0.07f, 1.34f, -0.16f, 2f)
            close()
            moveToRelative(0.25f, 5.56f)
            curveToRelative(0.6f, -1.11f, 1.06f, -2.31f, 1.38f, -3.56f)
            horizontalLineToRelative(2.95f)
            curveToRelative(-0.96f, 1.65f, -2.49f, 2.93f, -4.33f, 3.56f)
            close()
            moveTo(16.36f, 14f)
            curveToRelative(0.08f, -0.66f, 0.14f, -1.32f, 0.14f, -2f)
            curveToRelative(0f, -0.68f, -0.06f, -1.34f, -0.14f, -2f)
            horizontalLineToRelative(3.38f)
            curveToRelative(0.16f, 0.64f, 0.26f, 1.31f, 0.26f, 2f)
            reflectiveCurveToRelative(-0.1f, 1.36f, -0.26f, 2f)
            horizontalLineTo(16.36f)
            close()
        }
    }.build()
}

@Composable
fun PrimaryButton(
    text: String,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    onClick: () -> Unit,
) {
    val c = AppTheme.colors
    Box(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(if (enabled) c.blue else c.blue.copy(alpha = 0.5f))
            .clickable(enabled = enabled, onClick = onClick)
            .padding(16.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(text, color = c.onPrimary, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
    }
}

@Composable
fun SecondaryButton(
    text: String,
    onClick: () -> Unit,
) {
    val c = AppTheme.colors
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(c.card)
            .border(2.dp, c.blue, RoundedCornerShape(12.dp))
            .clickable(onClick = onClick)
            .padding(16.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(text, color = c.blue, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
    }
}

@Composable
fun StatItem(
    value: String,
    label: String,
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            value,
            fontSize = 22.sp,
            fontWeight = FontWeight.Bold,
            style = TextStyle(fontFeatureSettings = "tnum"),
        )
        Text(label, fontSize = 11.sp, color = AppTheme.colors.gray, fontWeight = FontWeight.Normal)
    }
}

@Composable
fun StatCard(
    value: String,
    label: String,
    valueColor: Color = MaterialTheme.colorScheme.onSurface,
) {
    val c = AppTheme.colors
    Column(
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .background(c.card)
            .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(12.dp))
            .padding(vertical = 16.dp, horizontal = 12.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            value,
            fontSize = 26.sp,
            fontWeight = FontWeight.Bold,
            color = valueColor,
            style = TextStyle(fontFeatureSettings = "tnum"),
        )
        Spacer(Modifier.height(4.dp))
        Text(label, fontSize = 11.sp, color = c.gray, fontWeight = FontWeight.Normal, textAlign = TextAlign.Center)
    }
}
