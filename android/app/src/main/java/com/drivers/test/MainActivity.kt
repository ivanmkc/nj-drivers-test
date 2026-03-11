package com.drivers.test

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import com.drivers.test.data.AppScreen
import com.drivers.test.ui.screens.*
import com.drivers.test.ui.theme.DriversTestTheme
import com.drivers.test.viewmodel.QuizViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            DriversTestTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    DriversTestApp(modifier = Modifier.padding(innerPadding))
                }
            }
        }
    }
}

@Composable
fun DriversTestApp(modifier: Modifier = Modifier, vm: QuizViewModel = viewModel()) {
    LaunchedEffect(Unit) { vm.loadStates() }

    when (vm.screen) {
        AppScreen.STATE_PICKER -> StatePickerScreen(vm)
        AppScreen.HOME -> HomeScreen(vm)
        AppScreen.QUIZ -> QuizScreen(vm)
        AppScreen.RESULTS -> ResultsScreen(vm)
        AppScreen.STATS -> StatsScreen(vm)
    }
}
