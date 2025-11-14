use reqwest;
use serde::Serialize;
use std::error::Error;
use tokio;
use std::io;

#[derive(Serialize)]
struct TokenPost {
    token: String
}

#[derive(Serialize)]
struct RequestSite {
    url: String,
}

impl RequestSite {
    async fn admin(&self) -> Result<(), Box<dyn Error>> {
        println!("input token:");
        
        let mut token = String::new();
        io::stdin().read_line(&mut token)?;
        
        let token = token.trim().to_string();
        
        if token.is_empty() {
            return Err("token can't be empty".into());
        }

        let json = TokenPost {
            token: token
        };

        let client = reqwest::Client::new();
        let response = client
            .post(&self.url)
            .json(&json)
            .send()
            .await?;

        println!("response status: {}", response.status());
        println!("response body: {}", response.text().await?);

        Ok(())
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let request_site = RequestSite {
        url: "http://192.168.3.19:2222/admin".to_string(),
    };

    request_site.admin().await?;

    Ok(())
}