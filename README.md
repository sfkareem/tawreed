# Tawreed — Work Package Extractor

Tawreed is an AI-driven work package extraction application that processes construction Bill of Quantities (BOQ) spreadsheets, categorizes the items, and generates organized supplier packages in a newly reconstructed Excel workbook.

## Prerequisites

Before setting up and running Tawreed, ensure you have the following installed:

- **Rust**: The Rust toolchain is required to build the Tauri backend. You can install it via [rustup](https://rustup.rs/).
- **Node.js**: Node.js (version 18+ recommended) is required for running the Next.js frontend application.
- **npm**: Comes bundled with Node.js.

## Environment Variables

Tawreed can use the following environment variable to pre-populate or supply the API key for external LLM execution:

- `TAWREED_API_KEY`: The API key for your configured LLM provider (e.g. MiniMax, OpenAI, etc.).

## Getting Started

### 1. Install Dependencies

Install the frontend and development dependencies:

```bash
npm install
```

### 2. Run the Development Server

To launch the application in development mode with hot-reloading for both the backend and frontend:

```bash
npm run tauri dev
```

### 3. Build the Application

To build the application for production, run:

```bash
npm run tauri build
```

This will bundle the application and generate production-ready executables for your platform under the `src-tauri/target/release` directory.

## Testing & Verification

To run backend logic tests and verify the extractor core:

1. Navigate to the backend directory:
   ```bash
   cd src-tauri
   ```
2. Generate the test binary:
   ```bash
   node build_test.cjs
   ```
3. Run or compile check the test runner:
   ```bash
   cargo check --bin test_boq
   ```
