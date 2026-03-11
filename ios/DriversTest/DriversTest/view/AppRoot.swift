import SwiftUI

struct AppRoot: View {
    @StateObject private var vm = QuizViewModel()
    @ObservedObject private var localizer = Localizer.shared

    var body: some View {
        Group {
            switch vm.screen {
            case .statePicker:
                StatePickerScreen(vm: vm, localizer: localizer)
            case .home:
                HomeScreen(vm: vm, localizer: localizer)
            case .quiz:
                QuizScreen(vm: vm, localizer: localizer)
            case .results:
                ResultsScreen(vm: vm, localizer: localizer)
            case .stats:
                StatsScreen(vm: vm, localizer: localizer)
            }
        }
        .task {
            await vm.loadStates()
        }
    }
}
