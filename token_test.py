from Tokens import Tokens
token = Tokens(token_file="test.txt", token_length=60, token_start="loh_")

for i in range(100):
    print(token.gen_token())