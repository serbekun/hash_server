import os
import secrets
from pathlib import Path

class Tokens:
    """
    # class for manage token mini database
    """

    def __init__(
        self,
        tokens_file: str,
        tokens_length: int,
        symbols: str = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM123456789",
        token_start: str = ""
        ):
        """
        # init Tokens object

        ## example
        ```python
        tokens = Tokens("tokens.txt", 15)
        ```

        ## but if you want your symbols list
        ```python
        tokens = Tokens("tokens.txt", 15, your_symbols)
        ```
        """

        self.tokens: set[str] = set()
        self.tokens_file = tokens_file
        self.symbols = symbols
        self.tokens_length = tokens_length
        self.token_start = token_start

        self.read_tokens()
    
    def gen_token(self) -> str:
        token = ''.join(
            secrets.choice(self.symbols)
            for _ in range(self.tokens_length)
        )
        return self.token_start + token

    def add_token(self, token: str) -> bool:
        """
        # add new token to file if that not exist
        
        ## example
        ```python
        token = tokens.gen_token()
        if tokens.add_tokens(token):
            print(f"Token {token} was added")
        else:
            print(f"adding {token} was error")
        ```
        """
        if token not in self.tokens:
            self.tokens.add(token)
            return True
        return False



    def remove_token(self, token: str) -> bool:
        """
        # remove token from file
        
        ## example
        ```python
        if tokens.remove_token(token):
            print(f"Token {token} was removed")
        else:
            print(f"removing token {token} was errors")
        ```
        """
        if token in self.tokens:
            self.tokens.remove(token)
            return True
        return False


    def check_token(self, token: str) -> bool:
        """
        # check exist token in file

        ## example
        ```python
        if tokens.check_token(token):
            print(f"Token {token} exist")
        else:
            print(f"Token {token} doesn't exist")
        ```
        """
        return token in self.tokens


    def read_tokens(self):
        """
        Function for load tokens from file
        """
        if not os.path.exists(self.tokens_file):
            self.tokens = []
        with open(self.tokens_file, "r", encoding="utf-8") as f:
            self.tokens = [line.strip() for line in f if line.strip()]

    
    def write_tokens(self):
        """
        Function for save tokens to file 
        """

        path = Path(self.tokens_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            for token in self.tokens:
                f.write(f"{token}\n")