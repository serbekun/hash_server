use reqwest;
use serde::Serialize;
use std::error::Error;
use std::io::{self, Write};

use crate::CONFIG;

#[derive(Serialize)]
struct TokenPost {
    token: String,
}

#[derive(Serialize)]
pub struct RequestSite {
    url: String,
}

impl RequestSite {
    pub fn new(url: String) -> RequestSite {
        RequestSite { url }
    }

    async fn post_to_endpoint(&self, endpoint: &str) -> Result<(), Box<dyn Error>> {
        let url = if endpoint.is_empty() {
            self.url.clone()
        } else {
            format!("{}{}", self.url, endpoint)
        };

        let token = self.read_token()?;
        let json = TokenPost { token };

        let client = reqwest::Client::new();
        let response = client.post(&url).json(&json).send().await?;

        println!("response status: {}", response.status());
        println!("response body: {}", response.text().await?);

        Ok(())
    }

    fn read_token(&self) -> Result<String, Box<dyn Error>> {
        let current_token = {
            let config = CONFIG.lock().unwrap();
            config.get_token().clone()
        };

        if !current_token.is_empty() {
            return Ok(current_token);
        }

        let mut new_token = String::new();
        print!("input token: ");
        io::stdout().flush()?;
        io::stdin().read_line(&mut new_token)?;

        let new_token = new_token.trim().to_string();

        if new_token.is_empty() {
            return Err("token can't be empty".into());
        }

        Ok(new_token)
    }

    pub async fn admin(&self) -> Result<(), Box<dyn Error>> {
        self.post_to_endpoint("").await
    }

    pub async fn clear_upload(&self) -> Result<(), Box<dyn Error>> {
        self.post_to_endpoint("/clear_uploads").await
    }

    pub async fn list_uploads(&self) -> Result<(), Box<dyn Error>> {
        self.post_to_endpoint("/list_uploads").await
    }

    pub async fn log(&self) -> Result<(), Box<dyn Error>> {
        self.post_to_endpoint("/log").await
    }
}
