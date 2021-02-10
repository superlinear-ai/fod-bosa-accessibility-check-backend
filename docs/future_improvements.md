# Future improvements

Ways to improve the usability of the Accessibility Check Backend

- [ ] **Also check changeable content.** For now the web page to be checked is rendered in the back-end in order to find contrast issues. This means it does not render the page exactly as the user sees it.
  - [ ] It will not see changeable content in there different versions (for example sliders)
  - [ ] different states of the web page (e.g. collapses, extensions, ...)
  - [ ] different screen sizes
    - Possible solution: find the hardcoded breakpoints in the css. Then we can render the web page for these different breakpoints in the back-end.

- [ ] **Handle authentication and cookies.** In the current solution it is impossible to check pages that need authentication to show the relevant content. There is also an issue with the cookies settings overlay that almost all website have.
  - Possible solutions:
    - Take a screenshot from the client side
    - Run the solution completely locally
    - Use an encrypted backend server

- [ ] **Make the solution run faster.** The goal of this project was to test the strength of using AI. The backend has not yet been optimized in terms of speed. The following components are bottlenecks:
  - [ ] We create 2 headless Chrome browsers to take 2 screenshots

Ways to improve checking the contrast of the interactive components:

- [ ] **Check contrast within an interactive component.** For now, we only check the contrast between a component and its background. For some components (e.g. a slider) it is also important to check the contrast within the component, otherwise the user will not be able to see if a slider is turned on or off. 

- [ ] **Better detect interactive components.** Right now, we only detect a simple subset of interactive components (submit and input). But sometimes, interactive components are not made using the standard html elements. These are not detected at the moment.
  - Possible solutions:
    - Train a model to detect interactive components

- [ ] **Take into account the [ACT rules](https://act-rules.github.io/rules/afw4f7).** "This rule checks that the highest possible contrast of every text character with its background meets the minimal contrast requirement." – so we would need to compare the brightest and the darkest colours in the detected boxes, rather than the "most used".
