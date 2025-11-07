from colorama import Fore, Style

# # print version of colorama for requirements.txt
# def get_colorama_version():
#     import colorama
#     print(colorama.__version__)


# get_colorama_version()

# light colors
r = Fore.LIGHTRED_EX
g = Fore.LIGHTGREEN_EX
b = Fore.LIGHTBLUE_EX
c = Fore.LIGHTCYAN_EX
y = Fore.LIGHTYELLOW_EX
m = Fore.LIGHTMAGENTA_EX
w = Fore.LIGHTWHITE_EX
re = Fore.RESET

# styles (dim, reset)
D = Style.DIM
R = Style.RESET_ALL


def print_terminal(message_type, sub_message_type, message, color=Fore.WHITE, style=Style.RESET_ALL):
    """Prints a message to the terminal with specified color and style."""

    if message_type == "INFO":
        color = Fore.CYAN

    if message_type == "WARNING" or message_type == "LOADING":
        color = Fore.YELLOW

    if sub_message_type == "Error":
        sub_message_color = Fore.RED

    if sub_message_type == "Completed":
        sub_message_color = Fore.GREEN

    if sub_message_type == "Initializing":
        sub_message_color = Fore.BLUE

    if sub_message_type == "Loading":
        sub_message_color = Fore.YELLOW

    if sub_message_type == "Time Change":
        sub_message_color = Fore.MAGENTA

    if sub_message_type == "Game Started":
        sub_message_color = Fore.GREEN
    
    if sub_message_type == "Auto Headlights":
        sub_message_color = Fore.YELLOW

    if sub_message_type == "Vehicle Selection":
        sub_message_color = Fore.CYAN

    if sub_message_type == "Info":
        sub_message_color = Fore.CYAN

    if sub_message_type == "Loading Game":
        sub_message_color = Fore.YELLOW

    if sub_message_type == "Day/Night Cycle":
        sub_message_color = Fore.MAGENTA

    if sub_message_type == "Headlights":
        sub_message_color = Fore.YELLOW

    if sub_message_type == "Vehicle":
        sub_message_color = Fore.CYAN
    
    if sub_message_type == "Text Info":
        sub_message_color = Fore.BLUE

    if sub_message_type == "Debug":
        sub_message_color = Fore.LIGHTBLACK_EX

    if sub_message_type == "Status":
        sub_message_color = Fore.GREEN

    if sub_message_type == "Transmission":
        sub_message_color = Fore.MAGENTA

    if sub_message_type == "Camera Lag":
        sub_message_color = Fore.LIGHTBLUE_EX

    if sub_message_type == "Game Reset":
        sub_message_color = Fore.MAGENTA

    if sub_message_type == "Game Exit":
        sub_message_color = Fore.RED

    if sub_message_type == "Window Size Selection":
        sub_message_color = Fore.CYAN

    if sub_message_type == "Game Start":
        sub_message_color = Fore.GREEN

    if sub_message_type == "Game Initialization":
        sub_message_color = Fore.CYAN

    if sub_message_type == "Size Selection":
        sub_message_color = Fore.CYAN

    if sub_message_type == "Gear Info":
        sub_message_color = Fore.CYAN

    if sub_message_type == "Time Info":
        sub_message_color = Fore.MAGENTA

    if sub_message_type == "HUD":
        sub_message_color = Fore.CYAN

    print(f"{color}{"{:<7}".format(message_type)}{re} {sub_message_color}{"{:<21}".format(sub_message_type)}{re} {message}{R}")