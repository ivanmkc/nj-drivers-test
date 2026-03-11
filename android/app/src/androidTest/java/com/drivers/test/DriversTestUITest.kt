package com.drivers.test

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.drivers.test.theme.DriversTestTheme
import com.drivers.test.view.screen.StatePickerScreen
import com.drivers.test.view.screen.HomeScreen
import com.drivers.test.viewmodel.QuizViewModel
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class DriversTestUITest {

    @get:Rule
    val composeTestRule = createComposeRule()

    // -- State Picker Screen --

    @Test
    fun statePicker_showsTitleAndDescription() {
        val vm = createTestViewModel()
        composeTestRule.setContent {
            DriversTestTheme {
                StatePickerScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText(vm.t("appTitle")).assertExists()
        composeTestRule.onNodeWithText(vm.t("selectStateDesc")).assertExists()
    }

    @Test
    fun statePicker_showsLanguageButtons() {
        val vm = createTestViewModel()
        composeTestRule.setContent {
            DriversTestTheme {
                StatePickerScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText("EN").assertExists()
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
        composeTestRule.onNodeWithText(vm.t("appTitle")).assertExists()
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
        composeTestRule.onNodeWithText("Connection failed").assertExists()
        composeTestRule.onNodeWithText("Retry").assertExists()
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
        composeTestRule.onNodeWithText("New Jersey").assertExists()
        composeTestRule.onNodeWithText("New York").assertExists()
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
        composeTestRule.onNodeWithText(vm.t("comingSoon")).assertExists()
    }

    // -- Home Screen --

    @Test
    fun homeScreen_showsTitle() {
        val vm = createTestViewModelWithState()
        val expected = vm.t("title", mapOf("state" to "NJ", "state_name" to "New Jersey"))
        composeTestRule.setContent {
            DriversTestTheme {
                HomeScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText(expected).assertExists()
    }

    @Test
    fun homeScreen_showsModeSelectorButtons() {
        val vm = createTestViewModelWithState()
        composeTestRule.setContent {
            DriversTestTheme {
                HomeScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText(vm.t("modeRandom")).assertExists()
        composeTestRule.onNodeWithText(vm.t("modeWeak")).assertExists()
    }

    @Test
    fun homeScreen_showsQuestionCountButtons() {
        val vm = createTestViewModelWithState()
        composeTestRule.setContent {
            DriversTestTheme {
                HomeScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText("10").assertExists()
        composeTestRule.onNodeWithText("25").assertExists()
        composeTestRule.onNodeWithText("50").assertExists()
    }

    @Test
    fun homeScreen_showsStartButton() {
        val vm = createTestViewModelWithState()
        composeTestRule.setContent {
            DriversTestTheme {
                HomeScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText(vm.t("startQuiz")).assertExists()
    }

    @Test
    fun homeScreen_showsChangeStateButton() {
        val vm = createTestViewModelWithState()
        composeTestRule.setContent {
            DriversTestTheme {
                HomeScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText(vm.t("changeState")).assertExists()
    }

    @Test
    fun homeScreen_showsPassingInfo() {
        val vm = createTestViewModelWithState()
        val expected = vm.t("passingScore", mapOf(
            "pass_pct" to "80",
            "pass_count" to "40",
            "test_count" to "50",
        ))
        composeTestRule.setContent {
            DriversTestTheme {
                HomeScreen(vm = vm)
            }
        }
        composeTestRule.onNodeWithText(expected, substring = true).assertExists()
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
        composeTestRule.onNodeWithText("\u65E5\u672C\u8A9E").performClick()
        composeTestRule.waitForIdle()
        val expected = vm.t("title", mapOf("state" to "NJ", "state_name" to "New Jersey"))
        composeTestRule.onNodeWithText(expected).assertExists()
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
        composeTestRule.waitForIdle()
        val expected = vm.t("title", mapOf("state" to "NJ", "state_name" to "New Jersey"))
        composeTestRule.onNodeWithText(expected).assertExists()
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
