import random
import sys
import hashlib
import csv


#colour codes
class colours:
  RED = '\033[91m'
  GREEN = '\033[32m'
  YELLOW = '\033[33m'
  BLUE = '\033[34m'
  GREY = '\033[90m'
  MAGENTA = '\033[95m'
  BOLD = '\033[1m'
  END = '\033[0m'


#encrypting the passwords
def hash_password(password):
  hashed_password = hashlib.sha256(password.encode()).hexdigest()
  return hashed_password


def print_stats():
  global games_played, num_wins, win_streak, max_win_streak, guess_distribution

  print('\n' + '=' * 40)
  print("           Player Statistics")
  print('=' * 40 + '\n')
  print(f"{colours.BLUE}Total Games Played: {games_played}{colours.END}")
  print(f"{colours.BLUE}Total Wins: {num_wins}{colours.END}")
  print(f"{colours.BLUE}Win Streak: {win_streak}{colours.END}")
  print(f"{colours.BLUE}Longest Win Streak: {max_win_streak}{colours.END}")
  print(
      f"{colours.BLUE}Win Percentange: {round((num_wins / games_played) * 100)}%{colours.END}"
  )
  print('\n' + '=' * 40)
  print("           Guess Distribution")
  print("                  Chart")
  print('=' * 40 + '\n')
  for i, count in enumerate(guess_distribution):
    print(f"{i+1}: {colours.GREEN}{'*' * count}{colours.END}")
  return True


#keeping track of user data
def update_player_info(username):
  global games_played, num_wins, win_streak, max_win_streak, guess_distribution

  with open('playersinfo.csv', 'r+') as file:
    lines = list(csv.reader(file))
    for i in range(len(lines)):
      if lines[i][0] == username:
        infos = [
            games_played, num_wins, win_streak, max_win_streak,
            *guess_distribution
        ]
        for j, info in enumerate(infos):
          lines[i][2 + j] = str(info)

    file.seek(0)
    writer = csv.writer(file)
    writer.writerows(lines)


#login to your specific account, to keep track of personal data
def account():
  global games_played, num_wins, win_streak, max_win_streak, guess_distribution

  while True:
    while True:

      account = input("LOGIN: Do you have an account? (y/n): ").strip()

      if account.lower() not in ['n', 'y']:
        print("Invalid Input, enter 'y' for yes or 'n' for no")
        continue

      elif account.lower() == 'n':
        #start creating account for new user
        while True:
          new_username = input("Create a username: ").lower()
          username_exits = False
          with open("playersinfo.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
              if row[0] == new_username.lower():
                print("username already taken")
                username_exits = True
                break

          if username_exits:
            break

          #ensure valid password
          while True:
            new_password = input(
                "Create a password, (must be 4 digits): ").strip()

            if not new_password.isdigit() or len(new_password) != 4:
              print("password must be exactly 4 numbers")
              continue

            hashed_password = hash_password(new_password)

            print("You have successfully created an account!")

            with open("playersinfo.csv", "a") as file:
              writer = csv.writer(file)
              writer.writerow([
                  new_username, hashed_password, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
              ])
            run_game(new_username)
            break
          break

  # if user has an account prompt for login
      elif account.lower() == 'y':
        while True:
          enter_username = input("Enter your username here: ").lower()
          with open("playersinfo.csv", "r") as file:
            lines = list(csv.reader(file))
    #checks if username exists in database
          if any(enter_username.lower() == line[0] for line in lines):
            for i, line in enumerate(lines):
              (username, hashed_password, str_games_played, str_num_wins,
               str_win_streak, str_max_win_streak,
               *str_guess_distribution) = line
              (games_played, num_wins, win_streak, max_win_streak) = (
                  int(str_games_played),
                  int(str_num_wins),
                  int(str_win_streak),
                  int(str_max_win_streak),
              )

              guess_distribution = [int(v) for v in str_guess_distribution]

              if enter_username.lower() == username.lower():
                while True:
                  enter_password = input("Enter your password here: ")

                  if hash_password(enter_password).strip() != hashed_password:
                    print("Wrong Password try again! (hint: It's 4 numbers)")
                    continue

                  if hash_password(enter_password).strip() == hashed_password:
                    run_game(enter_username)

            break
          else:
            print("User not found, try again")
            break


# filters through invalid guesses
def check_error(guess):
  if not guess.isalpha() and len(guess) != 5:
    print(colours.RED + "Has to be 5 letters & No numbers allowed " +
          colours.END)
    return True
  elif not guess.isalpha():
    print(colours.RED + "Only letters!" + colours.END)
    return True
  elif len(guess) != 5:
    print(colours.RED + "5 letters please!" + colours.END)
    return True
  else:
    with open('fiveletterdict.txt', 'r') as file:
      real_words = [line.strip() for line in file]
      if guess.strip() not in real_words:
        print(colours.GREY + "Thats not a real word!" + colours.END)
        return True
      return False


# checks if the guess was correct
def check_answer(guess, secret_word):
  if guess.upper() == secret_word.upper():
    return "win"
  else:
    return "lose"


#implementing hint logic
def hint(secret_word, guess):
  output = []
  guessed_letters = []
  remaining_letters = list(secret_word)

  for i in range(len(secret_word)):
    if guess[i].lower() not in secret_word:
      if guess[i].lower() != secret_word[i]:
        guessed_letters.append((guess[i].lower(), "-"))

    elif guess[i].lower() == secret_word[i]:
      guessed_letters.append((guess[i].lower(), "#"))
      remaining_letters.remove(guess[i].lower())

    elif guess[i].lower() != secret_word and guess[i].lower() in secret_word:
      guessed_letters.append((guess[i].lower(), "*"))

#making sure '*' deoesn't show up specifically when theres multiple of a letter guessed and all of them are found
  for i, (x, y) in enumerate(guessed_letters):
    if y == "*" and x in remaining_letters:
      remaining_letters.remove(x)
    elif y == "*" and x not in remaining_letters:
      guessed_letters[i] = (x, "-")

  for _, y in guessed_letters:
    output.append(y)

#assigning each symbol with a colour to mimic 'wordle'
  clean_output = ''
  for char in output:
    if char == '-':
      clean_output += colours.GREY + char + colours.END
    elif char == '#':
      clean_output += colours.GREEN + char + colours.END
    elif char == '*':
      clean_output += colours.YELLOW + char + colours.END
    else:
      clean_output += char
  return clean_output


# Allows user to play again
def replay(username):
  while True:
    replay = input(f"\nDo you want to play again? (yes/no): ").strip().lower()
    if replay == "yes":
      return True
    elif replay == "no":
      print("Thanks For Playing")
      update_player_info(username)
      sys.exit()
    else:
      print("Invalid input. Please enter 'yes' or 'no'.")


#choose a random word from the dictionary of common 5 letter words
def find_word():
  with open("secretwordlist.txt", 'r') as file:
    words = file.readlines()
    random_word = random.choice(words).strip()
    return random_word


# Handling game logic, basically puts everything together
games_played = 0
num_wins = 0
win_streak = 0
max_win_streak = 0
guess_distribution = [0 for _ in range(6)]


def run_game(username):
  global games_played, num_wins, win_streak, max_win_streak

  print("Starting the game...")
  games_played += 1

  secret_word = find_word()
  num_guess = 0

  while num_guess < 6:
    update_player_info(username)
    num_guess += 1
    #prompting user with a question
    print(f"\nGuess #{num_guess} of 6")
    guess = input(colours.BLUE + "Guess a 5 letter word: " +
                  colours.END).strip()

    error = check_error(guess)
    if error:
      num_guess -= 1
      continue

    check_result = check_answer(guess, secret_word)
    if check_result == "win":
      win_streak += 1
      num_wins += 1
      guess_distribution[num_guess - 1] += 1

      if win_streak > max_win_streak:
        max_win_streak = win_streak

      print(colours.GREEN + f"You won in {num_guess} try!" +
            colours.END if num_guess == 1 else colours.GREEN +
            f"You win! It took you {num_guess} tries." + colours.END)
      print_stats()

      if num_guess > 6 or not replay(username):
        update_player_info(username)
        return
      else:
        run_game(username)

    else:
      if num_guess == 6:
        win_streak = 0
        print(colours.RED + f"The word was not {guess} it was {secret_word}" +
              colours.END)
      else:
        hint_output = hint(secret_word, guess)
        print(colours.MAGENTA + f"                 Hint: {hint_output}" +
              colours.END)

  print("GAME OVER! Only 6 tries allowed.")
  print_stats()

  if replay(username):
    update_player_info(username)
    run_game(username)


# if user wants the instructioins
def main():
  while True:
    response = input(
        colours.MAGENTA +
        f"               Welcome To Wordle\n     Do you want to go directly to the game \n          or do you want instructions? \n\n(Type 'G' for game or 'I' for instructions): "
        + colours.END).strip().lower()
    if response == "i":
      print(colours.RED +
            "\n1. Guess the 5-letter secret word within 6 attempts." +
            colours.END)
      print(
          colours.RED +
          "2. Input your guess, ensuring it's a valid 5-letter word\nwith only alphabetical characters."
          + colours.END)
      print(colours.RED +
            "3. Win by guessing the word exactly or receive hints:" +
            colours.END)
      print(colours.RED + "   #: Correct letter in the correct position." +
            colours.END)
      print(colours.RED + "   *: Correct letter but in the wrong position." +
            colours.END)
      print(colours.RED + "   -: Incorrect letter." + colours.END)
      print(
          colours.RED +
          "4. Choose to play again or exit after winning or reaching the maximum attempts."
          + colours.END)

      play = input("\nDo you want to play now? (Yes/No):").strip().lower()
      while play not in ['yes', 'no']:
        print(colours.RED + "Invalid input. Please enter 'Yes' or 'No'." +
              colours.END)
        play = input("Do you want to play now? (Yes/No):").strip().lower()

      if play == 'yes':
        account()
        return True
      elif play == 'no':
        print("Bye, see you later!")
        return False

    elif response == "g":
      account()
      return True
    else:
      print(colours.RED + "Invalid input. Please enter 'G' or 'I'." +
            colours.END)


if __name__ == "__main__":
  main()
