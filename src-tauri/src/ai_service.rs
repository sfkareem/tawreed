use crate::config::AppSettings;
use base64::{Engine as _, engine::general_purpose};
use serde_json::Value;

pub struct AIService;

impl AIService {
    pub async fn call_ai(
        settings: &AppSettings,
        prompt: &str,
        text_content: &str,
        image_bytes_list: Option<Vec<Vec<u8>>>,
    ) -> Result<String, String> {
        if settings.api_key.is_empty() {
            return Err("API Key is missing in Settings.".to_string());
        }

        let client = reqwest::Client::builder()
            .timeout(std::time::Duration::from_secs(settings.api_timeout_seconds))
            .build()
            .map_err(|e| format!("Failed to build HTTP client: {}", e))?;

        let full_prompt = format!("{}\n\nDocument Data:\n{}", prompt, text_content);
        let provider = settings.api_provider.to_lowercase();

        if provider == "gemini" {
            let mut parts = vec![serde_json::json!({ "text": full_prompt })];
            if let Some(images) = image_bytes_list {
                for img in images {
                    let b64 = general_purpose::STANDARD.encode(&img);
                    parts.push(serde_json::json!({
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": b64
                        }
                    }));
                }
            }

            let request_body = serde_json::json!({
                "contents": [{ "parts": parts }],
                "generationConfig": {
                    "responseMimeType": "application/json"
                }
            });

            let base_url = if settings.base_url.is_empty() || settings.base_url == "https://generativelanguage.googleapis.com" {
                "https://generativelanguage.googleapis.com/v1beta".to_string()
            } else {
                settings.base_url.clone()
            };

            let url = format!("{}/models/{}:generateContent?key={}", base_url, settings.model_name, settings.api_key);
            let res = client.post(&url).json(&request_body).send().await
                .map_err(|e| format!("Request failed: {}", e))?;
            let body: Value = res.json().await.map_err(|e| format!("JSON parse failure: {}", e))?;
            let txt = body["candidates"][0]["content"]["parts"][0]["text"].as_str()
                .ok_or_else(|| format!("Invalid response format: {:?}", body))?;
            Ok(txt.to_string())

        } else {
            let content_value = if let Some(images) = image_bytes_list {
                let mut parts = vec![serde_json::json!({ "type": "text", "text": full_prompt })];
                for img in images {
                    let b64 = general_purpose::STANDARD.encode(&img);
                    parts.push(serde_json::json!({
                        "type": "image_url",
                        "image_url": { "url": format!("data:image/jpeg;base64,{}", b64) }
                    }));
                }
                serde_json::json!(parts)
            } else {
                serde_json::json!(full_prompt)
            };

            let request_body = serde_json::json!({
                "model": settings.model_name,
                "messages": [{ "role": "user", "content": content_value }],
                "response_format": { "type": "json_object" }
            });

            let base_url = if settings.base_url.is_empty() {
                "https://api.openai.com/v1/chat/completions".to_string()
            } else {
                let mut url = settings.base_url.clone();
                if !url.ends_with("/chat/completions") {
                    if url.ends_with('/') {
                        url.push_str("chat/completions");
                    } else {
                        url.push_str("/chat/completions");
                    }
                }
                url
            };

            let res = client.post(&base_url)
                .header("Authorization", format!("Bearer {}", settings.api_key))
                .json(&request_body).send().await
                .map_err(|e| format!("Request failed: {}", e))?;
            let body: Value = res.json().await.map_err(|e| format!("JSON parse failure: {}", e))?;
            let txt = body["choices"][0]["message"]["content"].as_str()
                .ok_or_else(|| format!("Invalid response format: {:?}", body))?;
            Ok(txt.to_string())
        }
    }

    pub fn clean_and_extract_json(raw: &str) -> Result<serde_json::Value, String> {
        let mut clean = raw.trim().to_string();
        if let Some(start) = clean.find("<think>") {
            if let Some(end) = clean.find("</think>") {
                if end > start {
                    clean.replace_range(start..end + 8, "");
                }
            }
        }
        let mut json_str = clean.trim();
        if json_str.starts_with("```") {
            if let Some(first_line) = json_str.find('\n') {
                json_str = &json_str[first_line..];
            }
            if json_str.ends_with("```") {
                json_str = &json_str[..json_str.len() - 3];
            }
            json_str = json_str.trim();
        }
        serde_json::from_str(json_str).map_err(|e| format!("Deserialization error: {}", e))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_clean_and_extract_json() {
        let raw = "<think>some internal thought process</think>```json\n{\"materials\":[]}\n```";
        let parsed = AIService::clean_and_extract_json(raw).unwrap();
        assert_eq!(parsed["materials"].as_array().unwrap().len(), 0);
    }
}
