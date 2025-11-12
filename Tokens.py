import os
import random

class Tokens:
    """
    # class for manage token mini database
    """

    def __init__(
        self, token_file: str,
        hash_length: str,
        symbols: str = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM123456789-_"
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

        self.token_file = token_file
        self.symbols = symbols
        self.hash_length = hash_length

    def gen_token(self) -> str:
        """
        # gen token from symbols
        
        ## example
        ```python
        token = tokens.gen_token()
        print(token)
        ```
        """
        token = ""
        for _ in range(15):
            token += random.choice(self.symbols)
        return token


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
        tokens = self.read_tokens()
        if token not in tokens:
            with open(self.token_file, "a", encoding="utf-8") as f:
                f.write(token + "\n")
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
        tokens = self.read_tokens()
        if token in tokens:
            tokens.remove(token)
            with open(self.token_file, "w", encoding="utf-8") as f:
                f.write("\n".join(tokens) + "\n" if tokens else "")
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
        tokens = self.read_tokens()
        return token in tokens


    def read_tokens(self):
        """
        # help function - read all token from file
        """
        if not os.path.exists(self.token_file):
            return []
        with open(self.token_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
