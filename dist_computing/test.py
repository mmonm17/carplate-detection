from PIL import Image
import numpy as np

each_img_dir = "C:\\Users\\Kyle Carlo C. Lasala\\Documents\\GitHub\\carplate-detection\\datasets\\test\\images\\0.jpg"

img = Image.open(each_img_dir)
img_arr = np.array(img)
# filename = each_img_dir.split("/")[-1]
# res = self.worker_proxies[i].receive_image(img_arr, filename)
# print(f"Worker {i+1}: {res}")
print(img_arr.tolist())