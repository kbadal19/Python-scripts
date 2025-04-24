import time
import pyautogui

# Add a short delay to give time to switch windows before the bot starts typing
time.sleep(3)

# Open the file and read its contents
with open("text1.txt", "r") as file:
    lines = file.readlines()

# Loop through each line, strip leading/trailing whitespace, and type it
for line in lines:
    stripped_line = line.strip()  # Remove only trailing whitespace (like newlines)
    pyautogui.typewrite(stripped_line)
    pyautogui.press('enter')  # Press enter to simulate newlines
          