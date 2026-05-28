use serde::{Serialize, Deserialize};
use std::fs::{self, File};
use std::io::{self, Write};
use std::path::PathBuf;

#[derive(Serialize, Deserialize, Debug, Clone)]
#[serde(default)]
pub struct AppSettings {
    pub api_provider: String,
    pub base_url: String,
    pub api_key: String,
    pub model_name: String,
    pub preferred_language: String,
    pub theme: String,
    pub api_timeout_seconds: u64,
}

impl Default for AppSettings {
    fn default() -> Self {
        Self {
            api_provider: "gemini".to_string(),
            base_url: "https://generativelanguage.googleapis.com".to_string(),
            api_key: "".to_string(),
            model_name: "gemini-2.0-flash".to_string(),
            preferred_language: "bilingual".to_string(),
            theme: "system".to_string(),
            api_timeout_seconds: 900,
        }
    }
}

pub struct ConfigManager;

impl ConfigManager {
    pub fn config_dir() -> PathBuf {
        let home = std::env::var("USERPROFILE")
            .or_else(|_| std::env::var("HOME"))
            .unwrap_or_else(|_| ".".to_string());
        PathBuf::from(home).join(".tawreed")
    }

    pub fn config_file() -> PathBuf {
        Self::config_dir().join("config.json")
    }

    pub fn logs_dir() -> PathBuf {
        Self::config_dir().join("logs")
    }

    pub fn load_settings() -> io::Result<AppSettings> {
        let path = Self::config_file();
        if !path.exists() {
            let default_settings = AppSettings::default();
            Self::save_settings(&default_settings)?;
            return Ok(default_settings);
        }
        let file = File::open(path)?;
        let reader = io::BufReader::new(file);
        let settings: AppSettings = serde_json::from_reader(reader)
            .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))?;
        Ok(settings)
    }

    pub fn save_settings(settings: &AppSettings) -> io::Result<()> {
        let dir = Self::config_dir();
        fs::create_dir_all(&dir)?;
        let mut temp = tempfile::NamedTempFile::new_in(&dir)?;
        let bytes = serde_json::to_vec_pretty(settings)
            .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))?;
        temp.write_all(&bytes)?;
        temp.flush()?;
        temp.persist(&Self::config_file())
            .map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_app_settings_default() {
        let settings = AppSettings::default();
        assert_eq!(settings.api_provider, "gemini");
        assert_eq!(settings.theme, "system");
    }
}
