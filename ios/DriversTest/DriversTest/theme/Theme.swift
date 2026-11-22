import SwiftUI

enum AppTheme {
    static let blue = Color("Blue")
    static let blueLight = Color("BlueLight")
    static let green = Color("Green")
    static let successText = Color("SuccessText")
    static let greenLight = Color("GreenLight")
    static let red = Color("Red")
    static let errorText = Color("ErrorText")
    static let redLight = Color("RedLight")
    static let orange = Color("Orange")
    static let gray = Color("Gray")
    static let grayLight = Color("GrayLight")
    static let onPrimary = Color("OnPrimary")

    static let accent = Color("Brass")
    static let navy = Color("Navy")
    static let secondaryText = Color("SecondaryText")
    static func display(_ size: CGFloat, relativeTo style: Font.TextStyle = .title) -> Font {
        .custom("IBMPlexSerif-Medium", size: size, relativeTo: style)
    }
    static func body(_ size: CGFloat, relativeTo style: Font.TextStyle = .body) -> Font {
        .custom("Inter-Regular", size: size, relativeTo: style)
    }

    // Theme-aware surface colors
    static let card = Color(UIColor.secondarySystemGroupedBackground)
    static let border = Color(UIColor.separator)
}
