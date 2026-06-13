"""Settings page: provider switcher + API key + model + base URL.

The provider dropdown drives the model list and the base-URL field:
- OpenAI, Google, Claude: base URL is pre-filled but editable
- OpenAI-Compatible: base URL is required and starts empty

Connection test runs in a background thread via asyncio.to_thread so
the UI doesn't freeze. Saved settings are validated by core.db before
they hit disk.
"""
import asyncio

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QMessageBox,
)
from PySide6.QtCore import Qt

from core import db
from core.ai import (
    get_provider_names,
    get_provider_config,
    is_valid_provider,
)
from gui.worker import check_connection


class SettingsPage(QWidget):
    """Full settings UI: provider, model, base URL, API key, test, save."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._loading = False  # guards against signal loops while populating UI
        self._build_ui()
        self._load_settings()

    # ----- UI construction ------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        title = QLabel("Settings")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        intro = QLabel(
            "Configure the LLM provider used to categorize BOQ items. "
            "Switching providers automatically updates the model list and base URL."
        )
        intro.setObjectName("sectionLabel")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.provider_combo = QComboBox()
        for name in get_provider_names():
            cfg = get_provider_config(name)
            self.provider_combo.addItem(cfg.get("label", name), userData=name)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        form.addRow("Provider:", self.provider_combo)

        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)  # user can type a custom model
        form.addRow("Model:", self.model_combo)

        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("https://...")
        form.addRow("Base URL:", self.base_url_input)

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Paste your API key (stored locally only)")
        form.addRow("API Key:", self.api_key_input)

        layout.addLayout(form)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)

        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self._test_connection)

        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("primaryBtn")
        self.save_btn.clicked.connect(self._save_settings)

        button_row.addWidget(self.test_btn)
        button_row.addStretch()
        button_row.addWidget(self.save_btn)
        layout.addLayout(button_row)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        layout.addStretch(1)

    # ----- Loading / saving -----------------------------------------------

    def _load_settings(self) -> None:
        settings = db.get_settings()
        self._loading = True
        try:
            provider = settings.get("provider", "OpenAI")
            if not is_valid_provider(provider):
                provider = "OpenAI"
            idx = self.provider_combo.findData(provider)
            if idx < 0:
                idx = 0
            self.provider_combo.setCurrentIndex(idx)
            # _on_provider_changed will populate the model combo; we then
            # override it with the saved value if the saved model is custom
            # or no longer in the provider's known list.
            self._populate_models_for_provider(provider, select_model=settings.get("model", ""))
            self.base_url_input.setText(settings.get("base_url", ""))
            self.api_key_input.setText(settings.get("api_key", ""))
        finally:
            self._loading = False

    def _save_settings(self) -> None:
        provider = self.provider_combo.currentData() or "OpenAI"
        model = self.model_combo.currentText().strip()
        base_url = self.base_url_input.text().strip()
        api_key = self.api_key_input.text().strip()

        cfg = get_provider_config(provider)
        if cfg.get("requires_base_url") and not base_url:
            QMessageBox.warning(
                self,
                "Base URL required",
                f"The '{cfg.get('label', provider)}' provider requires a Base URL.",
            )
            return
        if not api_key:
            QMessageBox.warning(self, "API key required", "Please enter an API key.")
            return
        if not model:
            QMessageBox.warning(self, "Model required", "Please select or type a model name.")
            return

        payload = {
            "provider": provider,
            "api_key": api_key,
            "model": model,
            "base_url": base_url,
        }
        try:
            db.save_settings(payload)
        except Exception as e:
            QMessageBox.critical(self, "Save failed", f"Could not save settings:\n{e}")
            return
        self.status_label.setText("✓ Settings saved.")

    # ----- Provider / model wiring ----------------------------------------

    def _on_provider_changed(self, _index: int) -> None:
        if self._loading:
            return
        provider = self.provider_combo.currentData() or "OpenAI"
        self._populate_models_for_provider(provider, select_model="")
        cfg = get_provider_config(provider)
        if cfg.get("base_url"):
            self.base_url_input.setText(cfg["base_url"])
        self.base_url_input.setPlaceholderText(
            "https://..." if cfg.get("requires_base_url") else cfg.get("base_url", "")
        )
        self.status_label.setText("")

    def _populate_models_for_provider(self, provider: str, select_model: str = "") -> None:
        cfg = get_provider_config(provider)
        models = list(cfg.get("models", []))
        self.model_combo.blockSignals(True)
        try:
            self.model_combo.clear()
            self.model_combo.addItems(models)
            target = select_model or cfg.get("default_model", "")
            if target:
                idx = self.model_combo.findText(target)
                if idx >= 0:
                    self.model_combo.setCurrentIndex(idx)
                else:
                    # Add as a custom entry on top so the user's saved choice
                    # is preserved even if it's no longer in the curated list.
                    self.model_combo.insertItem(0, target)
                    self.model_combo.setCurrentIndex(0)
        finally:
            self.model_combo.blockSignals(False)

    # ----- Test connection ------------------------------------------------

    def _test_connection(self) -> None:
        provider = self.provider_combo.currentData() or "OpenAI"
        api_key = self.api_key_input.text().strip()
        model = self.model_combo.currentText().strip()
        base_url = self.base_url_input.text().strip()

        cfg = get_provider_config(provider)
        if cfg.get("requires_base_url") and not base_url:
            QMessageBox.warning(
                self, "Base URL required",
                f"Enter a Base URL before testing '{cfg.get('label', provider)}'."
            )
            return
        if not api_key:
            QMessageBox.warning(self, "API key required", "Enter an API key to test the connection.")
            return
        if not model:
            QMessageBox.warning(self, "Model required", "Pick or type a model name first.")
            return

        self.test_btn.setEnabled(False)
        self.test_btn.setText("Testing...")
        self.status_label.setText("Testing connection...")

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        task = loop.create_task(
            asyncio.to_thread(check_connection, api_key, base_url, model)
        )

        def on_done(future):
            self.test_btn.setEnabled(True)
            self.test_btn.setText("Test Connection")
            try:
                success = future.result()
            except Exception as e:
                self.status_label.setText(f"Test error: {e}")
                QMessageBox.critical(self, "Test failed", f"Test error: {e}")
                return
            if success:
                self.status_label.setText("✓ Connection successful.")
                QMessageBox.information(self, "Success", "Connection successful!")
            else:
                self.status_label.setText("✗ Connection failed. Check key, URL, and model.")
                QMessageBox.critical(
                    self, "Connection failed",
                    "Could not reach the API. Verify the key, base URL, and model name."
                )

        task.add_done_callback(on_done)
