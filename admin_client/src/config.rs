use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

#[derive(Serialize, Deserialize, Debug)]

/// # use example
/// ```
/// let config = Config::load_config()?;
/// println!("loaded config: {:?}", config);
/// Ok(())
/// ```
pub struct Config {
    pub url: String,
    pub token: String,
}

impl Config {
    /// # create default config
    fn create_config() -> Result<(), Box<dyn std::error::Error>> {
        let config = Config {
            url: "http://localhost/admin".to_string(),
            token: "".to_string(),
        };

        let json_config = serde_json::to_string_pretty(&config)?;
        fs::write("config.json", json_config)?;

        println!("config file created");
        Ok(())
    }

    /// # load config from file
    pub fn load_config(path: &str) -> Result<Self, Box<dyn std::error::Error>> {

        if !Path::new(path).exists() {
            println!("config file doesn't exist create new...");
            Self::create_config()?;
        }

        let content = fs::read_to_string(path)?;
        let config: Config = serde_json::from_str(&content)?;
        Ok(config)
    }
    /// # return url variable
    pub fn get_url(&self) -> &String {
        &self.url
    }

    pub fn get_token(&self) -> String {
        self.token.clone()
    }

    pub fn set_token(&mut self, new_token: String) {
        self.token = new_token;
    }
}
