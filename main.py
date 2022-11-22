import openai
import webbrowser
import requests
from PIL import Image
from datetime import datetime
# from config import API_Key, Org_ID, Number_of_Generations, Prompt, Array_of_Artists
from config import API_Key, Org_ID


openai.organization = Org_ID
openai.api_key = API_Key


num = 4
prompt="mushroom cave"
artist_arr = ['Frederic Edwin Church']

# num = Number_of_Generations
# prompt = Prompt
# artist_arr = Array_of_Artists

date = datetime.now()
yes = ['yes', 'y']
no = ['no', 'n']

for artist in artist_arr:
    current_prompt = f'{prompt} by {artist}'
    response = openai.Image.create(
        prompt=current_prompt,
        n=num,
        size="1024x1024"  # "512x512"
    )

    # variation
    # response = openai.Image.create_variation(
    #   image=open(f'photos/{photoVar}', "rb"),
    #   n=num,
    #   size="1024x1024"
    # )

    f = open("hist.txt", "a")
    # sf = open("saved_hist.txt", "a")

    for i in range(num):
        url = response['data'][i]['url']
        f.write(
            f'{i + 1} of {num}\n{current_prompt}\n{date.day} {date.hour}:{date.minute}\n{url}\n\n')
        webbrowser.open_new_tab(url)

        while True:
            save_image = input(f'\nSave {current_prompt} (yes/no): ')
            if save_image.lower() in yes:
                # sf.write(f'\n{date.day} {date.hour}:{date.minute} - {current_prompt} ({i + 1})\n')
                # shorten name
                # name = prompt.split()[:4]
                # name = '-'.join(name)
                # name = f'{name}{i + 1}.png'
                name = f'photos/{current_prompt} {i + 1}.png'
                img = Image.open(requests.get(url, stream=True).raw)

                # resize photo
                # width, height = 256, 256
                # image = img.resize((width, height))
                img.save(name)
                break
            elif save_image.lower() in no:
                break
            else:
                print('Please input yes or no')
                continue

    f.close()
    # sf.close()
