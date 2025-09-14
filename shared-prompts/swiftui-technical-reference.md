# SwiftUI Technical Reference

## Modern SwiftUI Features (iOS 16+)

**Navigation Architecture**:
- NavigationStack and NavigationSplitView for sophisticated navigation patterns
- Swift 6 Observation framework (@Observable) replacing @ObservableObject
- Advanced Layout API for complex custom layouts
- Advanced animation APIs including PhaseAnimator and KeyframeAnimator

**Performance Optimization Techniques**:
- Lazy container usage (LazyVStack, LazyHStack) for large data sets
- View identity management and explicit id() usage
- EquatableView for expensive view calculations
- Proper use of @State vs @StateObject vs @ObservedObject

**Custom Component Patterns**:
- ViewModifier creation for reusable styling and behavior
- Custom Layout implementations for complex arrangements
- PreferenceKey usage for child-to-parent communication
- Custom ButtonStyle, ToggleStyle, and other style protocols

## SwiftUI Debugging Techniques

**Performance Debugging**:
- Use `_printChanges()` on Views to track unnecessary rebuilds
- Xcode Preview debugging with `#Preview` and live previews
- Instruments profiling for SwiftUI view performance analysis
- Debug view hierarchy with View Inspector and visual debugging

**State Management Debugging**:
- `print()` statements in computed properties to track recalculations
- Breakpoints in `body` computed property to understand rebuild triggers
- Custom debug modifiers to log state changes and view updates
- Console debugging of @Observable and @State property changes

**Common Debugging Patterns**:
```swift
// Debug view rebuilds
.onAppear { print("View appeared: \(type(of: self))") }
.onChange(of: someValue) { print("Value changed: \($0)") }

// Debug expensive operations
var body: some View {
    let _ = print("Body computed for: \(type(of: self))")
    return content
}
```

## Enhanced State Management Patterns

**Complete Property Wrapper Reference**:
- **@State**: Local mutable state within a single view
- **@StateObject**: Creates and owns ObservableObject instances
- **@ObservedObject**: References external ObservableObject instances
- **@EnvironmentObject**: Dependency injection for shared objects
- **@Environment**: Access system and custom environment values
- **@Binding**: Two-way connection to external state
- **@FocusState**: Manage keyboard focus and first responder status
- **@AppStorage**: UserDefaults integration with automatic updates
- **@SceneStorage**: Per-scene state preservation and restoration
- **@Observable**: Swift 6 modern observable pattern replacement for ObservableObject

**State Management Best Practices**:
```swift
// Use @State for simple local state
@State private var isExpanded = false

// Use @Observable for modern shared state
@Observable
class UserSettings {
    var theme: Theme = .light
    var notifications: Bool = true
}

// Use @Environment for dependency injection
@Environment(\.userSettings) var userSettings

// Use @Binding for child component state
struct ToggleRow: View {
    @Binding var isOn: Bool
    let title: String
}
```

## Common SwiftUI Solutions

**Keyboard Handling**:
```swift
// Dismiss keyboard on tap
.onTapGesture {
    UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil)
}

// Adjust for keyboard
.keyboardAdaptive()
```

**Sheet and Modal Presentation**:
```swift
// Modern sheet presentation
.sheet(isPresented: $showingSheet) {
    DetailView()
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
}

// Alert with custom actions
.alert("Confirmation", isPresented: $showingAlert) {
    Button("Delete", role: .destructive) { deleteAction() }
    Button("Cancel", role: .cancel) { }
}
```

**Safe Area and Layout Handling**:
```swift
// Ignore safe area selectively
.ignoresSafeArea(.container, edges: .top)

// Custom safe area handling
.safeAreaInset(edge: .bottom) {
    CustomToolbar()
}

// GeometryReader for custom layouts
GeometryReader { geometry in
    content
        .frame(width: geometry.size.width * 0.8)
}
```

**List and ScrollView Optimizations**:
```swift
// Lazy loading for performance
LazyVStack(spacing: 0) {
    ForEach(items) { item in
        ItemRow(item: item)
            .id(item.id) // Explicit identity
    }
}
.scrollTargetLayout() // iOS 17+ scroll targeting

// Custom scroll behavior
ScrollView {
    LazyVStack {
        content
    }
}
.scrollTargetBehavior(.viewAligned)
.scrollPosition(id: $scrollPosition)
```

## Animation and Interaction Patterns

**Advanced Animations**:
```swift
// Keyframe animations
KeyframeAnimator(initialValue: 0.0) { value in
    content
        .scaleEffect(value)
} keyframes: { _ in
    KeyframeTrack(\.scaleEffect) {
        CubicKeyframe(1.2, duration: 0.3)
        CubicKeyframe(1.0, duration: 0.2)
    }
}

// Phase animations
PhaseAnimator([0, 1, 0]) { phase in
    content
        .opacity(phase == 1 ? 1.0 : 0.5)
} animation: { phase in
    .easeInOut(duration: 0.5)
}
```

**Gesture Handling**:
```swift
// Complex gesture combinations
.gesture(
    DragGesture()
        .simultaneously(with: MagnificationGesture())
        .onChanged { value in
            // Handle combined gesture
        }
)

// Custom gesture modifiers
.onTapGesture(count: 2) { /* double tap */ }
.onLongPressGesture { /* long press */ }
```

## Performance Optimization Strategies

**View Efficiency**:
- Use `EquatableView` wrapper for expensive computations
- Implement proper `Equatable` conformance for custom types
- Minimize `body` recomputation through effective state management
- Use `@ViewBuilder` functions to extract reusable view logic

**Memory Management**:
- Proper lifecycle management for `@StateObject` instances
- Avoid retain cycles in closures and delegate patterns
- Use weak references appropriately in observable patterns
- Profile memory usage with Instruments

**Rendering Optimization**:
- Leverage view identity stability with explicit `id()` modifiers
- Use appropriate container types (LazyVStack vs VStack)
- Minimize view hierarchy depth and complexity
- Cache expensive computed properties when appropriate