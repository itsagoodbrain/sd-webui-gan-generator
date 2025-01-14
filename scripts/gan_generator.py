import modules.scripts as scripts
import gradio as gr
import glob, os

from modules import script_callbacks
import json

import gradio as gr
import numpy as np

from scripts.model import Model


model = Model()

DESCRIPTION = '''# StyleGAN3 Simple Image Generator Extension

Use this tool to generate random images with a pretrained StyleGAN3 network of your choice. 
Download model pickle files and place them in sd-webui-gan-generator/models folder. 
Supports generation with the cpu or gpu0. See available pretrained networks via [https://github.com/NVlabs/stylegan3](https://github.com/NVlabs/stylegan3).
Recommend using stylegan3-r-ffhq or stylegan2-celebahq
'''
def swap_slider(slider1, slider2):
    return slider2, slider1
    
def random_seeds(slider1, slider2):
    import random
    return random.randint(0, 4294967295 - 1), random.randint(0, 4294967295 - 1) 
    
def send_style(slider1):
    return slider1

def update_model_list():
    currentfile = os.path.dirname(__file__)
    path = currentfile + '\\..\\models\\'    
    return [os.path.basename(file) for file in glob.glob(path+"*.pkl")]
    
def update_model_drop():
    new_choices = gr.Dropdown.update(choices = update_model_list())
    return new_choices

def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False, css='style.css') as ui_component:
        gr.Markdown(DESCRIPTION)
        with gr.Column():
            modelDrop = gr.Dropdown(choices = update_model_list(), label="Model Selection", info="Place into models directory")            
            model_refresh_button = gr.Button('Refresh')
            deviceDrop = gr.Dropdown(choices = ['cpu','cuda:0'], value='cpu', label='Generation Device', info='Generate using CPU or GPU')
                                
        with gr.Tabs():
            with gr.TabItem('Simple Image Gen'):
                with gr.Row():
                    with gr.Column():
                        seed = gr.Slider(0,
                                         np.iinfo(np.uint32).max,
                                         step=1,
                                         value=0,
                                         label='Seed')
                        psi = gr.Slider(0,
                                        2,
                                        step=0.05,
                                        value=0.7,
                                        label='Truncation psi')
                        randomSeed = gr.Checkbox(value=False, label='Random Seed')
                        
                        simple_run_button = gr.Button('Generate Simple Image')

                    with gr.Column():
                        result = gr.Image(label='Result', elem_id='result')
                        outputSeed = gr.Markdown(label='Output Seed')
                        with gr.Row():
                            send_to_style_button1 = gr.Button('Send Seed to Style Seed1')
                            send_to_style_button2 = gr.Button('Send Seed to Style Seed2')
                        
            with gr.TabItem('Style Mixing'):
                with gr.Row():
                    with gr.Column():
                        seed1 = gr.Slider(0,
                                         np.iinfo(np.uint32).max,
                                         step=1,
                                         value=0,
                                         label='Seed 1')
                        seed2 = gr.Slider(0,
                                         np.iinfo(np.uint32).max,
                                         step=1,
                                         value=0,
                                         label='Seed 2')
                        with gr.Row():
                             swap_seed_button = gr.Button('Swap Seeds')
                             random_seeds_button = gr.Button('Pick Seeds For Me')
                        psi_style = gr.Slider(0,
                                        2,
                                        step=0.05,
                                        value=0.7,
                                        label='Truncation psi')  
                        style_interp = gr.Slider(0,
                                        2,
                                        step=0.05,
                                        value=1.0,
                                        label='Style transfer interpolation (0 = most like seed 2)')  
                                        
                        styleDrop = gr.Dropdown(
                                    choices=["coarse", "fine", "fine_average", "coarse_average", "total_average"], label="Method of Style Transfer", info="Select which type of style transfer you want!", value="coarse"
                                        ),                                        
                        style_run_button = gr.Button('Generate Style Mixing')
                    with gr.Column():
                        seed1im = gr.Image(label='Seed 1 Image', elem_id='seed1')
                        seed1txt = gr.Markdown(label='Seed 1', value="")
                        seed2im = gr.Image(label='Seed 2 Image', elem_id='seed2')
                        seed2txt = gr.Markdown(label='Seed 2', value="")
                        styleim = gr.Image(label='Style Mixed Image', elem_id='style')
        model_refresh_button.click(fn=update_model_drop,inputs=[],outputs=[modelDrop])
        simple_run_button.click(fn=model.set_model_and_generate_image,
                         inputs=[deviceDrop, modelDrop,seed,
                             psi, randomSeed], outputs=[result, outputSeed, seed])
        style_run_button.click(fn=model.set_model_and_generate_styles,
                         inputs=[deviceDrop, modelDrop,seed1, seed2, psi_style, styleDrop[0], style_interp], outputs=[seed1im, seed2im, styleim, seed1txt, seed2txt])
        swap_seed_button.click(fn=swap_slider, inputs=[seed1, seed2], outputs=[seed1,seed2])
        random_seeds_button.click(fn=random_seeds, inputs=[seed1,seed2], outputs=[seed1,seed2])
        send_to_style_button1.click(fn=send_style, inputs=[seed],outputs=[seed1])
        send_to_style_button2.click(fn=send_style, inputs=[seed],outputs=[seed2])
        return [(ui_component, "GAN Generator", "gan_generator_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)
