from __future__ import division
from google.cloud import speech
import keyboard
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"  # Location of Google Credentials

import time
import re
import sys

import pyaudio
from six.moves import queue

import TTS
import chat
import audio

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

TTS.list_voices()
TTS.change_voice("HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_FR-FR_HORTENSE_11.0") #French ID

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


def listen_print_loop(responses):
    global my_speech
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = " " * (num_chars_printed - len(transcript))
        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()
            num_chars_printed = len(transcript)

        else:
            my_speech = str(transcript+overwrite_chars)
            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r"\b(exit|quit|ferme)\b", transcript, re.I):
                print("Exiting..")
                audio.stop = True
                break
            elif re.search(r"\b(interrogation)\b", transcript, re.I):
                my_speech = my_speech.replace("interrogation", "?")

            num_chars_printed = 0

            # Verify with user if his input is correct
            print("You said: " + my_speech)

            is_correct = input("If this is correct, press Y, if not press N to try again, press V to change the AI voice speed or press Q to quit:")
            print(is_correct)
            if is_correct == 'n' or is_correct == 'N':
                my_speech = ""
            elif is_correct == 'q' or is_correct =='Q':
                audio.stop = True
                break
            elif is_correct == 'v' or is_correct == 'V':
                print("Current speed is: " + TTS.get_speed())
                speed = TTS.get_speed()
                speed = input("Speed levels are 100 (slowest) to 200 (fastest), make your choice: ")
                while speed < "100" or speed > "200":
                    print("Here")
                    print("Error, try again...")
                    speed = input("Speed levels are 100 (slowest) to 200 (fastest), make your choice: ")
                is_good = "n"
                while is_good == 'n' or is_good == "N":
                    TTS.change_speed(rate=int(speed))
                    TTS.Say("je parle de quelque chose")
                    is_good = input("If this speed is good for you press Y, press N to change speed.")
                    if is_good == "n" or is_good == "N":
                        speed = input("Speed levels are 100 (slowest) to 200 (fastest), make your choice: ")
                    else:
                        while speed < "100" or speed > "200":
                            print("Error, try again...")
                            speed = input("Speed levels are 100 (slowest) to 200 (fastest), make your choice: ")
            else:
                # Translate my speech to english
                my_speech_translated = TTS.Translate(my_speech, 'en')

                # Send message
                chat.send_message(my_speech_translated)
                time.sleep(8)  # Wait for AI response

                # Get AI response
                ai_response = chat.GetMessage()
                # Translate AI response back to french
                ai_response = TTS.Translate(ai_response, 'fr')
                # Speak AI response
                should_repeat = 'y'
                while should_repeat == 'y' or should_repeat == 'Y':
                    TTS.Say(ai_response)
                    should_repeat = input("Would you like to hear that again? Press Y or N.")






def main():

    # Initialize Chat
    chat.main()
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = "fr-FR"  # a BCP-47 language tag
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)
        # Now, put the transcription responses to use.

        listen_print_loop(responses)


if __name__ == "__main__":
    main()