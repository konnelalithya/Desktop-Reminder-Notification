from tkinter import *
from tkinter import messagebox
from plyer import notification
from PIL import Image, ImageTk
import pygame
import tempfile
from gtts import gTTS
import os
from tkcalendar import DateEntry
import datetime
import time

# Initialize pygame mixer
pygame.mixer.init()

# Global list to keep track of notification history
notification_history = []

# Function to play the voice notification
def voice_notification(title):
    message = f"{title}"
    tts = gTTS(text=message, lang='en')

    # Create a temporary file to store the audio
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    temp_file.close()  # Close the file to avoid permission issues

    try:
        # Save the generated voice message to the temp file
        tts.save(temp_file.name)
        print(f"Voice notification saved to {temp_file.name}")  # Debugging line

        # Stop any currently playing music
        pygame.mixer.music.stop()

        # Load the mp3 file using pygame and play it
        pygame.mixer.music.load(temp_file.name)
        pygame.mixer.music.play()

        print(f"Playing voice notification for: {title}")

        # Wait until the sound has finished playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"An error occurred while playing the voice notification: {e}")
    finally:
        # Remove the temp file after use
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

# Function to get today's screen time
def get_today_screen_time():
    # Placeholder: Replace this with the actual screen time retrieval logic
    # For demonstration purposes, I'm using a static value
    return "2 hours and 15 minutes"  # Replace this with real screen time data retrieval

# Function to open the notifier window
def open_notifier():
    notifier_window = Toplevel(main_menu)
    notifier_window.title('Notifier')
    notifier_window.geometry("1000x700")
    notifier_window.configure(bg="#e0f7fa")

    try:
        img = Image.open("notify-label.png")
        tkimage = ImageTk.PhotoImage(img)
        img_label = Label(notifier_window, image=tkimage, bg="#e0f7fa")
        img_label.image = tkimage  # Keep a reference to avoid garbage collection
        img_label.pack(pady=(20, 0))
    except FileNotFoundError:
        print("notify-label.png not found, skipping image loading.")

    icon_paths = {
        "eye": "eye.ico",
        "glass": "glass.ico",
        "ear": "ear.ico",
        "body": "BODY.ico",
        "bed": "BED.ico",
        "meeting": "meeting.ico",
        "reminder": "reminder.ico",
        "medicine": "medicine.ico"
    }

    user_notifications = []

    def add_notification():
        frame = Frame(notifier_window, bg="#e0f7fa")
        frame.pack(pady=10)

        title_label = Label(frame, text="Title:", bg="#e0f7fa", font=("Calibri", 12))
        title_label.grid(row=0, column=0, padx=(5, 10), pady=(5, 5))

        title_entry = Entry(frame, width=25, font=("Calibri", 12), bg="#ffffff", fg="#000000", bd=2, relief="groove", highlightthickness=1)
        title_entry.grid(row=0, column=1, padx=(5, 10), pady=(5, 5))

        msg_label = Label(frame, text="Message:", bg="#e0f7fa", font=("Calibri", 12))
        msg_label.grid(row=1, column=0, padx=(5, 10), pady=(5, 5))

        msg_entry = Entry(frame, width=25, font=("Calibri", 12), bg="#ffffff", fg="#000000", bd=2, relief="groove", highlightthickness=1)
        msg_entry.grid(row=1, column=1, padx=(5, 10), pady=(5, 5))

        date_label = Label(frame, text="Date:", bg="#e0f7fa", font=("Calibri", 12))
        date_label.grid(row=2, column=0, padx=(5, 10), pady=(5, 5))

        date_entry = DateEntry(frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        date_entry.grid(row=2, column=1, padx=(5, 10), pady=(5, 5))

        time_label = Label(frame, text="Time:", bg="#e0f7fa", font=("Calibri", 12))
        time_label.grid(row=3, column=0, padx=(5, 10), pady=(5, 5))

        time_entry = Entry(frame, width=10, font=("Calibri", 12), bg="#f5f5f5", fg="#333333", bd=2, relief="solid", highlightthickness=1)
        time_entry.grid(row=3, column=1, padx=(5, 10), pady=(5, 5))

        icon_label = Label(frame, text="Icon:", bg="#e0f7fa", font=("Calibri", 12))
        icon_label.grid(row=4, column=0, padx=(5, 10), pady=(5, 5))

        icon_var = StringVar(frame)
        icon_var.set("No Icon")
        icon_option = OptionMenu(frame, icon_var, "No Icon", *icon_paths.keys())
        icon_option.grid(row=4, column=1, padx=(5, 10), pady=(5, 5))

        user_notifications.append((title_entry, msg_entry, date_entry, time_entry, icon_var))

    def send_notifications():
        for title_entry, msg_entry, date_entry, time_entry, icon_var in user_notifications:
            title = title_entry.get()
            message = msg_entry.get()
            icon_key = icon_var.get()
            date = date_entry.get()
            time = time_entry.get()

            if not title or not message:
                messagebox.showwarning("Input Error", "Title and message cannot be empty!")
                return

            # Validate time format
            try:
                notification_time = datetime.datetime.strptime(f"{date} {time}", "%m/%d/%y %H:%M")
                total_seconds = (notification_time - datetime.datetime.now()).total_seconds()
                if total_seconds < 0:
                    raise ValueError("The selected time is in the past.")
            except ValueError as e:
                messagebox.showwarning("Input Error", str(e))
                return

            # Automatically repeat notification 3 times
            for _ in range(3):
                if total_seconds > 0:
                    notifier_window.after(int(total_seconds * 1000), send_single_notification, title, message, icon_key)
                else:
                    send_single_notification(title, message, icon_key)

        messagebox.showinfo("Notifications Sent", "All notifications have been sent successfully!")

    def send_single_notification(title, message, icon_key):
        icon = icon_paths.get(icon_key) if icon_key in icon_paths and icon_key != "No Icon" else None
        
        # Get today's screen time
        screen_time = get_today_screen_time()

        notification.notify(
            title=title,
            message=f"{message}\nToday's screen time: {screen_time}",
            app_name="Notifier",
            app_icon=icon,
            toast=True,
            timeout=10
        )

        notification_history.append(f"{title}: {message} (Sent)")

        voice_notification(title)

    # Function to clear the notification history
    def clear_notifications():
        global notification_history
        notification_history = []  # Clear the history
        messagebox.showinfo("Cleared", "Notification history has been cleared.")

    add_button = Button(notifier_window, text="Add Notification", command=add_notification, bg="#4db6ac", fg="black", font=("Calibri", 12), bd=2, relief="ridge")
    add_button.pack(pady=(20, 10))

    send_all_button = Button(notifier_window, text="Send All Notifications", command=send_notifications, bg="#4db6ac", fg="black", font=("Calibri", 12), bd=2, relief="ridge")
    send_all_button.pack(pady=(10, 20))

    clear_button = Button(notifier_window, text="Clear Notification History", command=clear_notifications, bg="#e57373", fg="black", font=("Calibri", 12), bd=2, relief="ridge")
    clear_button.pack(pady=(10, 20))

# Exit function
def exit_application():
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        main_menu.destroy()

# Main menu window
main_menu = Tk()
main_menu.title('Desktop Reminder Notification')
main_menu.geometry("1000x700")
main_menu.configure(bg="#e0f7fa")

# Set background
def load_background_image():
    try:
        bg_image = Image.open("background.png")  # Make sure the file path is correct
        return bg_image
    except FileNotFoundError:
        print("background.png not found.")
        return None

def set_background():
    global bg_image_tk
    bg_image = load_background_image()
    if bg_image:
        bg_image = bg_image.resize((main_menu.winfo_width(), main_menu.winfo_height()), Image.LANCZOS)  # Resize to window size
        bg_image_tk = ImageTk.PhotoImage(bg_image)

        # Update the label for the background
        bg_label.configure(image=bg_image_tk)
        bg_label.image = bg_image_tk  # Keep a reference

bg_image_tk = load_background_image()
if bg_image_tk:
    bg_image_tk = ImageTk.PhotoImage(bg_image_tk)  # Create PhotoImage only if image loaded successfully
    bg_label = Label(main_menu, image=bg_image_tk)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Full window

# Bind the function to resize the background when the window is resized
def on_resize(event):
    set_background()

main_menu.bind("<Configure>", on_resize)

# Welcome message
welcome_label = Label(main_menu, text="Welcome to Desktop Reminder Notification!", bg="#e0f7fa", font=("Calibri", 16))
welcome_label.pack(pady=(20, 10))

notifier_button = Button(main_menu, text="Open Notifier", command=open_notifier, bg="#4db6ac", fg="black", font=("Calibri", 12), bd=2, relief="ridge")
notifier_button.pack(pady=(10, 20))

exit_button = Button(main_menu, text="Exit", command=exit_application, bg="#e57373", fg="black", font=("Calibri", 12), bd=2, relief="ridge")
exit_button.pack(pady=(10, 20))

main_menu.protocol("WM_DELETE_WINDOW", exit_application)

# Start the main loop
main_menu.mainloop()
