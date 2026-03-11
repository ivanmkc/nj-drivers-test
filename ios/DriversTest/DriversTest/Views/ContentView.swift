import SwiftUI

struct ContentView: View {
    @StateObject private var vm = QuizViewModel()
    @ObservedObject private var localizer = Localizer.shared

    var body: some View {
        Group {
            switch vm.screen {
            case .statePicker:
                StatePickerView(vm: vm, localizer: localizer)
            case .home:
                HomeView(vm: vm, localizer: localizer)
            case .quiz:
                QuizView(vm: vm, localizer: localizer)
            case .results:
                ResultsView(vm: vm, localizer: localizer)
            case .stats:
                StatsView(vm: vm, localizer: localizer)
            }
        }
        .task {
            await vm.loadStates()
        }
    }
}
