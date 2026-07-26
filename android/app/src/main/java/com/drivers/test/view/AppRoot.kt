package com.drivers.test.view

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.drivers.test.model.AppScreen
import com.drivers.test.theme.AppTheme
import com.drivers.test.view.screen.HomeScreen
import com.drivers.test.view.screen.QuizScreen
import com.drivers.test.view.screen.ResultsScreen
import com.drivers.test.view.screen.StatePickerScreen
import com.drivers.test.view.screen.StatsScreen
import com.drivers.test.viewmodel.QuizViewModel

@Composable
fun AppRoot(
    modifier: Modifier = Modifier,
    vm: QuizViewModel = viewModel(),
) {
    Box(modifier = modifier) {
        when {
            vm.bundleLoading -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(MaterialTheme.colorScheme.background),
                    contentAlignment = Alignment.Center,
                ) {
                    CircularProgressIndicator(color = AppTheme.colors.blue)
                }
            }
            vm.bundleError != null -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(MaterialTheme.colorScheme.background)
                        .padding(32.dp),
                    contentAlignment = Alignment.Center,
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            "Failed to load questions",
                            fontSize = 18.sp,
                            color = AppTheme.colors.red,
                            textAlign = TextAlign.Center,
                        )
                        Spacer(Modifier.height(8.dp))
                        Text(
                            vm.bundleError ?: "",
                            fontSize = 14.sp,
                            color = AppTheme.colors.gray,
                            textAlign = TextAlign.Center,
                        )
                    }
                }
            }
            else -> when (vm.screen) {
                AppScreen.STATE_PICKER -> StatePickerScreen(vm)
                AppScreen.HOME -> HomeScreen(vm)
                AppScreen.QUIZ -> QuizScreen(vm)
                AppScreen.RESULTS -> ResultsScreen(vm)
                AppScreen.STATS -> StatsScreen(vm)
            }
        }
    }
}
