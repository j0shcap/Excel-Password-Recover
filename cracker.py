import time
from random import randint
import msoffcrypto
import msoffcrypto.exceptions
import io
from manual_wordlist import MY_WORDLIST

class Cracker:
    __passwords: list[str] = []
    __filename: str = ""
    __wordlist: str = ""
    __wordlist_length: int = len(MY_WORDLIST)
    __verbose: bool = True
    __wordlist_pointer: int = 0

    def __init__(self, filename, verbose, wordlist="default"):
        self.__filename = filename
        self.__verbose = verbose
        if wordlist == "default":
            self.__passwords = MY_WORDLIST
        else:
            self.__wordlist = wordlist
            self.read_password_list()
        while (self.__wordlist_pointer < self.__wordlist_length):
           password_guess = self.get_password()
           if self.__verbose:
                print(f"Trying {password_guess}...")
           guess = self.decrypt(str(password_guess))
           if (guess):
                self.success(password_guess)
                return
        self.end()

    def decrypt(self, password) -> bool:
        # verify_password/verify_integrity make msoffcrypto reject wrong
        # passwords instead of "decrypting" garbage and reporting success (#1).
        try:
            decrypted = io.BytesIO()
            with open(self.__filename, "rb") as f:
                file = msoffcrypto.OfficeFile(f)
                file.load_key(password=password, verify_password=True)
                file.decrypt(decrypted, verify_integrity=True)
            return True
        except msoffcrypto.exceptions.DecryptionError:
            return False

    def read_decrypted_file(self, correct_password) -> None:
        """Prints locked file information in the terminal."""
        import pandas as pd
        decrypted = io.BytesIO()
        with open(self.__filename, "rb") as f:
            file = msoffcrypto.OfficeFile(f)
            file.load_key(password=correct_password, verify_password=True)
            file.decrypt(decrypted, verify_integrity=True)
        df = pd.read_excel(decrypted)
        print(df)

    def get_password(self) -> str:
        self.__wordlist_pointer+=1
        return self.__passwords[self.__wordlist_pointer-1]

    def get_random_password(self) -> str:
        index = self.random_index()
        return self.__passwords[index]

    def read_password_list(self) -> None:
        with open(self.__wordlist, "r") as f:
            for line in f:
                self.__passwords.append(line.rstrip('\n'))
        self.__wordlist_length = len(self.__passwords)

    def random_index(self) -> int:
        return randint(0,self.__wordlist_length)

    def end(self) -> None:
        print(f"No password found :(")

    def success(self, password) -> None:
        print(f"CRACKED: {password}")
        self.read_decrypted_file(password)
        print("Good luck on your interview!")


# if __name__ == "__main__":
#     newCracker = Cracker()

