# SocialMediaScraper

This is just a couple of scripts that can help scrap only the photos of friends and public pages on Instagram and Facebook. This would very helpful to play with using [DiffusionModels](https://bytexd.com/how-to-use-dreambooth-to-fine-tune-stable-diffusion-colab/). This is only for educational purposes. 

Please install the dependencies: `pip install -r requirements.txt`

Some examples on how to run these scripts:

``python facebook_scraper.py --fb-username=email_fb  --fb-profile-id=friend_id --op-folder=fb_profiles --fb-password=password``

``python instagram_scraper.py --insta-username=email_insta  --insta-profile-id=friend_id --op-folder=insta_profiles --insta-password=password``

Once done, you can use the [DreamBooth colab notebook](https://bytexd.com/how-to-use-dreambooth-to-fine-tune-stable-diffusion-colab/) to create beautiful images of your friends or your idols. Again, this is only for educational purposes and I hope no one will use it to harm anyone.
