package com.drivers.test.ui.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// From shared/theme.json
val Blue = Color(0xFF1A56DB)
val BlueLight = Color(0xFFE8F0FE)
val Green = Color(0xFF16A34A)
val GreenLight = Color(0xFFDCFCE7)
val Red = Color(0xFFDC2626)
val RedLight = Color(0xFFFEE2E2)
val Orange = Color(0xFFEA580C)
val Gray = Color(0xFF6B7280)
val GrayLight = Color(0xFFF3F4F6)
val TextPrimary = Color(0xFF111827)

// Dark mode variants
val BlueDark = Color(0xFF5B8DEF)
val BlueLightDark = Color(0xFF1E293B)
val GreenDark = Color(0xFF4ADE80)
val GreenLightDark = Color(0xFF14332A)
val RedDark = Color(0xFFFCA5A5)
val RedLightDark = Color(0xFF3B1515)
val OrangeDark = Color(0xFFFB923C)
val GrayDark = Color(0xFF9CA3AF)
val GrayLightDark = Color(0xFF1F2937)
val TextPrimaryDark = Color(0xFFF9FAFB)
val SurfaceDark = Color(0xFF111827)
val CardDark = Color(0xFF1F2937)

private val LightColorScheme = lightColorScheme(
    primary = Blue,
    onPrimary = Color.White,
    primaryContainer = BlueLight,
    secondary = Green,
    error = Red,
    errorContainer = RedLight,
    background = GrayLight,
    surface = Color.White,
    onBackground = TextPrimary,
    onSurface = TextPrimary,
    outline = Color(0xFFE5E7EB),
)

private val DarkColorScheme = darkColorScheme(
    primary = BlueDark,
    onPrimary = Color.White,
    primaryContainer = BlueLightDark,
    secondary = GreenDark,
    error = RedDark,
    errorContainer = RedLightDark,
    background = SurfaceDark,
    surface = CardDark,
    onBackground = TextPrimaryDark,
    onSurface = TextPrimaryDark,
    outline = Color(0xFF374151),
)

// Custom colors accessible outside Material theme
data class AppColors(
    val blue: Color,
    val blueLight: Color,
    val green: Color,
    val greenLight: Color,
    val red: Color,
    val redLight: Color,
    val orange: Color,
    val gray: Color,
    val grayLight: Color,
    val card: Color,
)

val LightAppColors = AppColors(
    blue = Blue, blueLight = BlueLight,
    green = Green, greenLight = GreenLight,
    red = Red, redLight = RedLight,
    orange = Orange, gray = Gray, grayLight = GrayLight,
    card = Color.White,
)

val DarkAppColors = AppColors(
    blue = BlueDark, blueLight = BlueLightDark,
    green = GreenDark, greenLight = GreenLightDark,
    red = RedDark, redLight = RedLightDark,
    orange = OrangeDark, gray = GrayDark, grayLight = GrayLightDark,
    card = CardDark,
)

object AppTheme {
    var colors: AppColors = LightAppColors
        private set

    fun update(isDark: Boolean) {
        colors = if (isDark) DarkAppColors else LightAppColors
    }
}

@Composable
fun DriversTestTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    AppTheme.update(darkTheme)

    MaterialTheme(
        colorScheme = colorScheme,
        content = content,
    )
}
