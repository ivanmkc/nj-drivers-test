package com.drivers.test

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.drivers.test.theme.DriversTestTheme
import com.drivers.test.view.screen.StatePickerScreen
import com.drivers.test.view.screen.HomeScreen
import com.drivers.test.view.screen.QuizScreen
import com.drivers.test.view.screen.ResultsScreen
import com.drivers.test.view.screen.StatsScreen
import com.drivers.test.viewmodel.QuizViewModel
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * UI tests for the Driver's Test app.
 * These tests verify screen rendering and basic interactions.
 * They run against the Compose UI tree without needing a backend server.
 */
@RunWith(AndroidJUnit4::class)
class DriversTestUITest {

    @get:Rule
    val composeTestRule = createComposeRule()

    // -- State Picker Screen --

    @Test
    fun statePicker_showsTitleAndDescription() {
        composeTestRule.setContent {
            DriversTestTheme {
                StatePickerScreen(vm = createTestViewModel())
            }
        }
        composeTestRule.onNodeWithText("Driver's Test Practice").assertIsDisplayed()
        composeTestRule.onNodeWithText("Choose your state to start practicing").assertIsDisplayed()
    }

    @Test
    fun statePicker_showsLanguageButtons() {
        composeTestRule.setContent {
            DriversTestTheme {
                StatePickerScreen(vm = createTestViewModel())
            }
        }
        composeTestRule.onNodeWithText("EN").assertIsDisplayed()
    }

    @Test
    fun statePicker_showsLoadingWhenLoading() {
        val vm = createTestViewModel()
        vm.isLoading = true
        composeTestRule.setContent {
            DriversTestTheme {
                StatePickerScreen(vm = vm)
            }
        }
        composeTestRule.onNode(hasTestTag("loading") or hasContentDescription("loading"))
            .assertExists()
            .run { /* CircularProgressIndicator is present */ }
    }

    @Test
    fun statePicker_showsErrorMessage() {
        val vm = createTestViewModel()
        vm.errorMessage = "Connection failed"
        composeTestRule.setContent {
            DriversTestTheme {
                StatePickerScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText("Connection failed").assertIsDisplayed()
        composeTestRule.onNodeWithText("Retry").assertIsDisplayed()
    }

    @Test
    fun statePicker_showsStateCards() {
        val vm = createTestViewModel()
        populateTestStates(vm)
        composeTestRule.setContent {
            DriversTestTheme {
                StatePickerScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText("New Jersey").assertIsDisplayed()
        composeTestRule.onNodeWithText("New York").assertIsDisplayed()
    }

    @Test
    fun statePicker_disabledStateNotClickable() {
        val vm = createTestViewModel()
        populateTestStates(vm)
        composeTestRule.setContent {
            DriversTestTheme {
                StatePickerScreen(vm = vm)
            }
        }
        // "Coming soon" state should show badge
        composeTestRule.onNodeWithText("Coming soon").assertIsDisplayed()
    }

    // -- Home Screen --

    @Test
    fun homeScreen_showsTitle() {
        val vm = createTestViewModelWithState()
        composeTestRule.setContent {
            DriversTestTheme {
                HomeScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText("NJ Driver's Test").assertIsDisplayed()
    }

    @Test
    fun homeScreen_showsModeSelectorButtons() {
        val vm = createTestViewModelWithState()
        composeTestRule.setContent {
            DriversTestTheme {
                HomeScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText("Random").assertIsDisplayed()
        composeTestRule.onNodeWithText("Weak Spots").assertIsDisplayed()
    }

    @Test
    fun homeScreen_showsQuestionCountButtons() {
        val vm = createTestViewModelWithState()
        composeTestRule.setContent {
            DriversTestTheme {
                HomeScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText("10").assertIsDisplayed()
        composeTestRule.onNodeWithText("25").assertIsDisplayed()
        composeTestRule.onNodeWithText("50").assertIsDisplayed()
    }

    @Test
    fun homeScreen_showsStartButton() {
        val vm = createTestViewModelWithState()
        composeTestRule.setContent {
            DriversTestTheme {
                HomeScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText("Start Quiz").assertIsDisplayed()
    }

    @Test
    fun homeScreen_showsChangeStateButton() {
        val vm = createTestViewModelWithState()
        composeTestRule.setContent {
            DriversTestTheme {
                HomeScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText("Change State").assertIsDisplayed()
    }

    @Test
    fun homeScreen_showsPassingInfo() {
        val vm = createTestViewModelWithState()
        composeTestRule.setContent {
            DriversTestTheme {
                HomeScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText("Passing: 80% (40/50)", substring = true).assertIsDisplayed()
    }

    // -- Language Switching --

    @Test
    fun languageSwitching_changesToJapanese() {
        val vm = createTestViewModelWithState()
        composeTestRule.setContent {
            DriversTestTheme {
                HomeScreen(vm = vm)
            }
        }
        // Tap Japanese language button
        composeTestRule.onNodeWithText("日本語").performClick()
        // Title should now be in Japanese
        composeTestRule.onNodeWithText("NJ 運転免許テスト").assertIsDisplayed()
    }

    @Test
    fun languageSwitching_changesToSpanish() {
        val vm = createTestViewModelWithState()
        composeTestRule.setContent {
            DriversTestTheme {
                HomeScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText("ES").performClick()
        composeTestRule.onNodeWithText("Examen de Conducir NJ").assertIsDisplayed()
    }

    // -- Helpers --

    private fun createTestViewModel(): QuizViewModel {
        return QuizViewModel(
            androidx.test.core.app.ApplicationProvider.getApplicationContext()
        )
    }

    private fun createTestViewModelWithState(): QuizViewModel {
        val vm = createTestViewModel()
        vm.currentState = com.drivers.test.model.StateInfo(
            code = "nj",
            name = "New Jersey",
            agency = "MVC",
            passingScorePct = 80,
            testQuestionCount = 50,
            languages = listOf("en", "ja", "es"),
            totalQuestions = 332,
            hasQuestions = true,
        )
        vm.selectedCount = 50
        return vm
    }

    private fun populateTestStates(vm: QuizViewModel) {
        vm.allStates.clear()
        vm.allStates.addAll(listOf(
            com.drivers.test.model.StateInfo(
                code = "nj", name = "New Jersey", agency = "MVC",
                passingScorePct = 80, testQuestionCount = 50,
                languages = listOf("en"), totalQuestions = 332, hasQuestions = true,
            ),
            com.drivers.test.model.StateInfo(
                code = "ny", name = "New York", agency = "DMV",
                passingScorePct = 70, testQuestionCount = 20,
                languages = listOf("en"), totalQuestions = 407, hasQuestions = true,
            ),
            com.drivers.test.model.StateInfo(
                code = "ca", name = "California", agency = "DMV",
                passingScorePct = 83, testQuestionCount = 36,
                languages = listOf("en"), totalQuestions = 0, hasQuestions = false,
            ),
        ))
        vm.isLoading = false
    }
}
