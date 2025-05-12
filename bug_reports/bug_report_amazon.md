# Analysis of Amazon.com Address Testing Bugs

Based on the trajectory of steps attempting to add a Spanish address to an Amazon checkout process, I've identified several bugs and usability issues:

## Major Issues

### 1. International Address Form Bug (Steps 25-46)
**Type:** Feature Bug  
**Severity:** High  
**Issue:** The agent repeatedly attempted to find manual address entry fields within the "Add a new shipping address" form, but after multiple scrolling actions, the form fields never appeared. The form appeared to be stuck in an infinite "Autofill your current location" state with no way to access manual address fields.

**Expected behavior:** After clicking "Add a new delivery address", the user should see a form with country selector and address input fields to manually enter a Spanish address.
**Actual behavior:** Only an "Autofill" option was shown, with no manual entry fields appearing after multiple scroll attempts and waiting.

### 2. Currency Inconsistency (Steps 21-37)
**Type:** Feature Bug  
**Severity:** Medium  
**Issue:** The checkout page inconsistently displayed the order total in CNY (Chinese Yuan) at step 21 showing "CNY 38.41", then later switched to USD at step 23 showing "USD 5.23".

**Expected behavior:** Currency should remain consistent throughout the checkout process unless explicitly changed by the user.
**Actual behavior:** Currency changed from CNY to USD without user action.

### 3. Address Form Loading Issue (Steps 40-42)
**Type:** Feature Bug/Visual Glitch  
**Severity:** Medium  
**Issue:** At step 40, when attempting to add a new address, a loading spinner appeared but the form never fully loaded with the expected fields even after waiting.

**Expected behavior:** The address entry form should load within a reasonable time, showing all required fields.
**Actual behavior:** Form remained in a loading state with only the autofill option visible.

## Minor Issues

### 4. Address Change Navigation Loop (Steps 33-39)
**Type:** User Experience Bug  
**Severity:** Medium  
**Issue:** When attempting to change the delivery address, clicking "Change" and then "Add a new delivery address" led to circular navigation with no clear path to add an international address.

**Expected behavior:** Clicking "Add a new delivery address" should immediately take the user to a form with country selection options.
**Actual behavior:** The user gets stuck in a loop, repeatedly seeing the same address selection screen or loading indicators.

### 5. Autofill Modal Persistence (Steps 41-46)
**Type:** Visual Glitch  
**Severity:** Medium  
**Issue:** The "Autofill your current location" modal appeared to be difficult to dismiss and kept reappearing or staying on screen after multiple attempts to close it.

**Expected behavior:** The modal should close when the user clicks the close button.
**Actual behavior:** The modal persisted across multiple steps and close attempts.

## Recurring Patterns

1. **International Address Support Lacking:** The main recurring issue is Amazon's apparent inability to provide a clear path for adding international addresses during checkout.

2. **Modal Dismissal Problems:** Multiple attempts to dismiss modals and popups were unsuccessful, suggesting UI interaction issues.

3. **Circular Navigation:** The agent got caught in a loop of clicking "Add address" → seeing a loading screen or autofill option → going back → trying again.

## Recommendations

1. **Fix International Address Form:** Ensure the "Add a new delivery address" flow includes a country selector as the first step, followed by appropriate address fields that match the selected country's format.

2. **Consistent Currency Display:** Maintain consistent currency display throughout checkout until explicitly changed by the user.

3. **Improve Form Loading States:** Add timeout handling and better error feedback when address forms fail to load completely.

4. **Enhance Modal Interactions:** Ensure that modal dismissal works reliably and that clicking outside a modal or on close buttons properly removes the modal.

5. **Simplify Address Addition Flow:** Streamline the process of adding new addresses, particularly international ones, by reducing the number of steps and providing clear guidance.

6. **Test Cross-Country Scenarios:** Implement more thorough testing of checkout flows when shipping to countries other than the user's current location.

The most critical issue is the inability to add a Spanish address at all, which represents a fundamental feature failure for an international e-commerce platform. This suggests Amazon may have limitations with their international shipping address handling or UI issues specific to adding addresses from certain countries.