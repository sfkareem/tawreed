# Tawreed: Enterprise BOQ Slicer - System Design

## 1. Project Context & Vision
*   **App Name:** Tawreed (rebranded from "Slab").
*   **Core Purpose:** An enterprise-grade, fully LLM-driven application that autonomously slices Bill of Quantities (BOQs) into structured Work Packages.
*   **Target Stack:** Tauri (Rust) as the native shell, with a frontend built on Next.js (Static Export), Tailwind CSS, Framer Motion, and SQLite for persistence.

## 2. Architecture & System Initialization
*   **First-Time Run Routine:** On launch, the Rust backend verifies the existence of a `~/.tawreed` directory in the user's home folder.
*   **Folder Structure:** Automatically scaffolds `~/.tawreed/data/` (working files) and `~/.tawreed/logs/` (system logs).
*   **SQLite Database (`~/.tawreed/db/tawreed.db`):**
    *   `settings` table: Stores LLM API key, model ID, and preferred output language (English/Arabic).
    *   `history` table: Logs processed BOQs (Timestamp, Project Name, Packages Generated, Output Path).

## 3. Enterprise UI/UX & Navigation
*   **Design System:** Rebuilding the rudimentary UI with Tailwind CSS and Framer Motion to deliver smooth, high-contrast, professional micro-interactions.
*   **Navigation Routes:**
    *   **Main Screen ([TBD - Pending Name Selection]):** Features a drag-and-drop zone, toggles for Output Language and Export Format, and an animated "Generate" button with clear Loading/Error/Success states.
    *   **History:** A data table fetching from SQLite, displaying past runs with quick-access links to the generated folders.
    *   **Settings / About:** UI for managing LLM keys and viewing system docs.

## 4. Data Processing & Excel Generation
*   **Output Naming Convention:** `[Date]_[ProjectName]_Work_Packages_Tawreed.xlsx`
*   **Calculation Fixes:** Resolving the `#Value` error by enforcing strict numeric cell typing in Rust and utilizing bulletproof Excel formulas for the `Amount` column.
*   **Output Configuration:**
    *   **Language:** Dynamic generation of headers in English or Arabic based on UI toggle.
    *   **Export Architecture:** Capability to export as a single comprehensive workbook (with Master & Cover sheets) OR multiple separate workbooks (one per trade/package).
*   **Enterprise Styling & Print Setup:**
    *   Tables styled using clean ListObjects (e.g., `TableStyleMedium2`).
    *   All sheets programmatically forced to `A4` paper size, `Landscape` orientation, and `Fit to 1 Page Wide` for instant, perfect PDF printing.
