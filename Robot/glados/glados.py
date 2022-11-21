from os import system
from tqdm import tqdm
import torch
from glados.utils.tools import prepare_text
from scipy.io.wavfile import write
import time
from sys import modules as mod
import sys

print("Initializing TTS Engine...")

# Select the device
if torch.is_vulkan_available():
    device = 'vulkan'
if torch.cuda.is_available():
    print('USING CUDA')
    device = 'cuda'
else:
    device = 'cpu'
    print('USING CPU')

# Load models
glados = torch.jit.load('glados/models/glados.pt')
vocoder = torch.jit.load('glados/models/vocoder-gpu.pt', map_location=device)

# Prepare models in RAM

for i in tqdm(range(5)):
    init = glados.generate_jit(prepare_text(str(i)))
    init_mel = init['mel_post'].to(device)
    init_vo = vocoder(init_mel)


def speak(text):
    try:
        if len(text) > 0:

            # Tokenize, clean and phonemize input text
            x = prepare_text(text).to('cpu')

            with torch.no_grad():

                # Generate generic TTS-output
                old_time = time.time()
                tts_output = glados.generate_jit(x)
                # print("Forward Tacotron took " + str((time.time() - old_time) * 1000) + "ms")

                # Use HiFiGAN as vocoder to make output sound like GLaDOS
                old_time = time.time()
                mel = tts_output['mel_post'].to(device)
                audio = vocoder(mel)
                # print("HiFiGAN took " + str((time.time() - old_time) * 1000) + "ms")

                # Normalize audio to fit in wav-file
                audio = audio.squeeze()
                audio = audio * 32768.0
                audio = audio.cpu().numpy().astype('int16')
                output_file = 'output.wav'

                write(output_file, 22050, audio)

                # Play audio file
                system('amixer -D pulse set Capture toggle > /dev/null')
                system("aplay output.wav")
                system('amixer -D pulse set Capture toggle > /dev/null')

    except:
        print("ERROR in glados.py")
