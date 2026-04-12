package com.drivers.test.view

import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import com.drivers.test.model.AppScreen
import com.drivers.test.view.screen.*
import com.drivers.test.viewmodel.QuizViewModel

@Composable
fun AppRoot(
    modifier: Modifier = Modifier,
    vm: QuizViewModel = viewModel(),
) {
    LaunchedEffect(Unit) {
        vm.loadStates()
    }

    Box(modifier = modifier) {
        when (vm.screen) {
            AppScreen.STATE_PICKER -> StatePickerScreen(vm)
            AppScreen.HOME -> HomeScreen(vm)
            AppScreen.QUIZ -> QuizScreen(vm)
            AppScreen.RESULTS -> ResultsScreen(vm)
            AppScreen.STATS -> StatsScreen(vm)
        }
    }
}
