from config import Config

class Logging:

    def server_log(log: str) -> None:
        """
        Print and save log to file
        """
        with open(Config.Paths.Log.LOG_FOLDER + Config.Paths.Log.SERVER_LOG, 'a') as f:
            try:
                f.write(f"{log}\n")
            except FileExistsError:
                print("Server Error: Error save log")
            
        print(log)