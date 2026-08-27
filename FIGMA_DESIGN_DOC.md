# LoveMatch — Figma Frontend Design Document

This document outlines the UI/UX design requirements, color palettes, typography, and screen specifications for designing the **LoveMatch** dating platform frontend in Figma.

## 🎨 1. Brand Identity & Design System

### 1.1 Color Palette
- **Primary Brand Color (Passion & Love):** `#ff6b8a` (Soft Vibrant Pink)
- **Secondary Brand Color (Trust & Playfulness):** `#6c5ce7` (Vibrant Purple)
- **Background (Dark Mode First):** `#1a1a2e` (Deep Navy/Indigo Dark)
- **Card Backgrounds / Elevated Surfaces:** `#24243e` or `rgba(255, 255, 255, 0.03)` with slight white borders.
- **Success/Compatibility Highlights:** `#06d6a0` (Mint Green)
- **Warning/Reporting:** `#ffd166` (Yellow)
- **Danger/Block:** `#ef476f` (Red)

### 1.2 Typography
- **Headings & Display Text:** `Playfair Display` (Serif) – Adds elegance, romance, and an editorial feel to names and major titles.
- **Body & UI Elements:** `Inter` or `Poppins` (Sans-Serif) – Clean, highly readable, modern for chat bubbles, bio text, and navigation.

### 1.3 UI Elements & Styling
- **Cards & Buttons:** Pill-shaped buttons (radius `50px`), rounded cards (radius `16px` to `24px`).
- **Gradients:** Linear gradients combining the primary and secondary colors (e.g., `linear-gradient(135deg, #ff6b8a, #6c5ce7)`) for primary call-to-action (CTA) buttons, match celebrations, and progress bars.
- **Glassmorphism:** Use slight backdrop blurs (`backdrop-filter: blur(10px)`) and semi-transparent backgrounds for modals and floating nav bars to give a modern, premium feel.

---

## 📱 2. Core Screens to Design

### 2.1 Onboarding & Authentication
- **Splash Screen:** Animated logo with the gradient background.
- **Login/Signup:** Minimalist form with Social Login buttons (Google, Apple).
- **Profile Setup Wizard (Gamified):**
  - Step 1: Basic Info & Name.
  - Step 2: Zodiac & Location.
  - Step 3: Interest Tag Picker (Pill chips).
  - Step 4: Photo Gallery Upload (Grid of 6 slots, drag-and-drop).

### 2.2 Dashboard / Home
- **Welcome Header:** Greeting, profile miniature, and notification bell.
- **Profile Strength Meter:** Visual progress bar (0-100%) with a tip to improve.
- **Quick Actions:** "Edit Profile", "Safety Settings", "Go to Swipe Deck".
- **Pending Date Proposals:** Horizontal scrolling list of incoming dates.

### 2.3 Discovery & Swipe Deck (The Core)
- **Main Swipe Card:** 
  - Large full-screen or prominent card with the primary photo.
  - Gradient overlay at the bottom for text readability.
  - Name, Age, Distance, and Zodiac sign overlaid.
- **Card Details (Expanded View):**
  - Scrolling view revealing bio, interest tags (styled as chips), and prompt cards.
  - 5-Axis Compatibility Radar Chart prominently displayed.
- **Floating Action Buttons (FABs):**
  - Rewind (Yellow), Pass (Red cross), Superlike (Blue star), Like (Green/Pink heart).
- **Match Celebration Modal:**
  - Full-screen overlay, confetti animation, "It's a Match!" text, avatars of both users merging. "Send a Message" or "Keep Swiping" buttons.

### 2.4 Real-Time Chat & AI Spark
- **Inbox List:**
  - Search bar.
  - Row items: Avatar, Name, snippet of last message, unread badge, online indicator dot.
- **Conversation Screen:**
  - Top bar: Avatar, Name, "Propose Date" button, "Shield/Report" icon.
  - Chat bubbles: iMessage style. Sender (Gradient), Receiver (Dark grey).
  - Typing indicator animation (3 bouncing dots).
  - **AI Spark Integration:** A sparkly floating button next to the text input. Tapping it shows a bottom sheet with 3 AI-generated icebreakers.

### 2.5 Profile & Gamification
- **Public Profile View (How others see you):**
  - Grid or carousel of 6 photos.
  - Prompt Cards (e.g., "Two truths and a lie...").
- **Edit Profile:**
  - Photo grid with "X" to delete and "+" to add.
  - Inline editing for bio and prompts.
  - Incognito/Ghost mode toggle switch.

### 2.6 Trust & Safety
- **Report Modal:**
  - Radio buttons for reasons (Harassment, Fake Profile, Spam, etc.).
  - Text area for details.
- **Blocked Users List:**
  - Simple list with "Unblock" buttons.

---

## 🛠 3. Interactions & Animations to Prototype in Figma

1. **Card Swiping:** Drag interaction left/right with rotational physics. Overlay a "NOPE" or "LIKE" stamp dynamically based on drag direction.
2. **Match Reveal:** Scale-in animation of the match modal with confetti assets.
3. **AI Spark Generation:** Shimmer effect on the text box when the AI button is clicked, followed by the appearance of the 3 suggestions.
4. **Radar Chart Hover/Tap:** Tapping the radar chart highlights specific compatibility traits.

---

## 📁 4. Asset Export Requirements
- **Icons:** Export as SVG (using Bootstrap Icons or Phosphor Icons as a base).
- **Illustrations:** Any empty state illustrations (e.g., "No matches yet") should be exported as SVG.
- **Logo:** High-res SVG with gradient applied.
