import os
from PIL import Image
chemin = os.path.join(os.path.dirname(__file__), "../resources/images")
if not os.path.exists(chemin):
    os.makedirs(chemin)
image = Image.open(chemin + "/icons.png")

#Tailles souhaitées
sizes = [(64, 64), (128, 128), (256, 256)]
try:
    for size in sizes:
        resize_image = image.resize(size)
        resize_image.save(chemin + "/icon_" + str(size[0]) + ".ico")
        print("Image enregistrés dans {chemin}".format(chemin=chemin))
except Exception as e:
    print(e)