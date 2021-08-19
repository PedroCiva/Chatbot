import win32api
import win32gui
import threading
import keyboard
import time

WM_APPCOMMAND = 0x319
APPCOMMAND_MICROPHONE_VOLUME_MUTE = 0x180000

hwnd_active = win32gui.GetForegroundWindow()

mic_is_on = True
mic_hotkey = 'alt'
stop = False


def __toogle_mic():
    global mic_is_on
    while True and stop is False:
        if keyboard.is_pressed(mic_hotkey):
            if mic_is_on is True:
                win32api.SendMessage(hwnd_active, WM_APPCOMMAND, None, APPCOMMAND_MICROPHONE_VOLUME_MUTE)
                mic_is_on = False
                print("\nMicrophone is muted!")
            elif mic_is_on is False:
                win32api.SendMessage(hwnd_active, WM_APPCOMMAND, None, APPCOMMAND_MICROPHONE_VOLUME_MUTE)
                mic_is_on = True
                print("\nMicrophone is unmuted!")
            time.sleep(0.5)
    if stop is True: # Make sure to set microphone back to unmuted when leaving
        if mic_is_on is False:
            win32api.SendMessage(hwnd_active, WM_APPCOMMAND, None, APPCOMMAND_MICROPHONE_VOLUME_MUTE)






t1 = threading.Thread(target=  __toogle_mic)
t1.start()





