# Implementation Plan: NGO Website Redesign (Inspired by Thaagam.org)

This plan aims to elevate the NavSahaay Foundation website by incorporating high-impact design and transparency features found in top NGO websites like Thaagam.org.

## User Review Required

> [!IMPORTANT]
> - **Specific Impact Items**: We will transition from general causes to specific "Impact Packages" (e.g., "Plant a tree for ₹70").
> - **Trust Signals**: We need to confirm if NavSahaay has 80G certification to highlight it prominently.

## Proposed Changes

### 1. Enhanced UI/UX (Tailwind CSS)

#### [MODIFY] [base.html](file:///Users/apple/AndroidStudioProjects/NavSahaay/app/templates/base.html)
- Add a sticky "Donate Monthly" button in the header.
- Implement a floating "Quick Donate" widget.
- Update footer with trust logos (80G, ISO, etc. - placeholders for now).

#### [MODIFY] [home.html](file:///Users/apple/AndroidStudioProjects/NavSahaay/app/templates/home.html)
- **Hero Redesign**: Focus on urgency and transparency.
- **Impact Ticker**: Add an animated counter for Donors, Funds, and Lives Impacted.
- **Specific Causes/Packages**: Create a grid of specific items people can fund (e.g., Meal for a child, School kit).
- **Recent Activity Feed**: A scrolling section showing "Someone just donated ₹500".
- **Transparency Section**: Highlight the "Photo/Video Proof" promise.

### 2. Functional Improvements

#### [MODIFY] [models/donation.py](file:///Users/apple/AndroidStudioProjects/NavSahaay/app/models/donation.py)
- Add a field for `package_id` or `package_name` to track specific item donations.

#### [MODIFY] [routes/main.py](file:///Users/apple/AndroidStudioProjects/NavSahaay/app/routes/main.py)
- Update the `donate` route to handle specific package selections.

## Verification Plan

### Manual Verification
1. Open the home page and verify the new "Impact Items" grid.
2. Test the specific package donation flow.
3. Verify that the "Live Ticker" correctly reflects data (can be mocked or fetched from Firestore).
4. Check mobile responsiveness for the new complex grid layouts.
