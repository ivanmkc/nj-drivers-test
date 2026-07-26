package com.drivers.test.view.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
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
import com.drivers.test.theme.AppTheme

@Composable
fun LanguageBar(
    currentLang: String,
    langs: List<String> = listOf("en", "es"),
    langLabels: Map<String, String>,
    onSwitch: (String) -> Unit,
) {
    val c = AppTheme.colors
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.End,
    ) {
        langs.forEach { lang ->
            val isActive = lang == currentLang
            Text(
                text = langLabels[lang] ?: lang.uppercase(),
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                color = if (isActive) c.blue else c.gray,
                modifier = Modifier
                    .padding(horizontal = 2.dp)
                    .clip(RoundedCornerShape(20.dp))
                    .background(if (isActive) c.blueLight else c.card)
                    .border(
                        1.5.dp,
                        if (isActive) c.blue else MaterialTheme.colorScheme.outline,
                        RoundedCornerShape(20.dp),
                    )
                    .clickable { onSwitch(lang) }
                    .padding(horizontal = 12.dp, vertical = 6.dp),
            )
        }
    }
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
        Text(text, color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
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
        Text(value, fontSize = 22.sp, fontWeight = FontWeight.Bold)
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
        Text(value, fontSize = 26.sp, fontWeight = FontWeight.Bold, color = valueColor)
        Spacer(Modifier.height(4.dp))
        Text(label, fontSize = 11.sp, color = c.gray, fontWeight = FontWeight.Normal, textAlign = TextAlign.Center)
    }
}
