use clear_screen::clear;
use lazy_static::lazy_static;
use rustyline::Editor;
use rustyline::error::ReadlineError;
use std::error::Error;
use std::io::{self, Write};
use std::sync::Mutex;
use tokio;

mod config;
mod request_site;

lazy_static! {
    static ref CONFIG: Mutex<config::Config> =
        Mutex::new(config::Config::load_config("config.json").expect("Failed to load config"));
    static ref REQUEST_SITE: Mutex<request_site::RequestSite> = Mutex::new({
        let config = CONFIG.lock().unwrap();
        request_site::RequestSite::new(config.get_url().clone())
    });
}

fn set_token(new_token: String) -> Result<(), Box<dyn Error>> {
    let new_token = new_token.trim().to_string();

    if new_token.is_empty() {
        return Err("token can't be empty".into());
    }

    {
        let mut config = CONFIG.lock().unwrap();
        config.set_token(new_token.clone());
    }

    Ok(())
}

fn get_token_input() -> Result<String, Box<dyn Error>> {
    let mut token = String::new();
    print!("input token: ");
    std::io::stdout().flush()?;
    io::stdin().read_line(&mut token)?;

    let token = token.trim().to_string();
    if token.is_empty() {
        return Err("token can't be empty".into());
    }

    Ok(token)
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    {
        let config = CONFIG.lock().unwrap();
        println!("loaded config: {:?}", *config);
    }

    let mut rl = Editor::<()>::new().unwrap_or_else(|e| {
        eprintln!("Error init CLI: {}", e);
        std::process::exit(1);
    });

    loop {
        let readline = rl.readline("> ");
        match readline {
            Ok(line) => {
                let input = line.trim();
                if input.is_empty() {
                    continue;
                }
                let _ = rl.add_history_entry(input);

                match input {
                    "exit" => break,
                    "clear" => clear(),
                    "set_token" => match get_token_input() {
                        Ok(token) => {
                            if let Err(e) = set_token(token) {
                                eprintln!("Error setting token: {}", e);
                            }
                        }
                        Err(e) => eprintln!("Error reading token: {}", e),
                    },
                    "admin" => {
                        let request_site = REQUEST_SITE.lock().unwrap();
                        if let Err(e) = request_site.admin().await {
                            eprintln!("Error in admin: {}", e);
                        }
                    }
                    "clear_uploads" => {
                        let request_site = REQUEST_SITE.lock().unwrap();
                        if let Err(e) = request_site.clear_upload().await {
                            eprintln!("Error in clear_uploads: {}", e);
                        }
                    }
                    "list_uploads" => {
                        let request_site = REQUEST_SITE.lock().unwrap();
                        if let Err(e) = request_site.list_uploads().await {
                            eprintln!("Error in list_uploads: {}", e);
                        }
                    }
                    "log" => {
                        let request_site = REQUEST_SITE.lock().unwrap();
                        if let Err(e) = request_site.log().await {
                            eprintln!("Error in log: {}", e);
                        }
                    }
                    _ => println!("Unknown command {}", input),
                }
            }
            Err(ReadlineError::Interrupted) => {
                println!("Ctrl-C - exit");
                break;
            }
            Err(ReadlineError::Eof) => {
                println!("Ctrl-D - exit");
                break;
            }
            Err(err) => {
                println!("Input error: {:?}", err);
                break;
            }
        }
    }

    Ok(())
}
